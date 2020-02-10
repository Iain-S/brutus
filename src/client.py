#!/usr/bin/env python3
import sys
import socket as s

with s.socket(s.AF_UNIX, s.SOCK_STREAM) as sock_fd:
    print(sock_fd)
    sock_fd.connect(sys.argv[1]);
    msg = input("Please enter your message:")
    sock_fd.send(msg.encode('utf-8'))
    ret_msg = sock_fd.recv(4096)  # arbitrary but required buf size
    print(f"The return message was {ret_msg}")

