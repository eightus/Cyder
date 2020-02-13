from scapy.all import IP, ICMP, Raw, Ether
import random

# --------------------------------------------------------------------------------
# NMAP ICMP Echo (IE) Conditions
# IE tests involves sending 2 ICMP echo request packets to the target
#
#       ICMP Packet (1)
#           ICMP Type     = Echo Request  |   Payload     = 120 Bytes
#           ICMP Sequence = 295           |   ICMP Code   = 9
#           IP TOS        = 0             |   IP Flags    = DF (2)
# --------------------------------------------------------------------------------
#       ICMP Packet (2)
#           ICMP Type     = Echo Request  |   Payload     = 150 Bytes
#           ICMP Sequence = 296           |   ICMP Code   = 0
#           IP TOS        = 4             |   IP Flags    = 0 (Empty)
#           ICMP ID       = Packet (1).ID + 1
# --------------------------------------------------------------------------------


def icmp_detect(nfq_pkt, pkt, fp, mac, s_):

    nmap_pkt1_condition = (pkt[ICMP].type == 8 and
                           pkt[ICMP].seq == 295 and pkt[ICMP].code == 9 and
                           pkt[IP].tos == 0 and pkt[IP].flags == 2 and len(pkt[Raw].load) == 120)

    nmap_pkt2_condition = (pkt[ICMP].type == 8 and
                           pkt[ICMP].seq == 296 and pkt[ICMP].code == 0 and
                           pkt[IP].tos == 4 and
                           pkt[IP].flags == 0 and len(pkt[Raw].load) == 150)

    nmap_pkt3_condition = (pkt[ICMP].type == 8)
    # ----------------------------------------------------------------------------

    if nmap_pkt1_condition or nmap_pkt2_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['IE']:
            s_.send(icmp_craft(pkt, fp, mac))
        return True
    elif nmap_pkt3_condition:
        nfq_pkt.drop()
        if fp.Craft_Respond['IE']:
            s_.send(icmp_craft(pkt, fp, mac))
        return True
    else:
        return False


def icmp_craft(pkt, fp, mac):
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
    ip.ttl = int(fp.probe['IE']['TTL'], 16)
    dfi_flag = fp.probe['IE']['DFI']
    if dfi_flag == 'N':
        ip.flags = 0
    elif dfi_flag == 'S':
        ip.flags = pkt[IP].flags
    elif dfi_flag == 'Y':
        ip.flags = 2
    else:
        ip.flags = 0 if pkt[IP].flags == 2 else 2

    ip.id = fp.ip_id_icmp_gen()
    icmp = ICMP()
    icmp.type = 0
    icmp.id = pkt[ICMP].id

    cd_val = fp.probe['IE']['CD']
    if cd_val == 'Z':
        icmp.code = 0
    elif cd_val == 'S':
        icmp.code = pkt[ICMP].code
    else:
        icmp.code = random.randint(0, 15)

    icmp.seq = pkt[ICMP].seq
    data = pkt[ICMP].payload

    fin_pkt = ip / icmp / data if ether is None else ether / ip / icmp / data
    return fin_pkt

