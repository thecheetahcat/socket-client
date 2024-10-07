# 'logs' module is provided by the 'logging_notifications' package
from logs.logger_helper import LoggerHelper
import asyncio
import websockets
from abc import ABC, abstractmethod
from typing import Optional, Callable


def default_callback(obj):
    print(obj)


def default_reconnect_callback():
    print("Reconnected!")


class SocketInterface(ABC):
    """
    SocketInterface is an abstract base class that defines a common interface for managing Websocket connections.

    This interface is designed for maintaining longstanding connections and ensuring efficiency and speed for streams and requests.

    Attributes:
        ws_url (str): Websocket URL.
        run_time (int): Run time in seconds.
        callback (Callable): Callback function for when a message is received.
        reconnect_callback (Callable): Callback function for when reconnection is triggered.
    """
    def __init__(
            self,
            ws_url: str,
            run_time: int,
            callback: Optional[Callable] = None,
            reconnect_callback: Optional[Callable] = None
    ):
        """
        Initializes the Websocket with the URL, and call back methods for receiving messages, and reconnections.

        Sets up instance variables for the websocket, a task to listen for messages, and an asynchronous lock for safe reconnections.
        """
        self.logger = LoggerHelper(__file__)
        self.ws_url = ws_url
        self.run_time = run_time
        self.callback = callback if callback else default_callback
        self.reconnect_callback = reconnect_callback if reconnect_callback else default_reconnect_callback
        self.websocket = None
        self.listener_task = None
        self.reconnect_lock = asyncio.Lock()
        self.timer = 0
        self.run_flag = False

    @abstractmethod
    async def run(self) -> None:
        """
        Creates an event loop to maintain a persistent connection with while automating the process
        of disconnecting and reconnecting based on a given run_time.

        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    async def handle_expired_run_time(self) -> None:
        """
        Handles reconnection after run_time expires.

        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        """
        Starts the Websocket connection.
        This is where you call the connect method, set the listener task, and any other necessary tasks such as a heart beat task.

        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    async def connect(self, retry_sleep: int, backoff: int) -> websockets.WebSocketClientProtocol:
        """
        Connect to the websocket and return the WebSocketClientProtocol.
        Implement a simple backoff mechanism using the retry_sleep and backoff parameters for any failed connections.

        :param retry_sleep: Retry sleep time in seconds.
        :param backoff: Exponential backoff factor.
        :return: WebSocketClientProtocol.
        """
        raise NotImplementedError

    @abstractmethod
    async def listen(self) -> None:
        """
        Listen on the websocket for incoming messages.
        Implement the handle_message method here for calling the callback method.

        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    async def handle_message(self, message) -> None:
        """
        Utilize the callback method to handle incoming json data.

        :param message: Json data.
        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    async def send_message(self, message) -> None:
        """
        Send a message to the websocket.

        :param message: The message to send.
        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    async def reconnect(self) -> None:
        """
        Manually disconnect, and reconnect to the websocket. Use the disconnect method to disconnect the websocket.

        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from the websocket.

        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    def add_callback_method(self, callback: Callable) -> None:
        """
        Update the callback method after instantiation.

        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    def add_reconnect_callback_method(self, reconnect_callback: Callable) -> None:
        """
        Update the reconnect_callback method after instantiation.

        :return: None.
        """
        raise NotImplementedError

    @abstractmethod
    async def stop_stream(self, task: asyncio.Task) -> None:
        """
        Flags the run_flag to trigger a disconnection and awaits the websocket connection task.

        :param task: Websocket connection task.
        :return: None.
        """
        raise NotImplementedError
