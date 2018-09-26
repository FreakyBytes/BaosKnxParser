
from . import struct
from .const import TelegramType, APCI
from .knx import KnxAddress, KnxExtendedTelegram, KnxStandardTelegram, KnxAcknowledgementTelegram

def parse_knx_telegram(binary, timestamp=None):
    # check message code
    msg_code, = struct.CEMI_MSG_CODE.unpack(binary[0:1])
    if msg_code == 0x29:
        return parse_data_ind(binary, timestamp)
    elif msg_code == 0x2B:
        return parse_busmon_ind(binary, timestamp)
    else:
        raise TypeError("Can only parse L_Data.ind (0x29) and L_Busmon.ind (0x2B) at the moment, but got {}".format(hex(msg_code)))


def parse_busmon_ind(binary, timestamp=None):
    telegram = None
    add_len, = struct.CEMI_ADD_LEN.unpack(binary[1:2])
    knx_binary = binary[add_len + 2:]

    if len(knx_binary) == 1:
        # handle ACK telegram
        acknowledgement, = struct.KNX_ACK.unpack(knx_binary[0:1])
        return KnxAcknowledgementTelegram(acknowledgement=acknowledgement)

    # parse CTRL
    frame_type_flag, repeated_flag, system_broadcast_flag, priority, acknowledge_request_flag, confirm_flag = struct.KNX_CTRL.unpack(knx_binary[0:1])
    acknowledge_request_flag = not acknowledge_request_flag # acknowledge_request_flag flag is send inverted
    confirm_flag = not confirm_flag  # if `not confirm_flag` => error
    repeated_flag = not repeated_flag  # same with repeated_flag flag

    # parse NPCI
    destination_address_type, hop_count, payload_length = struct.KNX_NPCI.unpack(knx_binary[5:6])

    # create data model class
    if frame_type_flag == TelegramType.EXT:
        telegram = KnxExtendedTelegram(timestamp=timestamp, telegram_type=frame_type_flag, repeat=repeated_flag, ack=acknowledge_request_flag,
                                       priority=priority, confirm=confirm_flag, hop_count=hop_count)
    else:
        telegram = KnxStandardTelegram(timestamp=timestamp, telegram_type=frame_type_flag, repeat=repeated_flag, ack=acknowledge_request_flag,
                                       priority=priority, confirm=confirm_flag, hop_count=hop_count)
    
    # parse addresses
    telegram.src = parse_knx_addr(knx_binary[1:3])
    telegram.dest = parse_knx_addr(knx_binary[3:5], group=destination_address_type)

    # parse payload
    telegram.payload_length = payload_length - 1
    telegram.payload = knx_binary[6:8 + telegram.payload_length]
    apci = telegram.apci
    telegram.payload_data = parse_payload_data(apci, knx_binary[6:8 + telegram.payload_length], telegram.payload_length)
    return telegram

