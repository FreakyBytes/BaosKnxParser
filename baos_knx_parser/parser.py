
from . import struct
from .const import TelegramType, APCI
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
    frame_type_flag, repeated_flag, system_broadcast_flag, priority, acknowledge_request_flag, confirm_flag = struct.KNX_CTRL.unpack(knx_binary[0:1])
    acknowledge_request_flag = not acknowledge_request_flag  # acknowledge_request_flag flag is send inverted
    confirm_flag = not confirm_flag  # if `not confirm_flag` => error
    repeated_flag = not repeated_flag  # same with repeated_flag flag

    # parse CTRLE (it is send anyway in BAOS)
    destination_address_type, hop_count, extended_frame_format = struct.KNX_CTRLE.unpack(knx_binary[1:2])

    # create data model class
    if frame_type_flag == TelegramType.EXT:
        telegram = KnxExtendedTelegram(timestamp=timestamp, telegram_type=frame_type_flag, repeat=repeated_flag, ack=acknowledge_request_flag,
                                       priority=priority, confirm=confirm_flag, hop_count=hop_count, eff=extended_frame_format)
    else:
        telegram = KnxStandardTelegram(timestamp=timestamp, telegram_type=frame_type_flag, repeat=repeated_flag, ack=acknowledge_request_flag,
                                       priority=priority, confirm=confirm_flag, hop_count=hop_count)

    # parse addresses
    telegram.src = parse_knx_addr(knx_binary[2:4])
    telegram.dest = parse_knx_addr(knx_binary[4:6], group=destination_address_type)

    # parse payload
    telegram.payload_length, = struct.KNX_LENGTH.unpack(knx_binary[6:7])
    telegram.payload = knx_binary[7:9 + telegram.payload_length]
    if telegram.apci == APCI.A_GROUP_VALUE_WRITE and telegram.payload_length == 0:
        # Take last 6 Bits of Byte as payload-data
        telegram.payload_data = int(bin(int(knx_binary[8:9].hex(), 16))[4:10])
    if telegram.apci == APCI.A_GROUP_VALUE_WRITE and telegram.payload_length > 0:
        telegram.payload_data = int(knx_binary[9:9+telegram.payload_length].hex(), 16)
    if telegram.apci != APCI.A_GROUP_VALUE_WRITE:
        raise Exception(f'Parsing of Payload for {telegram.apci} not yet implemented!')
    return telegram


def parse_knx_addr(binary, group=False):
    if group:
        area, line, device = struct.KNX_ADDR_GROUP.unpack(binary)
    else:
        area, line, device = struct.KNX_ADDR_PHYSICAL.unpack(binary)
    return KnxAddress(area=area, line=line, device=device, group=group)
