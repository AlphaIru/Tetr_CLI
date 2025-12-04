"""This will handle the client side of p2p networking."""

from asyncio import (
    CancelledError,
    create_task,
    run,
    get_running_loop,
    Queue,
)

from iroh import Iroh, NodeOptions, NodeTicket, IrohError
from iroh.iroh_ffi import uniffi_set_event_loop

from network_lib import ALPN, handle_data


async def async_input(prompt: str = "") -> str:
    """Non-blocking input using executor."""
    loop = get_running_loop()
    return await loop.run_in_executor(None, input, prompt)


async def run_client(ticket_str: str):
    """Run as client - connect to server."""
    uniffi_set_event_loop(get_running_loop())  # type: ignore

    options = NodeOptions()
    node = await Iroh.memory_with_options(options)

    try:
        node_addr = NodeTicket.parse(ticket_str).node_addr()
    except IrohError:
        print("Invalid ticket.")
        await node.node().shutdown()
        return

    endpoint = node.node().endpoint()

    print("[Connecting to server...]")
    try:
        connection = await endpoint.connect(node_addr, ALPN)
        channel = await connection.open_bi()

        send_queue: Queue = Queue()
        recv_queue: Queue = Queue()

        create_task(handle_data(channel, "host", send_queue, recv_queue))

        async def process_data():
            while True:
                msg = await recv_queue.get()
                if msg is None:
                    print("\n[Server disconnected]")
                    break
                print(f"\r[from server]: {msg}\n> ", end="", flush=True)
                recv_queue.task_done()

        recv_task = create_task(process_data())

        print("[Connected! Type data and press Enter. Type /quit to exit]")

        while True:
            try:
                text = await async_input("> ")
            except (EOFError, KeyboardInterrupt):
                print("\n[Closing connection...]")
                break

            if not text:
                continue

            if text.strip().lower() == "/quit":
                break

            await send_queue.put({"client": text})

        await send_queue.put(None)
        recv_task.cancel()
        try:
            await recv_task
        except CancelledError:
            pass
        except Exception:
            pass

    except Exception as e:
        print(f"[Error: {e}]")
    finally:
        await node.node().shutdown()


if __name__ == "__main__":
    ticket: str = input("Enter ticket: ")
    try:
        run(run_client(ticket))
    except KeyboardInterrupt:
        print("\n[Shutting down]")