def parse_data_ind(binary, timestamp=None):
    telegram = None
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
                              APCI.A_GROUP_VALUE_WRITE, APCI.A_GROUP_VALUE_RESPONSE, APCI.A_DEVICE_DESCRIPTOR_READ]
    no_payload = [APCI.A_GROUP_VALUE_READ, APCI.A_INDIVIDUAL_ADDRESS_READ, APCI.A_DOMAIN_ADDRESS_READ,
                  APCI.A_USER_MANUFACTURE_INFO_READ, APCI.A_RESTART]
    individual_address_serial_number_payload = [APCI.A_INDIVIDUAL_ADDRESS_SERIAL_NUMBER_RESPONSE,
                                                APCI.A_INDIVIDUAL_ADDRESS_SERIAL_NUMBER_WRITE]
    network_parameter_payload = [APCI.A_NETWORK_PARAMETER_READ, APCI.A_NETWORK_PARAMETER_RESPONSE,
                                 APCI.A_NETWORK_PARAMETER_WRITE]
    domain_address_payload = [APCI.A_DOMAIN_ADDRESS_WRITE, APCI.A_DOMAIN_ADDRESS_RESPONSE]
    property_value_payload = [APCI.A_PROPERTY_VALUE_RESPONSE, APCI.A_PROPERTY_VALUE_WRITE]
    memory_write_payload = [APCI.A_MEMORY_RESPONSE, APCI.A_MEMORY_WRITE]
    user_memory_payload = [APCI.A_USER_MEMORY_RESPONSE, APCI.A_USER_MEMORY_WRITE]
    memory_bit_payload = [APCI.A_MEMORY_BIT_WRITE, APCI.A_USER_MEMORY_BIT_WRITE]

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
    elif apci == APCI.A_SERVICE_INFORMATION_INDICATION_WRITE:
        payload_bits = bin(int(payload_bytes[2:3].hex()))
        # values separated in verify mode, dupl. phys. Addr, appl. stopped
        payload_data = [payload_bits[5], payload_bits[6], payload_bits[7]]
    elif apci in domain_address_payload:
        payload_data = parse_knx_addr(payload_bytes[2:2+payload_length], True)
    elif apci == APCI.A_DOMAIN_ADDRESS_SELECTIVE_READ:
        # values separated in domain address, start address, range
        payload_data = [parse_knx_addr(payload_bytes[2:4], True), parse_knx_addr(payload_bytes[4:6]), payload_bytes[6]]
    elif apci == APCI.A_PROPERTY_VALUE_READ:
        payload_bits = bin(int(payload_bytes[4:6].hex(), 16))
        # values separated in Object_index, Property_id, nr_of_elem, Start_index
        payload_data = [int(payload_bytes[2:3].hex(), 16), int(payload_bytes[3:4].hex(), 16), int(payload_bits[0:4]),
                        int(payload_bits[4:])]
    elif apci in property_value_payload:
        payload_bits = bin(int(payload_bytes[4:6].hex(), 16))
        # values separated in Object_index, Property_id, nr_of_elem, Start_index, Data
        payload_data = [int(payload_bytes[2:3].hex(), 16), int(payload_bytes[3:4].hex(), 16), int(payload_bits[0:4]),
                        int(payload_bits[4:]), payload_bytes[6:2 + payload_length]]
    elif apci == APCI.A_PROPERTY_DESCRIPTION_READ:
        # values separated in Object_index, Property_id, Property_index
        payload_data = [int(payload_bytes[2:3].hex(), 16), int(payload_bytes[3:4].hex(), 16),
                        int(payload_bytes[4:5].hex(), 16)]
    elif apci == APCI.A_PROPERTY_DESCRIPTION_RESPONSE:
        payload_bits = bin(int(payload_bytes[8:9].hex(), 16))
        # values separated in Object_index, Property_id, Property_index, Type, max_nr_of_elem,
        # Access (read_level, write_level)
        payload_data = [int(payload_bytes[2:3].hex(), 16), int(payload_bytes[3:4].hex(), 16),
                        int(payload_bytes[4:5].hex(), 16), int(payload_bytes[5:6].hex(), 16),
                        int(payload_bytes[6:8].hex(), 16), int(payload_bits[0:4]), int(payload_bits[4:])]
    elif apci == APCI.A_DEVICE_DESCRIPTOR_RESPONSE:
        # values separated in Descriptor_type, Device descriptor
        payload_data = [int(bin(int(payload_bytes[1:2].hex(), 16))[4:10]),
                        int(payload_bytes[2:2 + payload_length].hex(), 16)]
    elif apci == APCI.A_LINK_READ:
        # values separated in Group_object_number, Start_index
        payload_data = [int(payload_bytes[2:3].hex(), 16), int(payload_bytes[3:4].hex(), 16)]
    elif apci == APCI.A_LINK_RESPONSE:
        payload_bits = bin(int(payload_bytes[3:4].hex(), 16))
        # values separated in Group_object_number, Sending_address, Start_address, Group_address_list
        payload_data = [int(payload_bytes[2:3].hex(), 16), int(payload_bits[0:4]), int(payload_bits[4:]),
                        int(payload_bytes[4:].hex(), 16)]
    elif apci == APCI.A_LINK_WRITE:
        payload_bits = bin(int(payload_bytes[3:4].hex(), 16))
        # values separated in Group_object_number, d flag, s flag, Group_address
        payload_data = [int(payload_bytes[2:3].hex(), 16), payload_bits[6:7], payload_bits[7:8],
                        int(payload_bytes[4:].hex(), 16)]
    elif apci == APCI.A_ADC_READ:
        # values separated in Channel_nr, Read_count
        payload_data = [bin(int(payload_bytes[1:2].hex(), 16))[4:10], int(payload_bytes[2:3].hex(), 16)]
    elif apci == APCI.A_ADC_RESPONSE:
        # values separated in Channel_nr, Read_count, Sum of AD_converter_Access
        payload_data = [bin(int(payload_bytes[1:2].hex(), 16))[4:10], int(payload_bytes[2:3].hex(), 16),
                        int(payload_bytes[3].hex(), 16)]
    elif apci == APCI.A_MEMORY_READ:
        payload_bits = bin(int(payload_bytes[1:2].hex(), 16))[6:10]
        # values separated in number, address
        payload_data = [payload_bits, parse_knx_addr(payload_bytes[2:4])]
    elif apci in memory_write_payload:
        payload_bits = bin(int(payload_bytes[1:2].hex(), 16))[6:10]
        # values separated in number, address, Data
        payload_data = [payload_bits, parse_knx_addr(payload_bytes[2:4]), payload_bytes[4:].hex()]
    elif apci in memory_bit_payload:
        number = int(payload_bytes[2:3].hex(), 16)
        # values separated in number, address, and_data, xor_data
        payload_data = [number, parse_knx_addr(payload_bytes[3:5]), payload_bytes[5:5 + number].hex(),
                        payload_bytes[5 + number:2 + 2 * number].hex()]
    elif apci == APCI.A_USER_MEMORY_READ:
        payload_bits = bin(int(payload_bytes[2:3].hex(), 16))
        # values separated in address extension, number, address
        payload_data = [int(payload_bits[0:4]), int(payload_bits[4:8]), parse_knx_addr(payload_bytes[3:5])]
    elif apci in user_memory_payload:
        payload_bits = bin(int(payload_bytes[2:3].hex(), 16))
        # values separated in address extension, number, address, data
        payload_data = [int(payload_bits[0:4]), int(payload_bits[4:8]), parse_knx_addr(payload_bytes[3:5]),
                        payload_bytes[5:].hex()]
    elif apci == APCI.A_USER_MANUFACTURE_INFO_RESPONSE:
        # values separated in manufacturer_id, manufacturer specific
        payload_data = [int(payload_bytes[2:3].hex(), 16), payload_bytes[3:5].hex()]
    elif apci == APCI.A_AUTHORIZE_REQUEST:
        # values separated in must be 0, Key
        payload_data = [int(payload_bytes[2:3].hex(), 16), payload_bytes[3:].hex()]
    elif apci == APCI.A_AUTHORIZE_RESPONSE:
        payload_data = int(payload_bytes[2:3].hex(), 16)
    elif apci == APCI.A_KEY_WRITE:
        # values separated in level, key
        payload_data = [int(payload_bytes[2:3].hex(), 16), payload_bytes[3:].hex()]
    elif apci == APCI.A_KEY_RESPONSE:
        payload_data = int(payload_bytes[2:3].hex(), 16)
    else:
        raise Exception('Parsing of Payload for {0} not yet implemented!'.format(telegram.apci))
    return payload_data
