#!/usr/bin/env python
from backend import *
import cgitb
import cgi
cgitb.enable()

form = cgi.FieldStorage()
fields = ["ps", "df", "finger", "uptime"]

print("Content-Type: text/html;charset=utf-8\r\n\r\n")
print("<head><title>Trabalho 1 de Redes</title></head>")

# Para cada Daemon
for j in range(1, 4):
	commands = []
	print("<h1>Daemon " + str(j) + ":</h1>")
	# Para cada Comando
	for i in range(4):
		# Testa se o checkbox do comando foi marcado
		if "maq" + str(j) + "_" + fields[i] in form:
			opt = ""
			# Testa se existem parametros para o comando, e caso tenha concatena eles em opt
			if "maq" + str(j) + "-" + fields[i] in form:
				opt = " " + form["maq" + str(j) +"-" + fields[i]].value
			# Adiona opt (parametros dos comandos) na lista de comandos a serem executado
			commands.append((i + 1, opt))
	# Executa lista de comandos do Daemon
	outputs = executeCommands(commands, j-1)

	# Para cada Comando
	for i in range(len(outputs)):
		# Imprime o Comando executado e os seus paramentros
		print("<h3>" + fields[commands[i][0] - 1] + " " + commands[i][1] + "</h3>")
		# Imprime o Output do Comando
		print(outputs[i].replace("\n", "<br>") + "<br><br>")

