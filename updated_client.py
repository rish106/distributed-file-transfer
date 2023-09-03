import socket
import time
import threading
from queue import Queue

lines = {}

MAX_LINES = 1000

clients_info = ["192.168.105.79:10000"]
# clients_info = []
OTHER_CLIENTS = len(clients_info)

connected_clients = 0

ENTRY_NUMBER = "2021CS10581"
TEAM_NAME = "slowbrains"

server_conn = socket.socket()

# sockets from which unique lines are sent to other clients
sending_client_sockets = []

# socket from which unique lines are received from other clients
receiving_client_sockets = []

# threads receiving and processing the lines from other clients
receiving_threads = []

print("Created receiving sockets at ports:")
for i in range(OTHER_CLIENTS):
    client_socket=socket.socket()
    
    host = ""
    port = 10000 + i
    print(port, end = "")
    if i == OTHER_CLIENTS - 1:
        print()
    else:
        print(" ", end = "")
    client_socket.bind((host, port))
    client_socket.listen(5)
    receiving_client_sockets.append(client_socket)

sending_data = Queue()


def worker_function(i):
    conn, address = receiving_client_sockets[i].accept()
    print(f"Connection established with IP {address[0]}")
    line_number = 0
    content = ""
    reading_content = False
    while True:
        data = conn.recv(4096)
        response = data.decode("utf-8")
        for i in range(len(response)):
            if response[i] == '\n':
                if reading_content:
                    lines[line_number] = content
                    line_number = 0
                    content = ""
                reading_content = not reading_content
            elif not reading_content:
                line_number = 10 * line_number + (ord(response[i]) - '0')
            else:
                content += response[i]


def sending_function():
    while True:
        if not sending_data.empty():
            data = sending_data.get()
            for client in sending_client_sockets:
                client.send(str.encode(data))


def receive_response():
    data = server_conn.recv(4096)
    response = data.decode("utf-8")
    if len(response) == 0:
        return receive_response()
    else:
        return response


def connect_to_server(cmd_arg):
    if len(cmd_arg) == 0:
        print("Enter the IP Address and Port of the server")
        return
    tokens = cmd_arg.split(":")
    if len(tokens) != 2:
        print("Invalid format, type 'CONNECTSERVER {IP_ADDRESS}:{HOST}'")
        return
    ip_address = tokens[0]
    port = int(tokens[1])
    try:
        server_conn.connect((ip_address, port))
        print("Connected to server", ip_address)
    except:
        print("Error connecting to", ip_address)


def connect_to_client(cmd_arg):
    if len(cmd_arg) == 0:
        print("Enter the IP Address and Port of the client")
        return
    tokens = cmd_arg.split(":")
    if len(tokens) != 2:
        print("Invalid format, type 'CONNECTCLIENT {IP_ADDRESS}:{HOST}'")
        return
    ip_address = tokens[0]
    port = int(tokens[1])
    try:
        global connected_clients
        receiving_threads.append(threading.Thread(target = worker_function, daemon = True, args = (connected_clients,)))
        receiving_threads[connected_clients].start()
        sending_client_sockets.append(socket.socket())
        sending_client_sockets[connected_clients].connect((ip_address, port))
        connected_clients += 1
        print("Connected to client", ip_address)
    except:
        print("Error connecting to client", ip_address)


def infinite_requests():
    actual_start = time.time()
    start = time.time()
    total_time = 0
    total_requests = 0
    line_number = 0
    content = ""
    reading_content = False
    completed_line = False
    def receive_line():
        nonlocal content, line_number, reading_content, total_requests, completed_line
        response = receive_response()
        for i in range(len(response)):
            if response[i] == '\n':
                if reading_content:
                    if line_number not in lines and line_number >= 0 and line_number < MAX_LINES:
                        lines[line_number] = content
                        for client in sending_client_sockets:
                            client.send(str.encode(str(line_number)+"\n"+content+"\n"))
                    line_number = 0
                    content = ""
                    completed_line = True
                reading_content = not reading_content
            elif not reading_content:
                line_number = 10 * line_number + (ord(response[i]) - ord('0'))
            else:
                content += response[i]
    while len(lines) < MAX_LINES:
        server_conn.send(str.encode("SENDLINE\n"))
        total_requests += 1
        curr = time.time()
        if (curr - start >= 5):
            start = curr
            total_time += 5
            print(len(lines), total_time)
        completed_line = False
        while not completed_line:
            receive_line()
    else:
        print(f"Completed in {time.time() - actual_start} seconds with {total_requests} requests from this client")
        submit_lines()


def submit_lines():
    submit_data = "SUBMIT\n" + ENTRY_NUMBER + "@" + TEAM_NAME + "\n"
    submit_data += str(len(lines)) + "\n"
    line_list = []
    for i in lines:
        line_list.append((i, lines[i]))
    line_list.sort()
    for i in line_list:
        submit_data += str(i[0]) + "\n" + i[1] + "\n"
    server_conn.send(str.encode(submit_data))
    response = receive_response()
    print(response, end = "")


def reset_session():
    server_conn.send(str.encode("SESSION RESET\n"))
    response = receive_response()
    print(response, end = "")


def get_incorrect_lines():
    server_conn.send(str.encode("SEND INCORRECT LINES\n"))
    response = receive_response()
    print(response, end = "")


def get_argument(cmd):
    tokens = cmd.split(' ')
    if len(tokens) < 2:
        return ""
    else:
        return tokens[1]


def handle_command(cmd):
    if cmd == "":
        print("Please enter a command")
    elif cmd == "EXIT":
        print("Closed connection")
        return False
    elif cmd == "START":
        infinite_requests()
    elif cmd.startswith("SERVER"):
        address_port = get_argument(cmd)
        connect_to_server(address_port)
    elif cmd.startswith("CLIENT"):
        address_port = get_argument(cmd)
        connect_to_client(address_port)
    elif cmd == "SUBMIT":
        submit_lines()
    elif cmd == "CLEAR":
        lines.clear()
        print("Cleared dictionary")
    elif cmd == "PRINT":
        print("Unique lines =", len(lines))
    elif cmd == "CO":
        for client in clients_info:
            connect_to_client(client)
    elif cmd == "INCORRECT":
        get_incorrect_lines()
    elif cmd == "RESET":
        reset_session()
    else:
        print("Invalid Command")
    return True


def start_command():
    connect_to_server("10.17.6.5:9801")
    try:
        while True:
            cmd = input()
            if not handle_command(cmd.strip().upper()):
                break
    except KeyboardInterrupt:
        print("\nConnection closed by user")
    finally:
        server_conn.close()
        for sock in sending_client_sockets:
            sock.close()
        for sock in receiving_client_sockets:
            sock.close()
        print("Closed all sockets")


# sending_thread = threading.Thread(target = sending_function, daemon = True)
# sending_thread.start()


start_command()
