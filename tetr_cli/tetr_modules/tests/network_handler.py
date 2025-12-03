"""A simple P2P network handler using iroh."""

# coding: utf-8

from asyncio import (
    CancelledError,
    create_task,
    FIRST_COMPLETED,
    get_running_loop,
    sleep,
    Task,
    wait,
)
from json import dumps, loads
from random import randint
from struct import pack, unpack
from typing import Dict, Optional

from iroh import (
    Connection,
    Endpoint,
    Iroh,
    NodeOptions,
    NodeTicket,
    SendStream,
    RecvStream,
)
from iroh.iroh_ffi import uniffi_set_event_loop, IrohError


ALPN: bytes = b"tetr_cli/1"


async def send_data(send_stream: SendStream, data: Dict):
    """Send data over the send stream."""
    for key, value in data.items():
        print(f"[Sending] {key}: {value}")
    json_data: bytes = dumps(data).encode("utf-8")
    # Big-endian 4-byte
    length = pack(">I", len(json_data))
    await send_stream.write_all(length + json_data)


async def receive_data(receive_stream: RecvStream) -> Optional[Dict]:
    """Receive data from the receive stream."""

    try:
        length_bytes: bytes = await receive_stream.read_exact(4)
        if not length_bytes:
            return None

        length: int = unpack(">I", length_bytes)[0]
        json_data: bytes = await receive_stream.read_exact(length)
        if not json_data:
            return None

    except IrohError:
        return None

    return loads(json_data.decode("utf-8"))


async def send_loop(send_stream: SendStream, peer_name: str):
    """Continuously send data to the peer."""
    try:
        repeat: int = randint(5, 10)
        for _ in range(repeat):
            data: Dict = {
                "message": f"Hello from {peer_name}",
                "value": f"Lucky Number: {randint(1, 100)}",
            }
            await send_data(send_stream, data)
            await sleep(1)
    except Exception as e:
        raise Exception(f"Send error: {e}") from e
    finally:
        await send_stream.finish()
        await send_stream.stopped()


async def receive_loop(receive_stream: RecvStream, peer_name: str):
    """Continuously receive data from the peer."""
    try:
        while True:
            data: Optional[Dict] = await receive_data(receive_stream)
            if data is None:
                print(f"[{peer_name} disconnected]")
                break
            for key, value in data.items():
                print(f"[{peer_name} received] {key}: {value}")
    except Exception as e:
        raise Exception(f"Receive error: {e}") from e


async def handle_data(channel, peer_name: str):
    """Handle bidirectional data on the channel."""
    send_stream: SendStream = channel.send()
    receive_stream: RecvStream = channel.recv()

    send_task: Task = create_task(send_loop(send_stream, peer_name))
    receive_task: Task = create_task(receive_loop(receive_stream, peer_name))

    _, pending = await wait([send_task, receive_task], return_when=FIRST_COMPLETED)

    for task in pending:
        task.cancel()
        try:
            await task
        except CancelledError:
            pass


class DataSocket:
    """Handles actual bi-directional data communication."""

    def __init__(self) -> None:
        pass

    async def accept(self, connection: Connection) -> None:
        """Handle bi-directional communication on the channel."""
        print("Accepted connection.")
        channel = await connection.accept_bi()
        await handle_data(channel, "client")

    async def shutdown(self) -> None:
        return


class DataProtocol:
    """Handles data protocol for client connections."""

    """Mainly for to mass creation DataSocket instances."""

    def __init__(self):
        pass

    def create(self, endpoint: Endpoint) -> DataSocket:
        return DataSocket()


class HostHandler:
    """Handles host-side network operations."""

    def __init__(self):
        """This initializes the host handler."""
        pass

    async def run_host(self):
        """Run the host to accept client connections."""
        options = NodeOptions()
        options.protocols = {ALPN: DataProtocol()}

        node = await Iroh.memory_with_options(options)
        node_address = await node.net().node_addr()
        ticket = NodeTicket(node_address)
        print(f"You are a host, here is the ticket: {ticket}")

        try:
            while True:
                await sleep(1)
        except KeyboardInterrupt:
            await node.node().shutdown()


class ClientHandler:
    """Handles client-side network operations."""

    def __init__(self, ticket: str = ""):
        """This initializes the client handler with an optional ticket."""
        self.__ticket = ticket

    async def run_client(self):
        """Run the client to connect to a host."""
        options = NodeOptions()
        node = await Iroh.memory_with_options(options)

        try:
            node_address = NodeTicket.parse(self.__ticket).node_addr()
        except IrohError:
            print(f"{self.__ticket} is not a valid ticket!")
            return

        endpoint = node.node().endpoint()

        connection = await endpoint.connect(node_address, ALPN)

        channel = await connection.open_bi()
        await handle_data(channel, "host")

        await node.node().shutdown()


async def setup_network(ticket: str = ""):
    """This function sets up a simple P2P network using iroh."""
    uniffi_set_event_loop(get_running_loop())  # type: ignore[arg-type]

    if ticket:
        client: ClientHandler = ClientHandler(ticket)
        await client.run_client()
        return

    host: HostHandler = HostHandler()
    await host.run_host()


if __name__ == "__main__":
    print("This is a network handler module for P2P communication.")
