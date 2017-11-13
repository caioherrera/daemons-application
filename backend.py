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

def computeChecksum(wordLen, identification, prt, src, dst, opt, chk = 0):
	checksum = chk
	checksum += (2 << 12) | (wordLen << 8)
	checksum += wordLen * 4
	checksum += identification
	checksum += 7 << 13
	checksum += (64 << 8) | prt
	source = struct.unpack("!I", src)
	dest = struct.unpack("!I", dst)
	checksum += (source[0] >> 16) + (source[0] & 0xFFFF)
	checksum += (dest[0] >> 16) + (dest[0] & 0xFFFF)

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
	checksum = computeChecksum(wordLen, daemons["seq"][num], prt, src, dst, opt)

	#instancia o stream de bytes 
	pkg = io.BytesIO()

	#primeira word do cabecalho: version, IHL, Type of Service e Total Length
	word = (2 << 28) | (wordLen << 24) | (wordLen * 4)
	pkg.write(struct.pack("!I", word))

	#segunda word do cabecalho: identification, flags, fragment offset
	word = (daemons["seq"][num] << 16) | (7 << 13)
	pkg.write(struct.pack("!I", word))

	#terceira word do cabecalho: timeToLive, protocol, headerChecksum iniciado com 0
	word = (64 << 24) | (prt << 16) | checksum
	pkg.write(struct.pack("!I", word))

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
	aux = struct.unpack("!IIIII", pkg.read(20))
	#for a in aux:
		#print(hex(a))

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
		#print("source: " + str(gethostbyname(gethostname())))
		destination = inet_aton(daemons["ip"][num])

		#envia o pacote para o daemon e aguarda o retorno
		pkg = createPackage(c[0], c[1], num, source, destination)
		pkg.seek(0)
		clientSocket.send(pkg.read())

		#recupera o pacote de resposta do daemon
		pkg = io.BytesIO(clientSocket.recv(10240))

		pkg.seek(0, 2)
		outputLen = pkg.tell() - 20

		pkg.seek(20)
		o = struct.unpack("s" * outputLen, pkg.read())
		outputs.append("".join(o))

		clientSocket.close()

	return outputs
