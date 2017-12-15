import socket


if __name__ == "__main__":
    print("Start Client")
    try:
        HOST, port = input("With who, you want to talk? IP Port\n").split(" ")
    except ValueError:
        print("You should enter ")
    if HOST.isdigit():
        ip = int(HOST)
    else:
        ip = HOST
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            # Connect to server and send data
            sock.connect((ip, int(port)))
            while True:
                try:
                    data = input("Enter your massage:\n")
                    sock.sendall(bytes(data + "\n", "utf-8"))

                    # Receive data from the server and shut down
                    received = str(sock.recv(1024), "utf-8")

                    print("Sent:     {}".format(data))
                    print("Received: {}".format(received))
                except BrokenPipeError:
                    print("Close Client")
                    sock.close()
        except KeyboardInterrupt:
            print("Close Client")
            sock.close()
        except TypeError:
            print("Error with host address! You must enter host IP and Port.")
