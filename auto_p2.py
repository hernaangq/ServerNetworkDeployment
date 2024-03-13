#!/usr/bin/env python

from lib_mv import MV,Red
import logging, sys, json
from lxml import etree
import os
from subprocess import call


with open('auto-p2.json', 'r') as file:
    data = json.load(file)

if data["num_serv"]>5 or data["num_serv"]<1:
    print("Número de servidores inválido, introduzca en su archivo de configuración un número de servidores de 1 a 5.")
else:
    num_serv = data["num_serv"]


debug = data["debug"]

if debug == True:
	logging.basicConfig(level =logging.DEBUG)
		
else:
	logging.basicConfig(level =logging.INFO)




def init_log():

	
    log = logging.getLogger('auto_p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False


def edit_xml(mv) :

	global tree

	if mv == "c1" or "lb":
		bridge_aux = "LAN1"
	else:
		bridge_aux = "LAN2"

	cwd = os.getcwd()  
	dir = cwd + "/" + mv	

	tree = etree.parse(dir + ".xml")
	root = tree.getroot()

	name = root.find("name")
	name.text = mv


	source = root.find("./devices/disk/source")
	source.set("file", dir + ".qcow2")

	bridge = root.find("./devices/interface/source")
	bridge.set("bridge", bridge_aux)

	if mv == "lb":
		element = etree.Element("interface")
		aux = root.find("devices")
		aux.append(element)
		element.set('type', "bridge")
		etree.SubElement(element, "source", bridge = "LAN2")
		etree.SubElement(element, "model", type = "virtio")


	fout = open(dir + ".xml", "w")
	fout.write(etree.tounicode(tree, pretty_print = True)) 
	fout.close()



def config(mv):
	
	cwd = os.getcwd()
	path = cwd + "/" + mv

	
	fout = open("hostname",'w')  
	fout.write(mv + "\n")  
	fout.close()
	call(["sudo", "virt-copy-in", "-a", mv + ".qcow2", "hostname", "/etc"])
	call(["rm", "-f", "hostname"])

	
	fout = open("hosts",'w')
	fout.write("127.0.1.1 " + mv + "\n") 
	fout.close()
	call(["sudo", "virt-copy-in", "-a", mv + ".qcow2", "hosts", "/etc"])
	call(["rm", "-f", "hosts"])

	
	fout = open("interfaces",'w')
	if mv == "lb":   
		fout.write("auto lo \n iface lo inet loopback \n auto eth0 \n iface eth0 inet static \n address 10.11.1.1  \n netmask 255.255.255.0 \ngateway 10.11.1.1\n auto eth1 \n iface eth1 inet static \n address 10.11.2.1  \n netmask 255.255.255.0 \n gateway 10.11.2.1")
	if mv == "c1":   
		fout.write("auto lo \niface lo inet loopback\n\nauto eth0\niface eth0 inet static\naddress 10.11.1.2\nnetmask 255.255.255.0 \ngateway 10.11.1.1 \n")
	else:
		fout.write("auto lo \niface lo inet loopback\n\nauto eth0\niface eth0 inet static\naddress 10.11.2.3"  + str(mv)[1]+ "\nnetmask 255.255.255.0 \ngateway 10.11.2.1 \n")
	fout.close()
	call(["sudo", "virt-copy-in", "-a", mv + ".qcow2", "interfaces", "/etc/network"])
	call(["rm", "-f", "interfaces"])



	if mv == "lb":
		call(["sudo", "virt-edit", "-a", "lb.qcow2", "/etc/sysctl.conf", "-e", "'s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'"])

	

def crear_escenario():
	c1 = MV("c1")
	c1.crear_mv()
	lb = MV("lb")
	lb.crear_mv()
	red = Red()
	red.crear_red()


def arrancar_escenario():
	c1 = MV("c1")
	c1.arrancar_mv()
	lb = MV("lb")
	lb.arrancar_mv()

def parar_escenario():
	c1 = MV("c1")
	c1.parar_mv()
	lb = MV("lb")
	lb.parar_mv()


def liberar_escenario():
	c1 = MV("c1")
	c1.liberar_mv()
	lb = MV("lb")
	lb.liberar_mv()
	red = Red()
	red.liberar_red()


# Main
init_log()

param = sys.argv

if param[1] == "crear":
	if len(param) == 3:
		if param[2] == "escenario":
			crear_escenario()
		else:
			mv = MV(param[2])
			mv.crear_mv()
	else:
		crear_escenario()
		for i in range(1, num_serv+1):
			mv = MV("s"+str(i))
			mv.crear_mv()
	
		
elif param[1] == "arrancar":
	if len(param) == 3:
		if param[2] == "escenario":
			arrancar_escenario()
		else:
			mv = MV(param[2])
			mv.arrancar_mv()
	else:
		arrancar_escenario()
		for i in range(1, num_serv+1):
			mv = MV("s"+str(i))
			mv.arrancar_mv()
	

elif param[1] == "parar":
	if len(param) == 3:
		if param[2] == "escenario":
			parar_escenario()
		else:
			mv = MV(param[2])
			mv.parar_mv()
	else:
		parar_escenario()
		for i in range(1, num_serv+1):
			mv = MV("s"+str(i))
			mv.parar_mv()


elif param[1] == "liberar":
	if len(param) == 3:
		if param[2] == "escenario":
			liberar_escenario()
		else:
			mv = MV(param[2])
			mv.liberar_mv()
	else:
		liberar_escenario()
		for i in range(1, num_serv+1):
			mv = MV("s"+str(i))
			mv.liberar_mv()

elif param[1] == "ver":
	log.debug("Monitorizacion de TODAS las máquinas virtuales")
	os.system("xterm -title MONITOR -e watch sudo virsh list --all & ")


elif param[1] == "ver-cpu":
    os.system("xterm -title CPU-STATS -e watch sudo virsh cpu-stats " + param[2]) 


elif param[1] == "ver-info":
    os.system("xterm -title INFO -e watch sudo virsh dominfo " + param[2])  


elif param[1] == "--help":
	help = """

  Modo de empleo del código: auto_p2.py <orden> <parametros>
  
  En cuanto a <orden> se pueden tomar los siguientes valores:
    
      ➜ crear: crea el escenario virtual
     
      ➜ arrancar: arranca las maquinas virtuales
			   En el caso de que se quiera arrancar una/unas maquinas virtuales especificas
			   se puede usar <parametros> con el nombre de la maquina seleccionada
			   Ejemplo: auto_p2.py arrancar s1 c1   (arrancara s1 y c1 unicamente)
      
      ➜ parar: para las maquinas virtuales  
			   En el caso de que se quiera parar una/unas maquinas virtuales especificas
			   se puede usar <parametros> con el nombre de la maquina seleccionada
			   Ejemplo: auto_p2.py parar s1 c1  (parara s1 y c1 unicamente)
      
      ➜ liberar: libera las maquinas virtuales y borra todos los ficheros creados
			   En el caso de que se quiera liberar una/unas maquinas virtuales especificas
			   se puede usar <parametros> con el nombre de la maquina seleccionada
			   Ejemplo: auto_p2.py liberar s1 c1  (liberara s1 y c1 unicamente)
       
      ➜ ver: para monitorizar todas las maquinas virtuales y ver su estado
     
      ➜ ver-cpu: para monitorizar el gasto de CPU que utiliza la maquinas virtual, usar con <parametros>
     
      ➜ ver-info: para ver informacion detallada como ID, nombre, estado, tiempo de ejecución,
			   memoria asignada de una maquina virtual, usar con <parametros>
  
	  ➜ --help: este propio comando, con la ayuda para saber que utilizar en cada caso
  
  
  """
  
	print(help)
	
else:
	print("Parámetro inválido, introduzca uno de los siguientes comandos: crear, arrancar, parar, liberar")
