import os
from netfilterqueue import NetfilterQueue
from scapy.all import IP, TCP, ICMP, UDP

try:
    from probe.fingerprint import OSFingerprint
    from probe.ecn_check import ecn_detect
    from probe.seqgen_check import seqgen_detect
    from probe.T2toT7_check import t2tot7_detect
    from probe.icmp_check import icmp_detect
    from probe.udp_check import udp_detect
    from probe.service_check import service_detect
    from config.config import Configuration
except ModuleNotFoundError:
    from Cloaked.probe.fingerprint import OSFingerprint
    from Cloaked.probe.ecn_check import ecn_detect
    from Cloaked.probe.seqgen_check import seqgen_detect
    from Cloaked.probe.T2toT7_check import t2tot7_detect
    from Cloaked.probe.icmp_check import icmp_detect
    from Cloaked.probe.udp_check import udp_detect
    from Cloaked.probe.service_check import service_detect
    from Cloaked.config.config import Configuration


def main():
    print('Running...')
    os.system('iptables -F')
    os.system('iptables -A INPUT -j NFQUEUE --queue-num 1')
    nfqueue = NetfilterQueue()
    nfqueue.bind(1, callback)
    try:
        nfqueue.run()
    except KeyboardInterrupt:
        os.system('iptables -F')


def callback(nfq_pkt):
    pkt = IP(nfq_pkt.get_payload())
    if pkt.haslayer(TCP):
        if not (seqgen_detect(nfq_pkt, pkt, cfg.fgrpt, cfg.service) or
                ecn_detect(nfq_pkt, pkt, cfg.fgrpt, cfg.service) or
                t2tot7_detect(nfq_pkt, pkt, cfg.fgrpt, cfg.service) or
                service_detect(nfq_pkt, pkt, cfg.fgrpt, cfg.service)):
            nfq_pkt.accept()

    elif pkt.haslayer(ICMP):
        if not icmp_detect(nfq_pkt, pkt, cfg.fgrpt):
            nfq_pkt.accept()

    elif pkt.haslayer(UDP):
        if not udp_detect(nfq_pkt, pkt, cfg.fgrpt):
            nfq_pkt.accept()


if __name__ == '__main__':

    service_list = dict()
    service_list[22] = b'SSH-9-AudioCodes\n'
    service_list[80] = b'HTTP/1.0 200 OK\r\nContent-type: text/html; charset=UTF-8\r\nPragma: no-cache\r\nWindow-target: _top\r\n'
    service_list[21] = b"220-GuildFTPd FTP Server (c) 1997-2002\r\n220-Version 0.999.14\r\n"
    cfg = Configuration()
    cfg.set_service(service_list)
    cfg.set_fgrpt('./Cloaked/mini-os.txt')
    cfg.set_debug(True)
    cfg.save_cfg()
    main()
