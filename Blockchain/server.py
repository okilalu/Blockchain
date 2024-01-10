import socket

server_ip = "192.168.88.1"
server_port = 4000

addr = (server_ip, server_port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(addr)
server_socket.listen(5)
print(f"Server mendengarkan di {addr}")


def handle_recv_data():
    response = 'Node received the data'
    client_socket.send(response.encode())
    client_socket.close()


while True:
    client_socket, client_address = server_socket.accept()
    print("Menerima koneksi dari", client_address)

    data = client_socket.recv(1024).decode()
    print("Menerima data:", data)

    handle_recv_data()