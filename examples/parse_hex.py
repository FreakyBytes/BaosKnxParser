#!/usr/bin/env python3

import baos_knx_parser as knx

"""
This example shows, how to take the complete hex from the logs and parse all standard fields
"""

t = knx.parse_knx_telegram(bytes.fromhex('2b090301000604c16cc3a9bc361612bee300800000ac'))
print(t)
print(t.tpci)
print()

t = knx.parse_knx_telegram(bytes.fromhex('2b090301010604c16d031bcc'))
print(t)
print()

print("00:04:01        2012-02-27      3.2.50  2/3/4   00800C7E        2900BCC0323213040200800C7E")
t = knx.parse_knx_telegram(bytes.fromhex('2900BCC0323213040200800C7E'))
print(t)
print(t.apci)
print()


print("00:06:10        2012-02-27      3.6.39  2/2/232 00800C7E        2900BCE0362712E80200800C7E")
t = knx.parse_knx_telegram(bytes.fromhex('2900BCE0362712E80200800C7E'))
print(t)
print(t.apci)


print()
print("00:06:12        2012-02-27      3.5.37  2/2/4   0081    2900BCC035251204000081")
t = knx.parse_knx_telegram(bytes.fromhex('2900BCC035251204000081'))
print(t)
print(t.apci)
