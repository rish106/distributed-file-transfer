import socket
import time
import threading
import queue

lines = {}
client1 = socket.socket()
client_rcving_2 = socket.socket()
client_sending_2 = socket.socket()
client_rcving_3 = socket.socket()
client_sending_3 = socket.socket()
client_rcving_4 = socket.socket()
client_sending_4 = socket.socket()

port2_rcving = 10010
port3_rcving = 10011
port4_rcving = 10012
# port2_sending = 10011
host_rcving_2=""
host_rcving_3=""
host_rcving_4=""
# host_sending_2=""
client_rcving_2.bind((host_rcving_2,port2_rcving))
client_rcving_3.bind((host_rcving_3,port3_rcving))
client_rcving_4.bind((host_rcving_4,port4_rcving))
# client_sending_2.bind((host_sending_2,port2_sending))
client_rcving_2.listen(5)
client_rcving_3.listen(5)
client_rcving_4.listen(5)
sending_queue = queue.Queue()



receving_end_clients = [client_rcving_2,client_rcving_3,client_rcving_4]
sending_end_clients = [client_sending_2,client_rcving_3,client_rcving_4]


# client3 = socket.socket()
# client4 = socket.socket()








def parse_command(command: str):
    if command == "":
        return [""]
    tokens = command.split(" ")
    return tokens


def receive_response():
    data = client1.recv(4096)
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
    # try:
    sending_queue.put(response)
    # except:
    #     print("Data sending to other client failed")

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
        client1.connect((ip_address, port))
        print("Connected to server", ip_address)
    except:
        print("Error connecting to", ip_address)


def connect_to_client(cmd_arg: str,my_socket):
    if len(cmd_arg) == 0:
        print("Enter the IP Address and Port of the server")
        return
    tokens = cmd_arg.split(":")
    if len(tokens) != 2:
        print("Invalid format, please write 'CONNECTSERVER {IP_ADDRESS}:{HOST}'")
        return
    ip_address = tokens[0]
    port = int(tokens[1])
    # client_socket = socket.socket()
    try:
        my_socket.connect((ip_address, port))
        # sending_end_clients.append(my)
        print("Connected to client", ip_address)
    except:
        print("Error connecting to client", ip_address)


def start_command():
    client1.connect(("192.168.154.75", 9994))
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
            total = 0
            while len(lines) < 1000:
                client1.send(str.encode("SENDLINE"))
                curr = time.time()
                
                if (curr - start >= 5):
                    total+=5
                    print(len(lines)," ",total)
                    start = curr
                try:
                    response_str = receive_response()
                    handle_response(response_str)
                except:
                    pass
            print(len(lines)," ",total+5)

        elif cmd_tokens[0] == "SENDLINE" and len(cmd_tokens) == 1:
            client1.send(str.encode(cmd))
            response_str = receive_response()
            handle_response(response_str)
        elif cmd_tokens[0] == "CONNECTSERVER":
            connect_to_server(cmd_tokens[1])
        elif cmd_tokens[0] == "CONNECTCLIENT":
            connect_to_client(cmd_tokens[1])
        elif cmd_tokens[0] == "SUBMIT":
            client1.send(str.encode(cmd))
            print("Submitted")
        elif cmd_tokens[0] == "unique_elm":
            print(len(lines))

        elif cmd_tokens[0]=="ejaculate":
            lines.clear()
        else:
            print("Invalid Command")



# def conn(l):
#     for i in l:
#         i.listen()


# listen_clients = [client_rcving_2]
# conn(listen_clients)


def worker_function(i):

    conn,addr = receving_end_clients[i].accept()
    # inp = addr[0] + ":" + str(10008)
    sending_end_clients[i].connect((addr[0],10000+i))
    print("Client to Client connection established","| IP " , addr[0])
    while True :
        response = str(conn.recv(4096),"utf-8")
        tokens = response.splitlines()
        if len(tokens) < 2:
            continue
        for j in range(0, len(tokens), 2):
            line_number = int(tokens[j])
            content = tokens[j+1]
            if line_number in lines:
                continue
            lines[line_number]=content

        # print(len(lines),"\n")

def sending_function():
    while True:
        if(not sending_queue.empty()):
            data = sending_queue.get()
            for clients in sending_end_clients:
                clients.send(str.encode(data))

thread0_rcv = threading.Thread(target=worker_function, args=(0,))
thread0_rcv.daemon=True
thread0_rcv.start()

thread1_rcv = threading.Thread(target=worker_function, args=(1,))
thread1_rcv.daemon=True
thread1_rcv.start()

thread2_rcv = threading.Thread(target=worker_function, args=(2,))
thread2_rcv.daemon=True
thread2_rcv.start()



thread1_send = threading.Thread(target = sending_function)
thread1_send.daemon=True
thread1_send.start()




# thread2 = threading.Thread(target=worker_function, args=(client3))
# thread3 = threading.Thread(target=worker_function, args=(client4))


start_command()
