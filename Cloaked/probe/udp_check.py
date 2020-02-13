from scapy.all import IP, ICMP, Raw, UDP, IPerror, UDPerror, Ether


def udp_detect(nfq_pkt, pkt, fp, mac, s_):
    nmap_pkt_condition = (pkt[IP].id == 0x1042 and
                          len(pkt[Raw].load) == 300 and
                          pkt[Raw].load == 300 * b'C')

    if nmap_pkt_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['U1']:
            s_.send(udp_craft(pkt, mac, fp))
        return True
    else:
        return False


def udp_craft(pkt, mac, fp):
    try:
        ether = Ether()
        ether.src = mac
        ether.dst = pkt[Ether].dst
        ether.type = 0x800
    except IndexError:
        ether = None

    ip = IP()
    ip.src = pkt[IP].dst
    ip.dst = pkt[IP].src
    ip.ttl = int(fp.probe['U1']['TTL'], 16)
    ip.flags = fp.probe['U1']['DF']
    ip.len = 56
    ip.id = 4162

    icmp = ICMP()
    icmp.type = 3
    icmp.unused = 0
    icmp.code = 13  # code 3 for reply

    iperror = IPerror()
    iperror.proto = 'udp'
    iperror.ttl = 0x3E
    iperror.len = fp.probe['U1']['RIPL']
    iperror.id = fp.probe['U1']['RID']

    ripck_val = fp.probe['U1']['RIPCK']
    if ripck_val == 'G':
        pass
    elif ripck_val == 'Z':
        iperror.chksum = 0
    else:
        iperror.chksum = pkt[IP].chksum

    udperror = UDPerror()
    udperror.sport = pkt[UDP].sport
    udperror.dport = pkt[UDP].dport
    udperror.len = pkt[UDP].len
    if fp.probe['U1']['RUCK'] == 'G':
        udperror.chksum = pkt[UDP].chksum
    else:
        udperror.chksum = fp.probe['U1']['RUCK']

    try:
        ipl = int(fp.probe['U1']['IPL'], 16)
    except KeyError:
        ipl = None

    data = pkt[Raw].load

    fin_pkt = ip / icmp / iperror / udperror / data if ether is None else ether / ip / icmp / iperror / udperror / data

    return fin_pkt
