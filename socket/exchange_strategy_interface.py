from abc import ABC, abstractmethod


class ExchangeStrategyInterface(ABC):
    """
    ExchangeStrategyInterface is an interface for applying any exchange specific methods to `SocketWrapper`.
    Mainly, upon starting the connection, and handling messages. The most common difference between different
    exchange clients is how Heartbeats are managed for long term connections.

    For example, Deribit has a specific message that must be sent to the client to keep the connection alive.
    Then, you must also respond to the clients heart beat message.
    """
    @abstractmethod
    async def start(self, manager) -> None:
        """
        Add any exchange specific tasks to the start method in `SocketWrapper`.

        :param manager: (Exchange)SocketManager class. e.g. `DeribitSocketManager`
        :return: None.
        """
        pass

    @abstractmethod
    async def handle_message(self, manager, message) -> None:
        """
        Add any exchange specific message handling to the handle_message method in `SocketWrapper`.

        :param manager: (Exchange)SocketManager class. e.g. `DeribitSocketManager`.
        :param message: The websocket message.
        :return: None.
        """
        pass
