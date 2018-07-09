
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
    apci = telegram.apci
    telegram.payload_data = parse_payload_data(apci,knx_binary[7:9 + telegram.payload_length], telegram.payload_length)
    return telegram


def parse_knx_addr(binary, group=False):
    if group:
        area, line, device = struct.KNX_ADDR_GROUP.unpack(binary)
    else:
        area, line, device = struct.KNX_ADDR_PHYSICAL.unpack(binary)
    return KnxAddress(area=area, line=line, device=device, group=group)


def parse_payload_data(apci, payload_bytes, payload_length):
    possible_short_payload = [APCI.A_INDIVIDUAL_ADDRESS_RESPONSE,
                              APCI.A_GROUP_VALUE_WRITE, APCI.A_GROUP_VALUE_RESPONSE]
    no_payload = [APCI.A_GROUP_VALUE_READ, APCI.A_INDIVIDUAL_ADDRESS_READ]
    individual_address_serial_number_payload = [APCI.A_INDIVIDUAL_ADDRESS_SERIAL_NUMBER_RESPONSE,
                                                APCI.A_INDIVIDUAL_ADDRESS_SERIAL_NUMBER_WRITE]
    network_parameter_payload = [APCI.A_NETWORK_PARAMETER_READ, APCI.A_NETWORK_PARAMETER_RESPONSE,
                                 APCI.A_NETWORK_PARAMETER_WRITE]

    if apci in possible_short_payload:
        if payload_length == 0:
            # Take last 6 Bits of Byte as payload-data
            payload_data = int(bin(int(payload_bytes[1:2].hex(), 16))[4:10])
        else:
            payload_data = int(payload_bytes[2:2 + payload_length].hex(), 16)
    elif apci in no_payload:
        payload_data = None
    elif apci == APCI.A_INDIVIDUAL_ADDRESS_WRITE:
        payload_data = parse_knx_addr(payload_bytes[2:2 + payload_length])
    elif apci == APCI.A_INDIVIDUAL_ADDRESS_SERIAL_NUMBER_READ:
        payload_data = int(payload_bytes[2:2 + payload_length].hex(), 16)
    elif apci in individual_address_serial_number_payload:
        # values separated in Serial number, Domain Address/New Address
        payload_data = [int(payload_bytes[2:8].hex(), 16), parse_knx_addr(payload_bytes[8:9])]
    elif apci in network_parameter_payload:
        # values separated in Interface object type, Property-ID, Test_info/Test_info+Test_result/Value
        payload_data = [int(payload_bytes[2:4].hex(), 16), int(payload_bytes[4:5].hex(), 16),
                        int(payload_bytes[5:2 + payload_length].hex(), 16)]
    else:
        raise Exception(f'Parsing of Payload for {telegram.apci} not yet implemented!')
    return payload_data
