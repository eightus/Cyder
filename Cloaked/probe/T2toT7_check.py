from scapy.all import IP, TCP, Ether
import random

try:
    from probe.crc_help import compensate
except ModuleNotFoundError:
    from Cloaked.probe.crc_help import compensate


def t2tot7_detect(nfq_pkt, pkt, fp, mac, s_):

    nmap_pkt_t2_condition = (pkt[TCP].window == 128 and pkt[TCP].flags == 0x00 and
                             pkt[IP].flags == 2 and
                             pkt[TCP].options == [('WScale', 10), ('NOP', None),
                                               ('MSS', 265), ('Timestamp', (4294967295, 0)),
                                               ('SAckOK', b'')])

    nmap_pkt_t3_condition = (pkt[TCP].window == 256 and pkt[TCP].flags == 0x02b and
                             pkt[TCP].options == [('WScale', 10), ('NOP', None),
                                                  ('MSS', 265), ('Timestamp', (4294967295, 0)),
                                                  ('SAckOK', b'')])

    nmap_pkt_t4_condition = (pkt[TCP].window == 1024 and pkt[TCP].flags == 0x010 and
                             pkt[IP].flags == 2 and
                             pkt[TCP].options == [('WScale', 10), ('NOP', None),
                                                  ('MSS', 265), ('Timestamp', (4294967295, 0)),
                                                  ('SAckOK', b'')])

    nmap_pkt_t5_condition = (pkt[TCP].window == 31337 and pkt[TCP].flags == 0x002 and
                             pkt[TCP].options == [('WScale', 10), ('NOP', None),
                                                  ('MSS', 265), ('Timestamp', (4294967295, 0)),
                                                  ('SAckOK', b'')])

    nmap_pkt_t6_condition = (pkt[TCP].window == 32768 and pkt[TCP].flags == 0x010 and
                             pkt[IP].flags == 2 and
                             pkt[TCP].options == [('WScale', 10), ('NOP', None),
                                                  ('MSS', 265), ('Timestamp', (4294967295, 0)),
                                                  ('SAckOK', b'')])

    nmap_pkt_t7_condition = (pkt[TCP].window == 65535 and pkt[TCP].flags == 0x029 and
                             pkt[TCP].options == [('WScale', 15), ('NOP', None),
                                                  ('MSS', 265), ('Timestamp', (4294967295, 0)),
                                                  ('SAckOK', b'')])

    # ----------------------------------------------------------------------------

    if nmap_pkt_t2_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['T2']:
            s_.send(t2tot7_craft(pkt, fp, mac, 'T2'))
        return True

    elif nmap_pkt_t3_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['T3']:
            s_.send(t2tot7_craft(pkt, fp, mac, 'T3'))
        return True

    elif nmap_pkt_t4_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['T4']:
            s_.send(t2tot7_craft(pkt, fp, mac, 'T4'))
        return True

    elif nmap_pkt_t5_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['T5']:
            s_.send(t2tot7_craft(pkt, fp, mac, 'T5'))
        return True

    elif nmap_pkt_t6_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['T6']:
            s_.send(t2tot7_craft(pkt, fp, mac, 'T6'))
        return True

    elif nmap_pkt_t7_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['T7']:
            s_.send(t2tot7_craft(pkt, fp, mac, 'T7'))
        return True

    else:
        return False


def t2tot7_craft(pkt, fp, mac, tno):
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
    ip.ttl = int(fp.probe[tno]['TTL'], 16)
    ip.flags = fp.probe[tno]['DF']
    ip.id = random.randint(1, 1000)

    tcp = TCP()

    s_val = fp.probe[tno]['S']
    if s_val == 'Z':
        tcp.seq = 0
    elif s_val == 'A':
        tcp.seq = pkt[TCP].ack
    elif s_val == 'A+':
        tcp.seq = pkt[TCP].ack + 1
    else:
        tcp.seq = pkt[TCP].ack + 369

    a_val = fp.probe[tno]['A']
    if a_val == 'Z':
        tcp.ack = 0
    elif a_val == 'S':
        tcp.ack = pkt[TCP].seq
    elif a_val == 'S+':
        tcp.ack = pkt[TCP].seq + 1
    else:
        tcp.ack = pkt[TCP].seq + 369

    flag_val = fp.probe[tno]['F']
    tcp.flags = flag_val

    w_val = fp.probe[tno]['W']
    if w_val == 'ECHOED':
        tcp.window = pkt[TCP].window
    else:
        tcp.window = w_val

    tcp.sport = pkt[TCP].dport
    tcp.dport = pkt[TCP].sport

    o_val = fp.probe[tno]['O']
    if o_val == 'EMPTY':
        pass
    else:
        tcp.options = o_val

    rd_val = fp.probe[tno]['RD']
    if rd_val != '0':
        crc = int(rd_val, 16)
        data = b'TCP Port is closed\x00'
        data += compensate(data, crc)
        fin_pkt = ip / tcp / data if ether is None else ether / ip / tcp / data
    else:
        fin_pkt = ip / tcp if ether is None else ether / ip / tcp

    return fin_pkt

