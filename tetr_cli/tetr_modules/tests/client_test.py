"""This module contains tests for network handling using iroh P2P library."""
# coding: utf-8

from asyncio import run

from network_handler import setup_network

if __name__ == "__main__":
    print("Simulating client...")
    input_ticket = input("Enter the ticket provided by the host: ")
    try:
        run(setup_network(input_ticket))
    except KeyboardInterrupt:
        print("Client simulation interrupted.")
