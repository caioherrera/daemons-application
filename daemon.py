#!/usr/bin/env python
from socket import *
import sys
import subprocess
import threading

#definicao de uma classe filha de threading.Thread
#para a utilizacao de paralelismo
class CommandExecution(threading.Thread):
	
	#construtor que recebe o socket relativo a thread
	def __init__(self, socket):
		threading.Thread.__init__(self, group=None)
		self.socket = socket

	#funcao de execucao da thread
	def run(self):
		
		#recebe e decodifica o pacote
		package = self.socket.recv(2048).decode()
		print("Pacote recebido: " + package)

		#verifica se e seguro executar o comando
		output = ""
		dangerous = set(";>|")
		if any((c in dangerous) for c in package):
			output = "Erro: parametro malicioso!"
		else:
			#tenta executar o comando e obter seu output
			try:
				output = subprocess.check_output(package.split(" "),
						stderr=subprocess.STDOUT)
			except subprocess.CalledProcessError as e:
				output = e.output
		print("Output: " + output)

		#retorna para o socket cliente o output do comando
		#apos isso, encerra a conexao
		self.socket.send(output.encode())
		self.socket.close()
		

#verifica se os argumentos foram passados corretamente
if len(sys.argv) != 3 or sys.argv[1] != "--port":
	print("Uso: ./daemon.py --port PORT")
else:
	port = int(sys.argv[2])
	print("Porta selecionada: " + str(port))

	#cria o socket servidor que vai receber os pacotes
	#sera utilizado o protocolo TCP na camada de transporte
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.bind(("", port))
	
	#socket aceita ate quatro conexoes simultaneas
	serverSocket.listen(4)
	print("Daemon escutando...")

	while(True):
		connectionSocket, address = serverSocket.accept()
		
		#aciona mecanismo de threads para gerenciar conexoes
		connection = CommandExecution(connectionSocket)
		connection.start()

 	serverSocket.close()		
