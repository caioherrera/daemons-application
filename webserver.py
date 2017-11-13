#!/usr/bin/env python
import cgitb
import cgi
cgitb.enable()

form = cgi.FieldStorage()
fields = ["ps", "df", "finger", "uptime"]

print("Content-Type: text/html;charset=utf-8\r\n\r\n")
print("<head><title>Trabalho 1 de Redes</title></head>")

# Testando apenas para o Daemon 1
print("Teste Daemon 1<br><br>")
commands = []
# Para cada Comando
for i in range(4):
	# Testa se o checkbox do comando foi marcado
	if "maq1_" + fields[i] in form:
		opt = ""
		# Testa se existem parametros para o comando, e caso tenha concatena eles em opt
		if "maq1-" + fields[i] in form:
			opt = " " + form["maq1-" + fields[i]].value
		# Adiona opt (parametros dos comandos) na lista de comandos a serem executado
		commands.append((i + 1, opt))
		# Imprime a lista de comandos a ser enviada para execucao
		print(fields[commands[i][0] - 1] + " " + commands[i][1] + "<br><br>")

