import bitstruct

STD_U16 = bitstruct.compile('>u16')
STD_U8 = bitstruct.compile('>u8')

CEMI_MSG_CODE = STD_U8
CEMI_ADD_LEN = STD_U8

KNX_CTRL = bitstruct.compile('>u2b1b1u2b1b1')
KNX_CTRLE = bitstruct.compile('>b1u3u4')
KNX_ADDR_PHYSICAL = bitstruct.compile('>u4u4u8')
KNX_ADDR_GROUP = bitstruct.compile('>u5u3u8')
KNX_DRL = bitstruct.compile('>b1u3u4')
KNX_LENGTH = STD_U8

KNX_APCI = bitstruct.compile('>p6u10')
KNX_TPCI = bitstruct.compile('>u2p4p2')
KNX_TPCI_APCI = bitstruct.compile('>u2u4u10')
KNX_NPCI = bitstruct.compile('>b1u3u4')
KNX_PACKET_NUMBER = bitstruct.compile('>p2u4p2')

KNX_ACK = STD_U8
