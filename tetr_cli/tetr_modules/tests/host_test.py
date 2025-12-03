"""This module contains tests for network handling using iroh P2P library."""
# coding: utf-8

from asyncio import run

from network_handler import setup_network


if __name__ == "__main__":
    print("Simulating host...")
    try:
        run(setup_network())
    except KeyboardInterrupt:
        print("Host simulation interrupted.")
