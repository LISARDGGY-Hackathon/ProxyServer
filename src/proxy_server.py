import socket
from threading import Thread
import time
import datetime

'''
A Simple Proxy Server to route requests to different model servers based on client input.
'''


vllm_gpt_oss_120b_1="http://210.61.209.139:45014/v1/"
vllm_gpt_oss_120b_2="http://210.61.209.139:45005/v1/"

model = vllm_gpt_oss_120b_1

PROXY_HOST = '0.0.0.0'
PROXY_PORT = 8888 

BUFFER_SIZE = 4096


def handle_client(client_socket, client_addr):
    try:
        while(True):
            data = client_socket.recv(BUFFER_SIZE)
            if(data == b"END"):
                break

            data = data.decode()
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{client_addr}] Received data:\n{data}")

            model_num = data.split(" ")[0]
            data = " ".join(data.split(" ")[1:])

            if(model_num == "1"):
                model = vllm_gpt_oss_120b_1
            elif(model_num == "2"):
                model = vllm_gpt_oss_120b_2
            else:
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{client_addr}] Unknown model number.")
                client_socket.send(b"Error: Unknown model number.")
                client_socket.send(b"END")
                continue
            
            
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{client_addr}] Using model: vllm_gpt_oss_120b_{model_num}...")
            client_socket.send(f"Using model: vllm_gpt_oss_120b_{model_num}...".encode())


            '''
            Here you can add code to forward the request to the selected model server
            and get the response back.
            Data to send to model server: data
            Model server URL: model
            '''

            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{client_addr}] Done. Sending response back to client.")

            client_socket.send(b"<The response from the model server>") # Placeholder for actual response

            time.sleep(0.1)
            client_socket.send(b"END")

    except Exception as e:
        print("Error handling client:", e)

    client_socket.close()
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{client_addr}] Connection closed.")


print("Starting proxy server...")
print(f"Proxy Server IP: {PROXY_HOST}:{PROXY_PORT}")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((PROXY_HOST, PROXY_PORT))
server.listen(10)

while(True):
    client_socket, addr = server.accept()

    addr = f"{addr[0]}:{addr[1]}"
    print("New connection:", addr)
    client_handler = Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()