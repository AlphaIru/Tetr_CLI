"""This will handle network host side of p2p networking."""

from asyncio import (
    CancelledError,
    gather,
    run,
    get_running_loop,
    Queue,
    create_task,
    wait_for,
)
from typing import Dict, Optional

from iroh import (
    Connection,
    Iroh,
    NodeAddr,
    NodeOptions,
    NodeTicket,
)
from iroh.iroh_ffi import uniffi_set_event_loop

from tetr_cli.tetr_modules.modules.network_lib import ALPN, handle_data
from tetr_cli.tetr_modules.modules.database import set_temp


async def run_host(
    game_state_send_queue: Optional[Queue] = None,
    game_state_recv_queue: Optional[Queue] = None,
):
    """Run as host - wait for incoming connections."""

    recv_queue: Queue[Optional[Dict]] = Queue()  # type: ignore
    send_queue: Queue[Optional[Dict]] = Queue()  # type: ignore

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

    uniffi_set_event_loop(get_running_loop())  # type: ignore

    options = NodeOptions()
    options.protocols = {ALPN: dataProtocol()}

    node = await Iroh.memory_with_options(options)
    node_addr: NodeAddr = await node.net().node_addr()  # type: ignore
    ticket = NodeTicket(node_addr)
    set_temp("ticket", str(ticket))

    # print("Host started. Share this ticket with the client:")
    # print(f"{ticket}")
    # print("\nWaiting for connection...")

    async def send_game_state():
        """Send game state updates."""
        if game_state_send_queue is None:
            return
        while True:
            send_payload = await game_state_send_queue.get()
            if send_payload is None or (
                isinstance(send_payload, dict) and send_payload.get("quit")
            ):
                break
            await send_queue.put(send_payload)
            game_state_send_queue.task_done()

    async def recv_game_state():
        """Receive game state updates."""
        if game_state_recv_queue is None:
            return
        while True:
            recv_payload = await recv_queue.get()
            if recv_payload is None:
                break
            await game_state_recv_queue.put(recv_payload)
            recv_queue.task_done()

    send_task = create_task(send_game_state())
    recv_task = create_task(recv_game_state())

    try:
        await wait_for(gather(send_task, recv_task), timeout=2.0)
    except KeyboardInterrupt:
        pass
        # print("\n[Shutting down]")
    finally:
        await send_queue.put(None)
        await recv_queue.put(None)
        send_task.cancel()
        recv_task.cancel()
        try:
            await send_task
            await recv_task
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
