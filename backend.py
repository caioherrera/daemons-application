from socket import *
import struct
import io

#define os parametros de cada um dos daemons
#seq representa a identificacao do ultimo pacote enviado
daemons = {
	"ip": ["127.0.0.1", "127.0.0.1", "127.0.0.1"],
	"porta": [9001, 9002, 9003],
	"seq": [0, 0, 0]
}

#funcao placeholder, retorna 0 ate ser implementada
def computeChecksum():
	return 0

def createPackage(prt, opt, num, src, dst):
	
	#obtem o comprimento do campo options em bytes e em words
	#alem de definir o tamanho do padding
	pad = 0
	byteLen = len(opt)
	wordLen = byteLen // 4
	if byteLen % 4 > 0:
		wordLen += 1
		pad = 4 - (byteLen % 4)

	#soma o comprimento de options com a parte fixa do cabecalho
	wordLen += 5

	optionsLen = len(opt)

	#instancia o stream de bytes 
	pkg = io.BytesIO()

	#primeira word do cabecalho: version, IHL, Type of Service e Total Length
	pkg.write(struct.pack("B", (2 << 4 | wordLen))
	pkg.write(struct.pack("B", 0)
	pkg.write(struct.pack("H", wordLen * 4))

	#segunda word do cabecalho: identification, flags, fragment offset
	pkg.write(struct.pack("H", daemons["seq"][num]))
	pkg.write(struct.pack("H", 7 << 13))

	#terceira word do cabecalho: timeToLive, protocol, headerChecksum iniciado com 0
	pkg.write(struct.pack("B", 64))
	pkg.write(struct.pack("B", prt))
	pkg.write(struct.pack("H", computeChecksum())

	#quarta e quinta words do cabecalho: source address e destination address,
	#alem de options e padding
	pkg.write(src)
	pkg.write(dst)
	pkg.write(opt)
	for i in range(pad):
		pkg.write(struct.pack("B", 0))

	#atualiza o ultimo numero de sequencia do daemon
	daemons["seq"][num] += 1

	pkg.seek(0)
	aux = struct.unpack("IIIII", pkg.read(20))
	for a in aux:
		print(hex(a))

	return pkg

def executeCommands(commands, num):

	outputs = []

	#assume-se commands como uma lista de pares (protocol, options), seguindo
	#as especificacoes do cabecalho
	for c in commands:

		#cria o socket cliente para enviar o pacote para o daemon
		#utilizando o protocolo TCP na camada de transporte
		clientSocket = socket(AF_INET, SOCK_STREAM)
		clientSocket.connect((daemons["ip"][num], daemons["porta"][num]))

		#define o endereco de origem e destino do pacote
		#no caso deste trabalho, ambos sao equivalentes
		source = inet_aton(gethostbyname(gethostname()))
		destination = inet_aton(daemons["ip"][num])

		#envia o pacote para o daemon e aguarda o retorno
		pkg = createPackage(c[0], c[1], num, source, destination)
		pkg.seek(0)
		clientSocket.send(pkg.read())
		#o = clientSocket.recv(2048)
		#outputs.append(o)

		clientSocket.close()

	return outputs
