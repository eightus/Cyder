import os
import netifaces as ni
from netaddr import IPAddress
from .getAvailableIP import getAvailableIP
from Cloaked.config.config import Configuration
import gconstant as gc

# Setting of global variables
virtDevices = {}
usedIP = []
macVLANCount = 0


class VirtualDevice:

    def __init__(self, name=None, macAddr=None, services=None, network=None, fingerprint=None,
                 ip=None, VLANCount=None):  # services is a dict, { 21 : ssh }
        self.VLANCount = VLANCount
        self.MacVLan = False

        if not fingerprint:  # If no OS fingerprint is set, then use default from text file
            fingerprint = './Cloaked/mini-os.txt'

        self.name = name  # Set device name
        self.http = True
        self.macAddr = macAddr  # Set device mac address
        self.hostIP, self.hostSubnet, self.cidr = getIPfromInterface()  # Get host machine ip, subnet and cidr

        # Setting of IP address and Virtual Interface
        if not ip:
            if not network:
                self.ip = self.getNewIPAddr(self.hostIP, self.hostSubnet, self.cidr)
                # if IP and network not supplied, auto get ip from host network
                self.connection()
                self.MacVLan = True
            else:
                # if ip not supplied but network supplied, then auto get ip from network
                self.ip = self.getNewIPAddr(self.hostIP, self.hostSubnet, self.cidr, network)
                # Auto get available ip from network
                self.connection()
                self.MacVLan = True
        else:
            self.ip = ip  # user specified IP
            if ip != self.hostIP:  # check if ip address is the host ip
                self.connection()  # Create the tunnel
                self.MacVLan = True

        self.cfg = Configuration()
        self.cfg.set_fgrpt(fingerprint) # Set OS fingerprint
        self.cfg.set_service(services) # Set services
        self.cfg.save_cfg()

    def connection(self): # Setting up new Virtual Interface using MacVLAN
        macVLAN = 'mac' + str(self.VLANCount)
        os.system('sudo ip link add {} link {} type macvlan mode bridge'.format(macVLAN, gc.INTERFACE))
        os.system('sudo ip addr add {}/{} dev {}'.format(self.ip, self.cidr, macVLAN))
        os.system('sudo ifconfig {} hw ether {}'.format(macVLAN, self.macAddr))
        os.system('sudo ifconfig {} up'.format(macVLAN))

    def getNewIPAddr(self, hostIP, hostSubnet, cidr, network=None):  # Get list of unused ip addresses in the network
        ipList = getAvailableIP(hostIP, hostSubnet, cidr, network)
        return ipList[0]  # return 1 ip address


def updateDevice(old_ipAddr, new_ipAddr, services=None, fingerprint=None, name=None, macAddr=None): # Update device's services and fingerprint
    if services:
        virtDevices[old_ipAddr].services = services
        virtDevices[old_ipAddr].cfg.set_service(services)
        gc.LOG_DEBUG.debug("Updating the services of {}".format(str(old_ipAddr)))
    if fingerprint:
        virtDevices[old_ipAddr].device = fingerprint
        virtDevices[old_ipAddr].cfg.set_fgrpt(fingerprint)
        virtDevices[old_ipAddr].cfg.save_cfg()  # Save Debug Only For Fingerprint
        gc.LOG_DEBUG.debug("Updating the fingerprint of {}".format(str(old_ipAddr)))
    if name:
        virtDevices[old_ipAddr].name = name
        gc.LOG_DEBUG.debug("Updating the name of {}".format(str(old_ipAddr)))
    if macAddr:
        virtDevices[old_ipAddr].macAddr = macAddr
        if old_ipAddr != virtDevices[old_ipAddr].hostIP: # Check if the device is the host machine
            os.system('sudo ifconfig mac{} hw ether {}'.format(virtDevices[old_ipAddr].VLANCount, virtDevices[old_ipAddr].macAddr))
        else:
            #  If host machine
            os.system('sudo ifconfig {} hw ether {}'.format(gc.INTERFACE, virtDevices[old_ipAddr].macAddr))
        gc.LOG_DEBUG.debug("Updating the Mac Address of {}".format(str(old_ipAddr)))
    if new_ipAddr:
        if old_ipAddr != new_ipAddr:
            if old_ipAddr != virtDevices[old_ipAddr].hostIP:
                os.system('sudo ifconfig mac{} {}'.format(virtDevices[old_ipAddr].VLANCount,new_ipAddr))
            else:
                os.system('sudo ifconfig {} {}'.format(gc.INTERFACE, new_ipAddr))
            virtDevices[new_ipAddr]= virtDevices.pop(old_ipAddr)
            usedIP.remove(old_ipAddr)
            usedIP.append(new_ipAddr)
            gc.LOG_DEBUG.debug("Updating the ip from {} to {}".format(str(old_ipAddr),str(new_ipAddr)))


def addNewDevice(name=None, services=None, network=None, fingerprint=None, ip=None, mac_addr=None):  # Adding new Device
    global macVLANCount
    print("Adding new device - {}".format(str(ip)))
    device = VirtualDevice(name=name, services=services, network=network, fingerprint=fingerprint, ip=ip,VLANCount=macVLANCount,macAddr=mac_addr)
    virtDevices[device.ip] = device  # Key is IP address, Value is the Virtual Device Object
    if device.ip == virtDevices[device.ip].hostIP and not (mac_addr == 'false' or mac_addr is None):
        #  Check if IP is host Machine IP address
        os.system('sudo ifconfig {} hw ether {}'.format(gc.INTERFACE, mac_addr))
    usedIP.append(device.ip)  # Stored the IP used by virtual device
    macVLANCount = macVLANCount + 1
    gc.LOG_DEBUG.debug("Added new device " + str(device.ip))


def deleteDevice(ip=None, name=None):
    gc.LOG_DEBUG.debug("Deleting device of ".format(str(ip)))
    device = virtDevices[ip]
    if device.ip != virtDevices[device.ip].hostIP: # check if the ip belongs to the host machine
        try:
            os.system('sudo ifconfig mac{} down'.format(device.VLANCount))
            os.system('sudo ip link del mac{}'.format(device.VLANCount))
        except Exception:
            gc.LOG_DEBUG.debug("Failed to remove the virtual interface of {}".format(str(ip)))
    del virtDevices[ip]
    usedIP.remove(ip)


def getIPfromInterface():
    ip = ni.ifaddresses(gc.INTERFACE)[ni.AF_INET][0]['addr']
    subnet = ni.ifaddresses(gc.INTERFACE)[ni.AF_INET][0]['netmask']
    CIDR = IPAddress(subnet).netmask_bits()
    return ip, subnet, CIDR


def getUsedIP():
    return usedIP


def getVirtualDevices():
    return virtDevices


def initalise():
    hostIP, subnet, cidr = getIPfromInterface()
    usedIP.append(str(hostIP))  # Adding host IP to list of Ip address of Devices


def destroyTap():
    #  Destroy virtual interface before exiting program
    gc.LOG_DEBUG.debug("Destroying Virtual Interfaces")
    for i in virtDevices.values():
        #  Check if there is virtual interface before destroying
        if i.MacVLan:
            try:
                os.system('sudo ifconfig mac{} down'.format(i.VLANCount))
                os.system('sudo ip link del mac{}'.format(i.VLANCount))
            except:
                gc.LOG_DEBUG.debug("Failed to destroy mac{}".format(i.VLANCount))
