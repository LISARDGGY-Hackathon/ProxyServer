# ProxyServer
This is a program that can use a computer as a proxy server to transfer data for LLM GPT OSS 120B.

## Usage

#### Server (proxy_server.py):
- Add code to forward the requests to the selected model server and get the response back. (line 50~ in proxy_server.py)
- Replace the placeholder with the LLM's response and send it back to the client. (line 59 in proxy_server.py)
- Setup port forwarding.
- Sharing your public IP with your partner.
- Run the program.


> variables:
>-  data: Data to send to model server
>-  model: Model server URL

---
#### client (client.py):
- Replace PROXY_HOST with the public IP of the server. 
- Wait for the server to be online.
- Run the program.

you can replace the following programs with your code.
```
model = input("Select model (1 or 2 or exit): ")
```
> model
>- **1** : vllm_gpt_oss_120b_1
>
>- **2** : vllm_gpt_oss_120b_2
>>
>- **exit** : Closed connection.
>>
>- else : Error


```
msg = input("input: ")
```
> **msg** is the message you want to send to the LLM.

other variable:

- **data** : The result of the LLM.