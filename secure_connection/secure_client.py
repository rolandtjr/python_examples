#!/usr/bin/env python3
"""secure_client.py
----------------
A module to establish a non-verifying SSL connection with a server and to 
send/receive messages through a secure socket.

Usage:
    Run the script to start a communication session with the server at 
    "127.0.0.1" on port 9001. Input messages in the console to send to 
    the server and receive replies. Type a message with the content 
    "quit" to close the connection.

Functions:
    main(server_address: str, server_port: int): Initiates a secure socket
    communication session with the specified server.
"""
from socket import create_connection, socket
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_NONE


def main(server_address: str, server_port: int):
    context = SSLContext(PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = CERT_NONE
    unsecure_socket: socket = create_connection((server_address, server_port))
    secure_socket = context.wrap_socket(
        unsecure_socket
    )  # , server_hostname="localhost")

    while True:
        message = input()
        secure_socket.send(message.encode("utf-8"))
        reply = secure_socket.recv(len(message))
        if reply == b"quit":
            break
        print(reply.decode("utf-8"))


if __name__ == "__main__":
    main("127.0.0.1", 9001)
