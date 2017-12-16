import socket
from kuznechik import kuznechik
import binascii
import time
from DFH import DiffieHellman

if __name__ == "__main__":
    print("Start Client")
    key = '8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef'
    while True:
        while True:
            try:
                HOST, port = input("With who, you want to talk? IP Port\n").split(" ")
            except ValueError:
                print("Error! You should enter only IP and Port")
                continue
            except KeyboardInterrupt:
                print("Close Client.")
                exit(-1)
            try:
                if HOST.isdigit():
                    ip = int(HOST)
                else:
                    ip = HOST
                if not port.isdigit():
                    raise NameError
                break
            except NameError:
                    print("Wrong IP or Port.")
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                # Connect to server and send data
                sock.connect((ip, int(port)))
                while True:
                    try:
                        data_str = input("Enter your massage:\n")
                        if not data_str:
                            raise BrokenPipeError
                        data = bytes(data_str, "utf-8")
                        text = binascii.hexlify(data).zfill(32)
                        crypto_text = kuznechik(key).encrypt(text)
                        print(crypto_text)
                        sock.send(crypto_text)
                        # Receive data from the server and shut down
                        crypto_received = sock.recv(2048)
                        print(crypto_received)
                        received_byte = kuznechik(key).decrypt(crypto_received)
                        print(received_byte)
                        received_hex = binascii.unhexlify(received_byte)
                        print(received_hex)
                        received_str = str(received_hex, "utf-8")
                        print("Sent:     {}".format(data_str))
                        print("Received: {}".format(received_str))
                    except BrokenPipeError:
                        print("Close Client")
                        sock.close()
                        exit(0)
            except KeyboardInterrupt:
                print("Close Client")
                sock.close()
                break
            #except TypeError:
            #    print("Error with host address! You must enter correct host IP and Port.")
            except socket.gaierror:
                print("Error with host address! Nodename nor servname provided, or not known.")
            except ConnectionRefusedError:
                print("Connection refused.")
