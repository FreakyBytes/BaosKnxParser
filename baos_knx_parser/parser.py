
from . import struct
from .const import TelegramType
from .knx import KnxAddress, KnxExtendedTelegram, KnxStandardTelegram


def parse_knx_telegram(binary, timestamp=None):
    telegram = None

    # cEMI stuff
    msg_code, = struct.CEMI_MSG_CODE.unpack(binary[0:1])
    if msg_code != 0x29:
        raise TypeError("Can only parse L_Data.ind (0x29) at the moment, but got {}".format(hex(msg_code)))

    add_len, = struct.CEMI_ADD_LEN.unpack(binary[1:2])
    knx_binary = binary[add_len + 2:]

    # parse CTRL
    telegram_type, repeat, broadcast, priority, ack, confirm = struct.KNX_CTRL.unpack(knx_binary[0:1])
    ack = not ack  # ack flag is send inverted
    confirm = not confirm  # if `not confirm` => error
    repeat = not repeat  # same with repeat flag

    # parse CTRLE (it is send anyway in BAOS)
    addr_type, hop_count, eff = struct.KNX_CTRLE.unpack(knx_binary[1:2])

    # create data model class
    if telegram_type == TelegramType.EXT:
        telegram = KnxExtendedTelegram(timestamp=timestamp, telegram_type=telegram_type, repeat=repeat, ack=ack,
                                       priority=priority, confirm=confirm, hop_count=hop_count, eff=eff)
    else:
        telegram = KnxStandardTelegram(timestamp=timestamp, telegram_type=telegram_type, repeat=repeat, ack=ack,
                                       priority=priority, confirm=confirm, hop_count=hop_count)

    # parse addresses
    telegram.src = parse_knx_addr(knx_binary[2:4])
    telegram.dest = parse_knx_addr(knx_binary[4:6], group=addr_type)

    # parse payload
    telegram.payload_length, = struct.KNX_LENGTH.unpack(knx_binary[6:7])
    telegram.payload = knx_binary[7:9 + telegram.payload_length]

    return telegram


def parse_knx_addr(binary, group=False):
    if group:
        area, line, device = struct.KNX_ADDR_GROUP.unpack(binary)
    else:
        area, line, device = struct.KNX_ADDR_PHYSICAL.unpack(binary)
    return KnxAddress(area=area, line=line, device=device, group=group)
