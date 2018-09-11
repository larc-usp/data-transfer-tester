#!/usr/bin/python

import time, subprocess, re
from measureTools.models import lftpData

def createRemoteFolder(pasta_des, pasta, usuario, ip_remoto):
	print "\nCriando pasta remota para envio de arquivos ...\n"
	cmd = "if [ ! -d " + "/" + pasta_des + "/" + pasta + " ] ; then mkdir -p /" + pasta_des + "/" + pasta + " ; fi"
	print cmd
	subprocess.check_call(['ssh',usuario + "@" + ip_remoto,cmd])

def removeRemoteFolder(pasta_des, tamanho, usuario, ip_remoto):
	print "\nRemovendo a pasta remota\n"
	cmd = "rm -rf /" + pasta_des + "/" + tamanho
	subprocess.check_call(['ssh',usuario + "@" + ip_remoto,cmd])

def createLocalFolder(pasta_des, tipo, tamanho):
	print "\nCriando pasta local para recebimento de arquivos ...\n"
	cmd = "if [ ! -d " + " /" + pasta_des + "/" + tipo + "/" + tamanho + " ] ; then mkdir -p /" + pasta_des + "/" + tipo + "/" + tamanho + " ; fi"
	subprocess.check_call(cmd, shell=True)

def removeLocalFolder(pasta_des, tipo, tamanho):
	print "\nRemovendo arquivos e pasta local criadas para o recebimento ...\n"
	cmd = "rm -rf " + "/" + pasta_des + "/" + tipo + "/" + tamanho
	subprocess.check_call(cmd, shell=True)

def executeLftP(usuario,ip_remoto,cmd):
	print "\nExecutando o LftP\n"
	retorno = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
	return retorno

def filterLftP(resultado_lftp):
	regex_velocidade = "[\d.]* [\w]*\/sec avg"
	lista_velocidade = re.findall(regex_velocidade,resultado_xrootd)
	velocidade       = lista_velocidade[len(lista_velocidade) - 1]
	velocidade       = velocidade.replace(" avg", "")
	velocidade 		 = "{0:0.1f}".format(convertToMb(velocidade))
	return velocidade

def saveLftPResult(velocidade, cenario, erro, numero_teste):
 	s = lftpData(velocidade=velocidade, scenario = cenario, descricao_erro = erro, num_teste = numero_teste)
	s.save()

def convertToMb(velocidade):
	numero = float(re.search('[\d.]*',velocidade).group(0))

	if velocidade[-6] == "G":
		numero = numero*1024
	elif velocidade[-6] == "k":
		numero = numero/1024

	if velocidade[-5] == "B":
		numero = numero*8

	return numero

def lftpTool(ip_remoto, tamanho, numero_teste, pasta_ori, pasta_des, fluxo, cenario):
	pasta_temp = 'area-teste'
	tipo     = "lftp_ftp"
	usuario  = "sdmz"
	data     = time.strftime('%d/%m %H:%M:%S')
	porta    = "2811"
	pasta 	 = tamanho + "/" + str(fluxo)
	error_description = ''

	try:
		createLocalFolder(pasta_des, tipo, tamanho)
		#cmd_xrootd = "xrdcp -d 3 ftp/test6 root://192.168.122.187//root/FTP/ xrdcp /root/Ftp/test9 test9 -d1"

		#cmd_xrootd = "xrdcp -d 3 "+ pasta_ori  + "/" + tamanho +"  root://" + ip_remoto + " xrdcp   /root/"+ pasta_des + "/" + tipo + "/" + tamanho + "_file_" + str(numero_teste) + " -d1 "
		#cmd_xrootd = "time -p globus-url-copy -vb -p " + str(fluxo) + " ftp://" + ip_remoto + ":" + str(porta)  + "/" + pasta_ori  + "/" + tamanho + "_file file:///" \
		#	+ pasta_des + "/" + tipo + "/" + tamanho + "_file_" + str(numero_teste)
		cmd_lftp = "lftp ftp://admin@192.168.122.198 && cd ftp && put /home/admin/ftp/1G_file"

		print cmd_lftp

		retorno_lftp = executeLftP(usuario, ip_remoto, cmd_lftp)
		resultado_lftp = filterLftP(retorno_lftp)
		removeLocalFolder(pasta_des, tipo, tamanho)
		saveLftPResult(resultado_lftp, cenario, error_description, numero_teste)

	except Exception as e:
		error_description = e
		saveLftPResult(0, cenario, error_description, numero_teste)