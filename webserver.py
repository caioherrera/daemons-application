#!/usr/bin/env python
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
	print("Daemon " + str(j) + ":<br><br>")
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
			# Imprime a lista de comandos a ser enviada para execucao
			print(fields[i] + " " + opt + "<br><br>")

