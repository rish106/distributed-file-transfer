import socket
import time

lines = {}

other_clients = []

s = socket.socket()

def parse_command(command: str):
    if command == "":
        return [""]
    tokens = command.split(" ")
    return tokens


def receive_response():
    data = s.recv(4096)
    output_str = data.decode("utf-8")
    return output_str


def handle_response(response: str):
    if len(response) == 0:
        return
    tokens = response.splitlines()
    line_number = int(tokens[0])
    content = tokens[1]
    if line_number in lines:
        return
    lines[line_number] = content
    for client in other_clients:
        client.send(response)

def connect_to_server(cmd_arg: str):
    if len(cmd_arg) == 0:
        print("Enter the IP Address and Port of the server")
        return
    tokens = cmd_arg.split(":")
    if len(tokens) != 2:
        print("Invalid format, please write 'CONNECTSERVER {IP_ADDRESS}:{HOST}'")
        return
    ip_address = tokens[0]
    port = int(tokens[1])
    print(ip_address, port)
    try:
        s.connect((ip_address, port))
        print("Connected to server", ip_address)
    except:
        print("Error connecting to", ip_address)


def connect_to_client(cmd_arg: str):
    if len(cmd_arg) == 0:
        print("Enter the IP Address and Port of the server")
        return
    tokens = cmd_arg.split(":")
    if len(tokens) != 2:
        print("Invalid format, please write 'CONNECTSERVER {IP_ADDRESS}:{HOST}'")
        return
    ip_address = tokens[0]
    port = int(tokens[1])
    client_socket = socket.socket()
    try:
        client_socket.connect((ip_address, port))
        other_clients.append(client_socket)
        print("Connected to client", ip_address)
    except:
        print("Error connecting to client", ip_address)


def start_command():
    s.connect(("192.168.247.75", 9998))
    while True:
        cmd = input()
        cmd = cmd.strip()
        cmd_tokens = parse_command(cmd)
        if cmd_tokens[0] == "":
            print("Please enter a command")
        elif cmd_tokens[0] == "EXIT":
            print("Closed connection")
            break
        elif cmd_tokens[0] == "START":
            start = time.time()
            while len(lines) < 1000:
                s.send(str.encode("SENDLINE"))
                curr = time.time()
                if (curr - start >= 5):
                    start = curr
                    print(len(lines))
                try:
                    response_str = receive_response()
                    handle_response(response_str)
                except:
                    pass

        elif cmd_tokens[0] == "SENDLINE" and len(cmd_tokens) == 1:
            s.send(str.encode(cmd))
            response_str = receive_response()
            handle_response(response_str)
        elif cmd_tokens[0] == "CONNECTSERVER":
            connect_to_server(cmd_tokens[1])
        elif cmd_tokens[0] == "CONNECTCLIENT":
            connect_to_client(cmd_tokens[1])
        elif cmd_tokens[0] == "SUBMIT":
            s.send(str.encode(cmd))
            print("Submitted")
        else:
            print("Invalid Command")


start_command()
