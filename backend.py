from socket import *

#define os parametros de cada um dos daemons
#seq representa a identificacao do ultimo pacote enviado
daemons = {
	"ip": ["127.0.0.1", "127.0.0.1", "127.0.0.1"],
	"porta": [9001, 9002, 9003],
	"seq": [0, 0, 0]
}

def executeCommands(commands, num):

	outputs = []

	for c in commands:

		#cria o socket cliente para enviar o pacote para o daemon
		#utilizando o protocolo TCP na camada de transporte
		clientSocket = socket(AF_INET, SOCK_STREAM)
		clientSocket.connect((daemons["ip"][num], daemons["porta"][num]))

		#envia o pacote para o daemon e aguarda o retorno
		clientSocket.send(c.encode())
		o = clientSocket.recv(2048).decode()
		outputs.append(o)

		clientSocket.close()

	return outputs
