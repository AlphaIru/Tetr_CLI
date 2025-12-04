"""This module provides networking utilities for Tetr CLI using iroh library."""

# coding: utf-8

from asyncio import (
    CancelledError,
    create_task,
    FIRST_COMPLETED,
    Queue,
    wait,
)

from json import loads, dumps, JSONDecodeError
import struct
from typing import Dict, Optional

from iroh import (
    IrohError,
    SendStream,
    RecvStream,
)

ALPN = b"tetr_cli/1"
LENGTH_PREFIX_SIZE = 4


async def send_message(send_stream, payload: Dict):
    """Send a length-prefixed message."""
    data: bytes = dumps(payload).encode("utf-8")
    length: bytes = struct.pack(">I", len(data))  # 4-byte big-endian length
    try:
        await send_stream.write_all(length + data)
    except IrohError:
        pass


async def recv_message(recv_stream) -> Optional[Dict]:
    """Receive a length-prefixed message."""
    try:
        length_bytes: bytes = await recv_stream.read_exact(LENGTH_PREFIX_SIZE)
        if not length_bytes:
            return None

        length = struct.unpack(">I", bytes(length_bytes))[0]

        if length > 100000:
            # print("[recv error: message too long]")
            return None

        data: bytes = await recv_stream.read_exact(length)
        if not data:
            return None
        return loads(bytes(data).decode("utf-8"))
    except JSONDecodeError:
        return None
    except IrohError:
        return None
    except Exception:
        # print(f"[recv error: {e}]")
        return None


async def send_loop(send_stream, peer_name: str, send_queue: Optional[Queue] = None):
    """Loop to send user input as messages."""
    try:
        if send_queue:
            while True:
                payload = await send_queue.get()
                if payload is None:
                    break
                # print(f"[sending]: {payload}")
                await send_message(send_stream, payload)
                send_queue.task_done()
    except IrohError:
        pass
    except Exception:
        pass
    finally:
        try:
            await send_stream.finish()
            await send_stream.stopped()
        except Exception:
            pass


async def recv_loop(recv_stream, peer_name: str, recv_queue: Optional[Queue] = None):
    """Loop to receive and display messages."""
    try:
        while True:
            msg = await recv_message(recv_stream)
            if msg is None:
                # print(f"[{peer_name} disconnected]")
                break
            if recv_queue:
                await recv_queue.put(msg)
    except Exception:
        pass
        # print(f"[recv error: {e}]")


async def handle_data(
    channel,
    peer_name: str,
    send_queue: Optional[Queue] = None,
    recv_queue: Optional[Queue] = None,
):
    """Handle bidirectional data on a channel."""
    send_stream: SendStream = channel.send()
    recv_stream: RecvStream = channel.recv()

    send_task = create_task(send_loop(send_stream, peer_name, send_queue))
    recv_task = create_task(recv_loop(recv_stream, peer_name, recv_queue))

    _, pending = await wait([send_task, recv_task], return_when=FIRST_COMPLETED)

    for task in pending:
        task.cancel()
        try:
            await task
        except CancelledError:
            pass


if __name__ == "__main__":
    print("This is a module, please run the network_client.py or network_server.py.")
