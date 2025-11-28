import socket

'''
Client for connecting to the proxy server and sending requests to selected models.
'''

PROXY_HOST = 'PUBLIC_IP' # Replace with actual public IP
PROXY_PORT = 8888

BUFFER_SIZE = 4096

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("connecting to proxy server...")
client.connect((PROXY_HOST, PROXY_PORT))
print("successfully connected to proxy server.")

while(True):
    model = input("Select model (1 or 2 or exit): ")

    if(model == "exit"):
        break
    if(model not in ["1", "2"]):
        print("Invalid model number. Please enter 1 or 2.\n")
        continue

    msg = input("input: ")

    client.send(f"{model} {msg}".encode())

    while(True):
        data = client.recv(BUFFER_SIZE)
        if(data == b"END"):
            break

        data = data.decode()
        print(data)

    print()
client.send(b"END")
print("Connection closed.")