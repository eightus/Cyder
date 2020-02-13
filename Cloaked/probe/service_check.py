from scapy.all import IP, TCP, Ether, Raw

# check = ['nmaplowercheck', 'NmapUpperCheck', 'POST /sdk', 'HNAP1', 'GET / HTTP/1.0\r\n\r\n']
# check = [i.encode() for i in check]


def service_detect(nfq_pkt, pkt, fp, mac, service, s_):

    nmap_syn_condition = (pkt[TCP].flags == 0x002 and
                          pkt[TCP].dport in service.keys() and
                          pkt[TCP].ack == 0)

    # nmap_ack_pshack_condition = ((pkt[TCP].flags == 0x010 or pkt[TCP].flags == 0x018) and
    #                              pkt[TCP].dport in service.keys() and
    #                              pkt[TCP].seq == pkt[TCP].ack and
    #                              pkt.haslayer(Raw) and
    #                              any(txt in pkt[Raw].load for txt in check))

    nmap_ack_condition = (pkt[TCP].flags == 0x010 and
                          pkt[TCP].dport in service.keys() and
                          pkt[TCP].seq == pkt[TCP].ack)

    if nmap_syn_condition:
        nfq_pkt.drop()
        s_.send(service_craft(pkt, fp, mac, service))
        return True

    # elif nmap_ack_pshack_condition:
    #     nfq_pkt.drop()
    #     s_.send(service_craft(pkt, fp, mac, service, True))
    #     return True

    elif nmap_ack_condition:
        nfq_pkt.drop()
        s_.send(service_craft(pkt, fp, mac, service, True))
        return True

    else:
        return False


def service_craft(pkt, fp, mac, service, type_=False):
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
    ip.ttl = int(fp.ttl, 16)
    ip.flags = 0x4000

    tcp = TCP()
    tcp.sport = pkt[TCP].dport
    tcp.dport = pkt[TCP].sport

    if type_:
        tcp.flags = 0x018  # PSH / ACK
        tcp.seq = pkt[TCP].seq
        tcp.ack = pkt[TCP].ack
        data = service[pkt[TCP].dport]
        fin_pkt = ip / tcp / data if ether is None else ether / ip / tcp / data
        return fin_pkt
    else:
        tcp.flags = 0x012  # SYN / ACK
        tcp.seq = pkt[TCP].seq
        tcp.ack = pkt[TCP].seq + 1
        fin_pkt = ip / tcp if ether is None else ether / ip / tcp
        return fin_pkt


