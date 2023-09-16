#!/usr/bin/env python3
"""secure_server.py
----------------
This module facilitates creating an asynchronous SSL server that echoes
received messages. The server operates using SSL certificates stored in 
the "server_keys" directory.

Usage:
    Run the script to initiate the server on "localhost" at port 9001. 
    It listens for incoming connections and echoes messages unless "quit" 
    is received, which terminates the connection.

Functions:
    handle_client(reader: StreamReader, writer: StreamWriter) -> None:
        Handles the communication with a connected client asynchronously.
    
    main(address: str, port: int) -> None:
        Sets up and starts the SSL server with the necessary certificates.
"""
import logging
from asyncio import StreamReader, StreamWriter, run, start_server
from pathlib import Path
from ssl import Purpose, create_default_context


async def handle_client(reader: StreamReader, writer: StreamWriter):
    while True:
        msg_bytes = await reader.read(10)
        if msg_bytes == b"quit":
            writer.write(b"quit")
            await writer.drain()
            break
        writer.write(msg_bytes)
        await writer.drain()


async def main(address: str, port: int):
    storage_path: Path = Path("server_keys")

    keyfile = storage_path / "key.pem"
    certfile = storage_path / "cert.pem"
    context = create_default_context(Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile, keyfile)

    server = await start_server(handle_client, address, port, ssl=context)

    service_socket = server.sockets[0].getsockname()
    logging.info("Serving on %s", service_socket)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    run(main("localhost", 9001))
