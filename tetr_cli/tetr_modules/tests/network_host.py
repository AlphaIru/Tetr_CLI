"""This will handle network host side of p2p networking."""

from asyncio import (
    CancelledError,
    run,
    get_running_loop,
    Queue,
    create_task,
)

from iroh import (
    Connection,
    Iroh,
    NodeAddr,
    NodeOptions,
    NodeTicket,
)
from iroh.iroh_ffi import uniffi_set_event_loop

from network_lib import ALPN, handle_data


async def run_host():
    """Run as host - wait for incoming connections."""

    recv_queue = Queue()
    send_queue = Queue()

    class dataSocket:
        """Handler for incoming data connections (host-side)."""

        async def accept(self, conn: Connection):
            print("[Client connected]")
            channel = await conn.accept_bi()
            await handle_data(channel, "client", send_queue, recv_queue)

        async def shutdown(self):
            pass

    class dataProtocol:
        def create(self, endpoint):
            return dataSocket()

    uniffi_set_event_loop(get_running_loop())

    options = NodeOptions()
    options.protocols = {ALPN: dataProtocol()}

    node = await Iroh.memory_with_options(options)
    node_addr: NodeAddr = await node.net().node_addr()  # type: ignore
    ticket = NodeTicket(node_addr)

    print("Host started. Share this ticket with the client:")
    print(f"{ticket}")
    print("\nWaiting for connection...")

    async def async_input(prompt: str = "") -> str:
        """Non-blocking input using executor."""
        loop = get_running_loop()
        return await loop.run_in_executor(None, input, prompt)

    async def process_data():
        while True:
            msg = await recv_queue.get()
            if msg is None:
                print("\n[Client disconnected]")
                break
            print(
                f"\r[from client]: {msg}\n> ", end="", flush=True
            )
            recv_queue.task_done()

    async def send_data():
        print("[Type messages. /quit to exit]")
        while True:
            text = await async_input("> ")  # CHANGED: use async_input
            if text.strip() == "/quit":
                break
            if not text:  # ADD: skip empty
                continue
            await send_queue.put({"host": text})

    recv_task = create_task(process_data())
    send_task = create_task(send_data())

    try:
        await send_task
    except KeyboardInterrupt:
        print("\n[Shutting down]")
    finally:
        await send_queue.put(None)
        recv_task.cancel()
        send_task.cancel()
        try:
            await recv_task
            await send_task
        except CancelledError:
            pass
        except Exception:
            pass
        await node.node().shutdown()


if __name__ == "__main__":
    try:
        run(run_host())
    except KeyboardInterrupt:
        print("\n[Interrupted]")
