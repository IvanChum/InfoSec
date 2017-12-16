import socketserver
from kuznechik import kuznechik
import binascii
from DFH import DiffieHellman


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        key = '8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef'
        print("...Connecting from: ", self.client_address)
        while True:
            data = self.request.recv(2048)
            if not data:
                print("Close connection.")
                print("Waiting for new connection...")
                break
            text_hex = kuznechik(key).decrypt(data)
            text_str = str(binascii.unhexlify(text_hex), "utf-8")
            print("{} wrote:   {}".format(self.client_address[0], text_str))
            text_str = text_str.upper()
            print("Send to {}: {}".format(self.client_address[0], text_str))
            text_byte = bytes(text_str, "utf-8")
            print(text_byte)
            text_hex = binascii.hexlify(text_byte).zfill(32)
            print(text_hex)
            crypto_text = kuznechik(key).encrypt(text_hex)
            print(crypto_text)
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
