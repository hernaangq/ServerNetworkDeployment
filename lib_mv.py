import logging,json
from subprocess import call
from lxml import etree
import os

log = logging.getLogger('auto_p2')


def edit_xml(mv) :
    
    if mv == "c1":
      bridge_aux = "LAN1"
    elif mv == "lb":
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

    fout = open(dir + ".xml", "w")
    fout.write(etree.tounicode(tree, pretty_print = True)) 
    fout.close()

    if mv == "lb":
      fin = open(dir + ".xml",'r')   
      fout = open("temporal.xml",'w')  
      for line in fin:
        if "</interface>" in line:
          fout.write("</interface>\n <interface type='bridge'>\n <source bridge='"+"LAN2"+"'/>\n <model type='virtio'/>\n </interface>\n")
        else:
          fout.write(line)
      fin.close()
      fout.close()

      call(["cp","./temporal.xml", dir + ".xml"])  
      call(["rm", "-f", "./temporal.xml"])



def config(mv):
    cwd = os.getcwd()
    path = cwd + "/" + mv

    
    fout = open("hostname",'w')  
    fout.write(mv + "\n")  
    fout.close()
    call(["sudo", "virt-copy-in", "-a", mv + ".qcow2", "hostname", "/etc"])
    call(["rm", "-f", "hostname"])

    

    call("sudo virt-edit -a " + mv + ".qcow2 /etc/hosts -e 's/127.0.1.1.*/127.0.1.1 " + mv + "/'", shell=True)

    fout = open("interfaces",'w')
    if mv == "lb":   
      fout.write("auto lo \niface lo inet loopback \n\nauto eth0 \niface eth0 inet static \n  address 10.11.1.1  \n netmask 255.255.255.0 \n gateway 10.11.1.1\n\nauto eth1 \niface eth1 inet static \n  address 10.11.2.1  \n netmask 255.255.255.0 \n gateway 10.11.2.1\n")
      call("sudo virt-edit -a lb.qcow2 /etc/sysctl.conf -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'", shell=True)

    else:
      if mv == "c1":   
        fout.write("auto lo \niface lo inet loopback \n auto eth0 \n iface eth0 inet static \n address 10.11.1.2  \nnetmask 255.255.255.0 \n gateway 10.11.1.1 \n")
        
        
      else:
        fout.write("auto lo \niface lo inet loopback \n auto eth0 \n iface eth0 inet static \n address 10.11.2.3"  + str(mv)[1]+ " \nnetmask 255.255.255.0  \n gateway 10.11.2.1 \n")
      
    fout.close()
    call(["sudo", "virt-copy-in", "-a", mv + ".qcow2", "interfaces", "/etc/network"])
    call(["rm", "-f", "interfaces"])

    

class MV:
  def __init__(self, nombre):
    self.nombre = nombre


  def crear_mv (self):
    log.debug("crear_mv " + self.nombre)
    call(["qemu-img","create", "-f", "qcow2", "-b", "./cdps-vm-base-pc1.qcow2", self.nombre +".qcow2"])
    call(["cp", "plantilla-vm-pc1.xml", self.nombre+".xml"])
    edit_xml(self.nombre)
    log.debug("Fichero XML de "+self.nombre+" modificados con éxito.")
    call(["sudo", "virsh", "define", self.nombre+".xml"])
    log.debug("Máquinas "+self.nombre+" definida con éxito.")
    config(self.nombre)
    
  def arrancar_mv (self):
    log.debug("arrancar_mv " + self.nombre)
    call(["sudo", "virsh", "start", self.nombre])
    os.system("xterm -e 'sudo virsh console "+ self.nombre +"' &")
    
  def parar_mv (self):
    log.debug("parar_mv " + self.nombre)
    call(["sudo","virsh","shutdown", self.nombre])

  def liberar_mv (self):
    log.debug("liberar_mv " + self.nombre)
    call(["sudo","virsh","destroy",self.nombre])
    call(["sudo", "virsh", "undefine", self.nombre])
    call(["rm", "-f", self.nombre+".qcow2"])	
    call(["rm", "-f", self.nombre+".xml"])

  
class Red:
  def __init__(self):
    log.debug('init Red')

  def crear_red(self):
    log.debug("crear_red")
    call(["sudo", "brctl", "addbr", "LAN1"])
    call(["sudo", "brctl", "addbr", "LAN2"])
    call(["sudo", "ifconfig", "LAN1", "up"])
    call(["sudo", "ifconfig", "LAN2", "up"])
    call(["sudo", "ifconfig", "LAN1", "10.11.1.3/24"])
    call(["sudo", "ip", "route", "add", "10.11.0.0/16", "via", "10.11.1.1"])
    log.debug("La configuración de la red se ha llevado a cabo.")

  def liberar_red(self):
    call(["sudo", "ifconfig", "LAN1", "down"])
    call(["sudo", "ifconfig", "LAN2", "down"])
    call(["sudo", "brctl", "delbr", "LAN1"])
    call(["sudo", "brctl", "delbr", "LAN2"])
