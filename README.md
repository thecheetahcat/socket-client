# Socket Client Package

---

## Description:
The **socket_client package** is a Websocket Client Manager built for maintaining long-standing connections for handling streams and messages.
Specifically, for centralized cryptocurrency exchanges, but it can likely be used for most use cases. It provides a base `SocketWrapper` class 
that can be used for most exchanges, along with an `ExchangeStrategyInterface`, which can be used to add exchange-specific tasks such as heartbeat management.

---

## Installation

### Requirements
- Python 3.8+
- `websockets` (standard Python library)
- `logging_notifications` (custom logger built by myself)

You can install the required dependencies via `pip`:
```bash
pip install -r requirements.txt
```

---

## Usage

Implementing `SocketWrapper` without an `ExchangeStrategy` or callback methods:

```python
from websocket.socket_wrapper import SocketWrapper
import asyncio


async def main():
    socket_client = SocketWrapper("<websocket_url>")
    await socket_client.start()
    socket_task = asyncio.create_task(socket_client.run())

    # make any api requests or stream requests here
    # for example: await socket_client.send_message(your_request)

    await asyncio.sleep(60)  # keep the connection alive for 60 seconds
    await socket_client.stop_stream(socket_task)  # safely close the connection 


asyncio.run(main())
```

Adding an ExchangeStrategy (Deribit):

```python
from websocket.exchange_strategy_interface import ExchangeStrategyInterface
from websocket.socket_wrapper import SocketWrapper

# deribit has a specific heartbeat message and response
HB_MSG = {"jsonrpc": "2.0", "id": 0000, "method": "public/set_heartbeat", "params": {"interval": 30}}
HB_RESPONSE = {"jsonrpc": "2.0", "id": 0000, "method": "public/test"}


class DeribitExchangeStrategy(ExchangeStrategyInterface):
    # this will add a method to the start method in SocketWrapper
    async def start(self, manager) -> None:
        await manager.send_message(HB_MSG)  # send the heartbeat message as per deribit docs

    # this will add a method to the handle_message method in SocketWrapper
    async def handle_message(self, manager, message) -> None:
        if "method" in message and message['method'] == "heartbeat":
            if message['params']['type'] == "test_request":
                await manager.send_message(HB_RESPONSE)  # respond to the heartbeat as per deribit docs


class DeribitSocketManager(SocketWrapper):
    def __init__(self, strategy: DeribitExchangeStrategy):
        super().__init__("wss://www.deribit.com/ws/api/v2", strategy=strategy)
```

Adding callback methods for receiving messages and reconnecting:

```python
from websocket.socket_wrapper import SocketWrapper


# you can either add them on instantiation:
def default_callback(obj):
    print(obj)


def default_reconnect_callback():
    print("Reconnected!")


instantiated_callback_client = SocketWrapper("<websocket_url>", callback=default_callback, reconnect_callback=default_reconnect_callback)

# or you can add them after instantiation:
socket_client = SocketWrapper("<websocket_url>")

socket_client.add_callback_method(default_callback)
socket_client.add_reconnect_callback_method(default_reconnect_callback)
```

---

#### License
This package is licensed under the MIT License. See the LICENSE file for details.

----
### Updated local commit author to cheetah cat...