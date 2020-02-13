import socket
from netaddr import IPNetwork


def network(ip, mask, cidr):
    iOctets = ip.split('.')
    mOctets = mask.split('.')

    sys_network = str(int(iOctets[0]) & int(mOctets[0])) + '.'
    sys_network += str(int(iOctets[1]) & int(mOctets[1])) + '.'
    sys_network += str(int(iOctets[2]) & int(mOctets[2])) + '.'
    sys_network += str(int(iOctets[3]) & int(mOctets[3]))
    sys_network = sys_network + "/" + str(cidr)
    print(sys_network)
    return sys_network


def ipRange(start_ip, end_ip):
    start = list(map(int, start_ip.split(".")))
    end = list(map(int, end_ip.split(".")))
    temp = start
    ip_range = [start_ip]

    while temp != end:
        start[3] += 1
        for i in (3, 2, 1):
            if temp[i] == 256:
                temp[i] = 0
                temp[i - 1] += 1
        ip_range.append(".".join(map(str, temp)))

    return ip_range


def getAvailableIP(ip, mask, cidr, newNetwork):  # newNetwork is in the format 10.10.10.0/24

    if not newNetwork:
        networkAddr = network(ip,mask,cidr)
    else:
        networkAddr = newNetwork
    ip = IPNetwork(networkAddr)
    ip_range = ipRange(str(ip[2]), str(ip[-2])) # start from .2 to .254

    unused_ip_range = []
    used_ip_range = []

    print("Start getting available IP")
    for ip in ip_range:
        try:
            used_ip_range.append(socket.gethostbyaddr(ip)[0])
        except socket.error:
            unused_ip_range.append(ip)
            pass
    print("Finish getting available IP")
    return unused_ip_range
