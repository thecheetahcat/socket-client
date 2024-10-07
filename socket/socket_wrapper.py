from socket_interface import SocketInterface
from exchange_strategy_interface import ExchangeStrategyInterface
import asyncio
import websockets
import json
import inspect
from typing import Optional, Callable


class SocketWrapper(SocketInterface):
    def __init__(
            self,
            ws_url: str,
            run_time: int = 86400,
            callback: Optional[Callable] = None,
            reconnect_callback: Optional[Callable] = None,
            strategy: Optional[ExchangeStrategyInterface] = None,
    ):
        super().__init__(ws_url, run_time, callback, reconnect_callback)
        self.wrapper_logger = self.logger.get_logger(__name__)
        self.strategy = strategy

    async def run(self) -> None:
        while self.run_flag:
            await asyncio.sleep(1)
            self.timer += 1

            if self.timer > self.run_time:  # sleep for n(time) before manually disconnecting and reconnecting
                await self.handle_expired_run_time()

        await self.disconnect()  # disconnect once we exit the loop

    async def handle_expired_run_time(self) -> None:
        await self.reconnect()
        self.wrapper_logger.info(f"Manual reconnect called after {self.run_time}s. Actual timer: {self.timer}")
        self.timer = 0
        self.wrapper_logger.info(f"Timer reset: {self.timer}")

    async def start(self) -> None:
        self.run_flag = True
        self.websocket = await self.connect()
        self.listener_task = asyncio.create_task(self.listen())
        if self.strategy:
            await self.strategy.start(self)

    async def connect(self, retry_sleep: int = 1, backoff: int = 1) -> websockets.WebSocketClientProtocol:
        while True:
            try:
                return await websockets.connect(str(self.ws_url))
            except Exception as Error:
                self.wrapper_logger.error(f"Connection failed: {Error}, retrying in {backoff} seconds...")
                await asyncio.sleep(retry_sleep * backoff)
                backoff *= 2  # simple exponential backoff

    async def listen(self) -> None:
        if self.websocket and self.websocket.open:
            try:
                async for message in self.websocket:
                    await self.handle_message(json.loads(message))
            except Exception as Error:
                self.wrapper_logger.error(f"Error in listen: {Error}")
                await self.reconnect()

    async def handle_message(self, message) -> None:
        if self.strategy:
            await self.strategy.handle_message(self, message)
        await self.callback(message) if inspect.iscoroutinefunction(self.callback) else self.callback(message)

    async def send_message(self, message) -> None:
        if self.websocket and self.websocket.open:
            await self.websocket.send(json.dumps(message))

    async def reconnect(self) -> None:
        self.wrapper_logger.info("Reconnect Called.")
        async with self.reconnect_lock:  # prevent concurrent reconnections
            await self.disconnect()
            await asyncio.sleep(1)  # rest for a moment before reconnecting
            await self.start()
            self.wrapper_logger.info("Reconnected to WebSocket.")
            if self.reconnect_callback:
                await self.reconnect_callback() if inspect.iscoroutinefunction(self.reconnect_callback) else self.reconnect_callback()

    async def disconnect(self) -> None:
        if self.listener_task:
            self.listener_task.cancel()
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        try:
            await self.listener_task
        except asyncio.CancelledError:
            self.wrapper_logger.info("Tasks cancelled.")
        self.wrapper_logger.info("Disconnected from Websocket.")

    def add_callback_method(self, callback: Callable) -> None:
        self.callback = callback

    def add_reconnect_callback_method(self, reconnect_callback: Callable) -> None:
        self.reconnect_callback = reconnect_callback

    async def stop_stream(self, task: asyncio.Task) -> None:
        self.run_flag = False
        if task:
            task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            self.wrapper_logger.info(f"Websocket stream task cancelled.")
        self.wrapper_logger.info(f"Successfully stopped stream. Run Flag: {self.run_flag}")
