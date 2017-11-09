#!/usr/bin/env python
from socket import *
import sys
import subprocess
import threading
import io
import struct

commands = ["ps", "df", "finger", "uptime"]

def computeChecksum(headerLen, totalLen, identification, prt, source, dest, opt, chk = 0):
	checksum = chk
	checksum += (2 << 12) | headerLen << 8
	checksum += totalLen * 4
	checksum += identification
	checksum += 7 << 13
	checksum += (64 << 8) | prt
	checksum += (source >> 16) + (source & 0xFFFF)
	checksum += (dest >> 16) + (dest & 0xFFFF)

	flag = True
	partialsum = 0
	for c in opt:
		flag = not flag
		if flag:
			partialsum += ord(c)
			checksum += partialsum
			partialsum = 0
		else:
			partialsum = ord(c) << 8
	
	checksum = (checksum & 0xFFFF) + (checksum >> 32)
	checksum = (checksum ^ 0xFFFF)

	return checksum

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
		package = io.BytesIO(self.socket.recv(2048))
		package.seek(0)
		header = struct.unpack("!IIIII", package.read(20))

		#obtem as options associadas ao comando
		package.seek(20)
		optionsLen = (((header[0] >> 24) & 15) - 5) * 4
		options = struct.unpack(optionsLen * "s", package.read())
		options = "".join(options)

		#obtem comando pelo campo protocol
		command = commands[((header[2] >> 16) & 0xFF) - 1]
		command += options		
		print(command)

		#verifica se e seguro executar o comando
		output = ""
		dangerous = set(";>|")
		if any((c in dangerous) for c in options):
			output = "Erro: parametro malicioso!"
		else:
			#tenta executar o comando e obter seu output
			try:
				output = subprocess.check_output(command.split(" "), stderr=subprocess.STDOUT)
			except subprocess.CalledProcessError as e:
				output = e.output
		print("Output: " + output)
		
		#modifica cabecalho do pacote para retornar
		outputLen = len(output) // 4
		if len(output) % 4 > 0:
			outputLen += 1

		newHeader = []
		newHeader.append((header[0] & 0xF0FF0000) | (5 << 24) | (20 + outputLen * 4))
		newHeader.append(header[1] & 0xFFFF0FFF)
		newHeader.append(header[2] - 0x01000000)
		newHeader.append(header[4])
		newHeader.append(header[3])
		chk = computeChecksum(5, outputLen, newHeader[1] >> 16, (newHeader[2] >> 16) & 0x00FF, newHeader[3], newHeader[4], output)
		newHeader[2] = newHeader[2] | chk

		pkg = io.BytesIO()
		for h in header:
			pkg.write(struct.pack("!I", h))
		pkg.write(output)
		
		#retorna para o socket cliente o output do comando
		#apos isso, encerra a conexao
		pkg.seek(0)
		self.socket.send(pkg.read())
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
