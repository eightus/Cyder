from binascii import crc32
from struct import pack

FINALXOR = 0xffffffff
INITXOR = 0xffffffff
CRCPOLY = 0xEDB88320
CRCINV = 0x5B358FD3


def tableAt(byte):
    return crc32(chr(byte ^ 0xff)) & 0xffffffff ^ FINALXOR ^ (INITXOR >> 8)


def compensate(buf, wanted):
    wanted ^= FINALXOR

    newBits = 0
    for i in range(32):
        if newBits & 1:
           newBits >>= 1
           newBits ^= CRCPOLY
        else:
           newBits >>= 1

        if wanted & 1:
           newBits ^= CRCINV

        wanted >>= 1

    newBits ^= crc32(buf) ^ FINALXOR
    return pack('<L', newBits)

