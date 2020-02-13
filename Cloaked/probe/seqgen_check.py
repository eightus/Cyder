from scapy.all import IP, TCP, Ether

try:
    from probe.crc_help import compensate
except ModuleNotFoundError:
    from Cloaked.probe.crc_help import compensate


def seqgen_detect(nfq_pkt, pkt, fp, mac, s_):

    # ----------------------------------------------------------------------------
    nmap_pkt1_condition = (pkt[TCP].window == 1 and pkt[TCP].flags == 0x02 and
                           pkt[TCP].options == [('WScale', 10), ('NOP', None),
                                                ('MSS', 1460), ('Timestamp', (4294967295, 0)),
                                                ('SAckOK', b'')])

    nmap_pkt2_condition = (pkt[TCP].window == 63 and pkt[TCP].flags == 0x02 and
                           pkt[TCP].options == [('MSS', 1400), ('WScale', 0),
                                                ('SAckOK', b''), ('Timestamp', (4294967295, 0)),
                                                ('EOL', None)])

    nmap_pkt3_condition = (pkt[TCP].window == 4 and pkt[TCP].flags == 0x02 and
                           pkt[TCP].options == [('Timestamp', (4294967295, 0)),
                                                ('NOP', None), ('NOP', None),
                                                ('WScale', 5), ('NOP', None),
                                                ('MSS', 640)])

    nmap_pkt4_condition = (pkt[TCP].window == 4 and pkt[TCP].flags == 0x02 and
                           pkt[TCP].options == [('SAckOK', b''),
                                                ('Timestamp', (4294967295, 0)),
                                                ('WScale', 10), ('EOL', None)])

    nmap_pkt5_condition = (pkt[TCP].window == 16 and pkt[TCP].flags == 0x02 and
                           pkt[TCP].options == [('MSS', 536), ('SAckOK', b''),
                                                ('Timestamp', (4294967295, 0)),
                                                ('WScale', 10), ('EOL', None)])

    nmap_pkt6_condition = (pkt[TCP].window == 512 and pkt[TCP].flags == 0x02 and
                           pkt[TCP].options == [('MSS', 265), ('SAckOK', b''),
                                                ('Timestamp', (4294967295, 0))])

    # ----------------------------------------------------------------------------

    if nmap_pkt1_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['PKT_1']:
            s_.send(seqgen_pkt_craft(pkt, fp, mac, '1'))
        return True

    elif nmap_pkt2_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['PKT_2']:
            s_.send(seqgen_pkt_craft(pkt, fp, mac, '2'))
        return True

    elif nmap_pkt3_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['PKT_3']:
            s_.send(seqgen_pkt_craft(pkt, fp, mac, '3'))
        return True

    elif nmap_pkt4_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['PKT_4']:
            s_.send(seqgen_pkt_craft(pkt, fp, mac, '4'))
        return True

    elif nmap_pkt5_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['PKT_5']:
            s_.send(seqgen_pkt_craft(pkt, fp, mac, '5'))
        return True

    elif nmap_pkt6_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['PKT_6']:
            s_.send(seqgen_pkt_craft(pkt, fp, mac, '6'))
        return True

    else:
        return False


def seqgen_pkt_craft(pkt, fp, mac, pno):
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
    ip.ttl = int(fp.probe['T1']['TTL'], 16)
    ip.flags = fp.probe['T1']['DF']
    ip.id = fp.ip_id_gen()

    tcp = TCP()

    s_val = fp.probe['T1']['S']
    if s_val == 'Z':
        tcp.seq = 0
    elif s_val == 'A':
        tcp.seq = pkt[TCP].ack
    elif s_val == 'A+':
        tcp.seq = pkt[TCP].ack + 1
    else:
        tcp.seq = fp.tcp_seq_gen()

    a_val = fp.probe['T1']['A']
    if a_val == 'Z':
        tcp.ack = 0
    elif a_val == 'S':
        tcp.ack = pkt[TCP].seq
    elif a_val == 'S+':
        tcp.ack = pkt[TCP].seq + 1
    else:
        tcp.ack = pkt[TCP].seq + 369

    flag_val = fp.probe['T1']['F']
    tcp.flags = flag_val

    tcp.window = fp.probe['WIN']['W' + pno]

    tcp.sport = pkt[TCP].dport
    tcp.dport = pkt[TCP].sport

    tcp.options = fp.probe['OPS']['O' + pno]

    rd_val = fp.probe['T1']['RD']
    if rd_val != '0':
        crc = int(rd_val, 16)
        data = b'TCP Port is closed\x00'
        data += compensate(data, crc)
        fin_pkt = ip / tcp / data if ether is None else ether / ip / tcp / data

    else:
        fin_pkt = ip / tcp if ether is None else ether / ip / tcp
    return fin_pkt
