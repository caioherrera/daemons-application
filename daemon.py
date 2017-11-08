#!/usr/bin/env python
from socket import *
import sys

#verifica se os argumentos foram passados corretamente
if len(sys.argv) != 3 or sys.argv[1] != "--port":
	print("Uso: python daemon.py --port PORT")
else:
	port = int(sys.argv[2])
	print("Porta selecionada: " + str(port))

	#cria o socket servidor que vai receber os pacotes
	#sera utilizado o protocolo TCP na camada de transporte
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.bind(("", port))
	
	#socket aceita apenas uma conexao simultanea
	serverSocket.listen(1)
	print("Daemon escutando...")

	while(True):
		connectionSocket, address = serverSocket.accept()
		
		#recebe e decodifica o pacote
		package = connectionSocket.recv(2048).decode()

		#exibe o conteudo recebido e encerra a conexao
		print("Pacote recebido: " + package)
		connectionSocket.close()
		
	
