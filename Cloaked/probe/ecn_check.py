from scapy.all import IP, TCP, Ether


def ecn_detect(nfq_pkt, pkt, fp, mac, s_):

    nmap_pkt_condition = (pkt[TCP].window == 3 and pkt[TCP].flags == 0xc2 and
                          pkt[TCP].urgptr == 0xF7F5 and
                          pkt[TCP].options == [('WScale', 10), ('NOP', None),
                                               ('MSS', 1460), ('SAckOK', b''),
                                               ('NOP', None), ('NOP', None)])

    if nmap_pkt_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['ECN']:
            s_.send(ecn_craft(pkt, mac, fp))
        return True
    else:
        return False


def ecn_craft(pkt, mac, fp):
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
    ip.ttl = int(fp.probe['ECN']['TTL'], 16)

    ip_flag = fp.probe['ECN']['DF']
    if ip_flag == 'Y':
        ip.flags = 2
    else:
        ip.flags = 0
    ip.id = fp.ip_id_gen()

    tcp = TCP()
    w_val = fp.probe['ECN']['W']
    if w_val == 'ECHOED':
        tcp.window = pkt[TCP].window
    else:
        tcp.window = w_val
    tcp.sport = pkt[TCP].dport
    tcp.dport = pkt[TCP].sport

    cc_val = fp.probe['ECN']['CC']
    if cc_val == 'Y':
        tcp.flags = 0x52
    elif cc_val == 'N':
        tcp.flags = 0x12
    elif cc_val == 'S':
        tcp.flags = 0xD2
    else:
        tcp.flags = 0x10

    o_val = fp.probe['ECN']['O']
    if o_val == 'EMPTY':
        pass
    else:
        tcp.options = o_val

    fin_pkt = ip / tcp if ether is None else ether / ip / tcp

    return fin_pkt
