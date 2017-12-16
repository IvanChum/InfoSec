import socket
from kuznechik import kuznechik
import binascii
import time
from DFH import DiffieHellman


def Partition(lst,siz):
    """Разбиение списка на куски равной длины размером siz"""
    return [lst[i:i+siz] for i in range(0,len(lst),siz)]


if __name__ == "__main__":
    print("Start Client")
    # key = '8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef'
    Alice = DiffieHellman()
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
                        sock.send(Alice.publicKey.to_bytes(Alice.publicKey.bit_length(), byteorder="big"))
                        Bob_key = int.from_bytes(sock.recv(2048), byteorder="big")
                        Alice.genKey(Bob_key)
                        key = str(binascii.hexlify(Alice.getKey()), "utf-8")
                        data_str = input("Enter your message:\n")
                        if not data_str:
                            raise BrokenPipeError
                        big_text = Partition(data_str, 16)
                        sock.send(len(big_text).to_bytes(len(big_text).bit_length(), byteorder="big"))
                        for i in big_text:
                            data = bytes(i, "utf-8")
                            text = binascii.hexlify(data).zfill(32)
                            crypto_text = kuznechik(key).encrypt(text)
                            sock.send(crypto_text)
                        # Receive data from the server and shut down
                        data = sock.recv(2048)
                        size = int.from_bytes(data, byteorder="big")
                        text = ""
                        for i in range(size):
                            data = sock.recv(2048)
                            text_hex = kuznechik(key).decrypt(data)
                            text_str = str(binascii.unhexlify(text_hex), "utf-8")
                            text += text_str
                        print("Sent:     {}".format(data_str))
                        print("Received: {}".format(text))
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
