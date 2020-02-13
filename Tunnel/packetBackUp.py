from netfilterqueue import NetfilterQueue
from scapy.all import IP, TCP, UDP, ICMP, ARP, Ether
from Tunnel.VirtualDevice import destroyTap, getVirtualDevices
from Cloaked.probe.ecn_check import ecn_detect
from Cloaked.probe.seqgen_check import seqgen_detect
from Cloaked.probe.T2toT7_check import t2tot7_detect
from Cloaked.probe.icmp_check import icmp_detect
from Cloaked.probe.udp_check import udp_detect
from Cloaked.probe.service_check import service_detect
import gconstant as gc
import time
import sys
from subprocess import DEVNULL, STDOUT, check_call
import socket
import json
import base64


def handle_packet(nfq_packet):
    try:
        pkt = IP(nfq_packet.get_payload())
    except:
        forward_packet(nfq_packet)
        return 0

    if pkt[IP].dst == '127.0.0.1':
        forward_packet(nfq_packet)
        return 0

    virtDevices = getVirtualDevices()  # Get Dict of virtual devices
    if pkt[IP].dst in virtDevices.keys():  # Check if the Packet is intended for any of the virtual devices
        fgrpt = virtDevices[pkt[IP].dst].cfg.fgrpt  # Get the OS Fingerprint of the virtual device
        mac = virtDevices[pkt[IP].dst].macAddr  # Get the MAC Address of the Virtual Device
        services = virtDevices[pkt[IP].dst].cfg.service  # Get the Services of the virtual device
        device_name = virtDevices[pkt[IP].dst].name  # Get the Name of the virtual device
        if pkt.haslayer(TCP):
            port = pkt[TCP].dport
        elif pkt.haslayer(UDP):
            port = pkt[UDP].dport
        else:
            port = 0
        try:
            parse_data = base64.encodebytes(nfq_packet.get_payload()).decode('ascii')
            data = {'timestamp': time.time(), 'dst_ip': pkt[IP].dst, 'host_os': device_name, 'src_ip': pkt[IP].src,
                    'services': port, 'packet': parse_data}
            gc.LOG_PACKET.info(json.dumps(data))
        except Exception as e:
            print('Why?!' + str(e))

    else:
        forward_packet(nfq_packet)  # If packet not intended for the virtual devices, then forward it
        return 0

    #  Check if the packet layer is TCP
    if pkt.haslayer(TCP):
        if not (seqgen_detect(nfq_packet, pkt, fgrpt, mac, gc.SOCKET_INTERFACE) or
                ecn_detect(nfq_packet, pkt, fgrpt, mac, gc.SOCKET_INTERFACE) or
                t2tot7_detect(nfq_packet, pkt, fgrpt, mac, gc.SOCKET_INTERFACE) or
                service_detect(nfq_packet, pkt, fgrpt, mac, services, gc.SOCKET_INTERFACE)):
            forward_packet(nfq_packet)

    #  Check if the packet layer is ICMP
    elif pkt.haslayer(ICMP):
        if not icmp_detect(nfq_packet, pkt, fgrpt, mac, gc.SOCKET_INTERFACE):
            forward_packet(nfq_packet)

    #  Check if the packet layer is UDP
    elif pkt.haslayer(UDP):
        if not udp_detect(nfq_packet, pkt, fgrpt, mac, gc.SOCKET_INTERFACE):
            forward_packet(nfq_packet)

    #  Don't analyse the packet, let it continue to destination
    else:
        forward_packet(nfq_packet)
    return 0


def flush_tables():
    #  Flush IP tables after exiting program
    gc.LOG_DEBUG.debug("Flushing Table")
    check_call(['iptables', '-D', 'INPUT', '-j', 'NFQUEUE', '--queue-num', '2'], stdout=DEVNULL, stderr=STDOUT)


def forward_packet(nfq_packet):
    #  Send the packet from NFQUEUE without modification
    nfq_packet.accept()


def drop_packet(nfq_packet):
    # Drop the packet from NFQUEUE
    nfq_packet.drop()


def rules():
    #  Rules to be added to IP tables
    check_call(['sysctl', 'net.ipv4.conf.all.arp_ignore=1'], stdout=DEVNULL, stderr=STDOUT)
    check_call(['sysctl', 'net.ipv4.conf.all.arp_announce=2'], stdout=DEVNULL, stderr=STDOUT)
    check_call(['sysctl', 'net.ipv4.conf.all.rp_filter=2'], stdout=DEVNULL, stderr=STDOUT)
    check_call(['echo 1 | tee /proc/sys/net/ipv4/ip_forward'], stdout=DEVNULL, stderr=STDOUT, shell=True)
    check_call(['iptables', '-I', 'INPUT', '-j', 'NFQUEUE', '--queue-num', '2'], stdout=DEVNULL, stderr=STDOUT)


def startIntercept():
    rules()
    nfqueue = NetfilterQueue()
    #  Bind it to queue number 2
    nfqueue.bind(2, handle_packet)
    s = socket.fromfd(nfqueue.get_fd(), socket.AF_INET, socket.SOCK_STREAM)
    try:
        #  Start nfqueue
        nfqueue.run_socket(s)
    except KeyboardInterrupt:
        flush_tables()
        nfqueue.unbind()
        destroyTap()
        gc.TCPDUMP.terminate()
        gc.LOG_DEBUG.debug("Exiting Program (Keyboard Interrupt)")
        gc.LOG_DEBUG.debug('#'*50)
        sys.exit()
    except SystemError:
        gc.LOG_DEBUG.debug("Failed to Start NFQueue (System Error)")
        flush_tables()
        nfqueue.unbind()
        destroyTap()
        sys.exit()
    except:
        gc.LOG_DEBUG.debug("Failed to Start NFQueue (Unknown Error Encountered)")
        sys.exit()
