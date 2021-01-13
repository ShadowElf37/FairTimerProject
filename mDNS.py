from socket import *
from struct import pack, unpack
from data import *
from math import ceil

QTYPE = {'A':1,
         'AAAA': 28,
         'AFSDB': 18,
         'APL': 42,
         'CAA': 257,
         'CDNSKEY': 60,
         'CDS': 59,
         'CERT': 37,
         'CNAME': 5,
         'DHCID': 49,
         'DLV': 32769,
         'DNAME': 39,
         'DNSKEY': 48,
         'DS': 43,
         'LOC': 29,
         'NS': 2,
         'PTR': 12,
         'SIG': 24,
         'SRV': 33,
         'TXT': 16,
         'URI': 256,
         '*': 255}

class mDNSQueryHeader:
    def __init__(self, qname, qtype, req_unicast=0, qclass=1):
        self.qname = qname
        self.qtype = QTYPE[qtype]
        self.req_unicast = req_unicast
        self.qclass = qclass
        self.header = [
            self.qname,  # v
            0, # 8, nullbyte ending qname
            self.qtype,  # 16
            Bin(self.req_unicast) + Bin(self.qclass),  # 1+15
        ]

    def compile(self):
        return pack('!%ssBHH' % len(self.qname), *self.header)

class mDNSRecord:
    def __init__(self, bytes):
        self.name = ...
        self.type = ...
        self.cache_flush = ...
        self._class = ...
        self.ttl = ...
        self.dlength = ...
        self.data = ...