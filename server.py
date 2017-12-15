import socketserver


class MyTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("...Connecting from: ", self.client_address)
        while True:
            self.data = self.rfile.readline().strip()
            if not self.data:
                print("Close connection.")
                print("Waiting for new connection...")
                break
            print("{} wrote:".format(self.client_address[0]))
            print(self.data.decode("utf-8"))
            self.wfile.write(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = input("Enter address of server: IP Port\n").split(" ")
    print("Server start")
    print("Waiting for connection...")

    # Create the server, binding to localhost on port which user chooses
    with socketserver.TCPServer((HOST, int(PORT)), MyTCPHandler) as server:
        try:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutdown server.")
            server.shutdown()
