import bitstruct

CEMI_MSG_CODE = bitstruct.compile('>u8')
CEMI_ADD_LEN = bitstruct.compile('>u8')

KNX_CTRL = bitstruct.compile('>u2b1b1u2b1b1')
KNX_CTRLE = bitstruct.compile('>b1u3u4')
KNX_ADDR_PHYSICAL = bitstruct.compile('>u4u4u8')
KNX_ADDR_GROUP = bitstruct.compile('>u5u3u8')
KNX_DRL = bitstruct.compile('>b1u3u4')
KNX_LENGTH = bitstruct.compile('>u8')

KNX_APCI = bitstruct.compile('>p6u10')
