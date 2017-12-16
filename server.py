import socketserver
from kuznechik import kuznechik
import binascii
from DFH import DiffieHellman


def Partition(lst,siz):
    """Разбиение списка на куски равной длины размером siz"""
    return [lst[i:i+siz] for i in range(0,len(lst),siz)]


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        Bob = DiffieHellman()
        print("...Connecting from: ", self.client_address)
        while True:
            data = self.request.recv(2048)
            if not data:
                print("Close connection.")
                print("Waiting for new connection...")
                break
            Alice_key = int.from_bytes(data, byteorder="big")
            self.request.send(Bob.publicKey.to_bytes(Bob.publicKey.bit_length(), byteorder="big"))
            Bob.genKey(Alice_key)
            key = str(binascii.hexlify(Bob.getKey()), "utf-8")
            data = self.request.recv(2048)
            text = ""
            size = int.from_bytes(data, byteorder="big")
            for i in range(size):
                data = self.request.recv(2048)
                text_hex = kuznechik(key).decrypt(data)
                text_str = str(binascii.unhexlify(text_hex), "utf-8")
                text += text_str
            print("{} wrote:   {}".format(self.client_address[0], text))
            text = text.upper()
            print("Send to {}: {}".format(self.client_address[0], text))
            big_text = Partition(text, 16)
            self.request.send(len(big_text).to_bytes(len(big_text).bit_length(), byteorder="big"))
            for i in big_text:
                text_byte = bytes(i, "utf-8")
                text_hex = binascii.hexlify(text_byte).zfill(32)
                crypto_text = kuznechik(key).encrypt(text_hex)
                self.request.send(crypto_text)


if __name__ == "__main__":
    while True:
        try:
            HOST, port = input("Enter host address: IP Port\n").split(" ")
        except ValueError:
            print("Error! You should enter only IP and Port")
            continue
        except KeyboardInterrupt:
            print("Close Server.")
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
    print("Server start")
    print("Waiting for connection...")

    # Create the server, binding to localhost on port which user chooses
    with socketserver.TCPServer((ip, int(port)), MyTCPHandler) as server:
        try:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutdown server.")
            server.shutdown()
