
from datetime import datetime

from . import struct  # precompiled bitstructs
from .const import TelegramType, TelegramPriority, APCI, TPCI, TelegramAcknowledgement


class KnxAddress(object):
    PHYSICAL_DELIMITER = '.'
    GROUP_DELIMITER = '/'

    def __init__(self, str=None, area=None, line=None, device=None, group=False):

        if str and (area or line or device):
            raise TypeError("Either set the address as string or as separated fields. Not both")

        if str:
            segments = str.split(KnxAddress.PHYSICAL_DELIMITER if not group else KnxAddress.GROUP_DELIMITER)
            self.area = segments[0]
            self.line = segments[1]
            self.device = segments[2]
        else:
            self.area = area
            self.line = line
            self.device = device

        self.group = group

    def __repr__(self):
        return "KnxAddress('{str}', group={group})".format(str=str(self), group=self.group)

    def __str__(self):
        return "{area}{delim}{line}{delim}{device}".format(
            area=self.area, line=self.line, device=self.device,
            delim=KnxAddress.PHYSICAL_DELIMITER if not self.group else KnxAddress.GROUP_DELIMITER
        )

    def __int__(self):
        bin_addr = self.to_binary()
        integer, = struct.STD_U16.unpack(bin_addr)
        return integer

    def __float__(self):
        return float(self.__int__())

    def __eq__(self, value):
        if not isinstance(value, KnxAddress):
            return False

        return self.group == value.group and self.area == value.area and self.line == value.line and self.device == value.device

    def to_binary(self):
        if not self.group:
            return struct.KNX_ADDR_PHYSICAL.pack(self.area, self.line, self.device)
        else:
            return struct.KNX_ADDR_GROUP.pack(self.area, self.line, self.device)

    def is_group_address(self):
        return self.group

    def is_physical_address(self):
        return not self.group


class KnxBaseTelegram(object):

    def __init__(self, telegram_type=TelegramType.DATA, repeat=False, ack=False, priority=TelegramPriority.NORMAL, confirm=True, src=None, dest=None, hop_count=0, timestamp=None):
        self.timestamp = timestamp if timestamp else datetime.now()
        self.telegram_type = TelegramType(telegram_type)
        self.repeat = repeat
        self.ack = ack
        self.priority = TelegramPriority(priority)
        self.confirm = confirm
        self.src = src
        self.dest = dest
        self.hop_count = hop_count

    def __repr__(self):
        return """KnxExtendedTelegram(src='{src}', dest='{dest}', telegram_type={tt},
    repeat={repeat}, ack={ack}, priority={prio}, hop_count={hop_count}, timestamp={timestamp})""".format(tt=repr(self.telegram_type), prio=repr(self.priority), **self.__dict__)

    @property
    def tpdu(self):
        if self.payload:
            return self.payload[0]
        else:
            return None

    @property
    def apci(self):
        if not self.payload:
            return None

        apci_num, = struct.KNX_APCI.unpack(self.payload[0:3])
        return APCI(apci_num)

    @property
    def tpci(self):
        if not self.payload:
            return None

        tpci_num, = struct.KNX_TPCI.unpack(self.payload[0:2])
        return TPCI(tpci_num)

    @property
    def packet_number(self):
        if not self.payload:
            return None

        count, = struct.KNX_PACKET_NUMBER.unpack(self.payload[0:2])
        return count

    @property
    def packet_count(self):
        import warnings
        warnings.warn("packet_count is deprecated, used packet_number", DeprecationWarning)

        return self.packet_number

    def to_binary(self):
        raise NotImplemented()


class KnxStandardTelegram(KnxBaseTelegram):

    def __init__(self, payload_length=None, payload=bytes(), *args, **kwargs):
        super(KnxStandardTelegram, self).__init__(*args, **kwargs)

        if payload_length is not None and not len(payload) == payload_length - 2:
            raise TypeError("Payload length mismatch")

        self.payload = payload
        self.payload_data = None
        self.payload_length = payload_length if payload_length is not None else len(payload) - 2

    def __repr__(self):
        p = self.payload.hex()
        return """KnxStandardTelegram(src='{src}', dest='{dest}', telegram_type={tt},
    repeat={repeat}, ack={ack}, priority={prio}, hop_count={hop_count}, timestamp='{timestamp}',
    payload_length={payload_length}, payload=payload=bytes.fromhex('{p}')), payload_data={payload_data}"""\
            .format(tt=repr(self.telegram_type), prio=repr(self.priority), p=p, **self.__dict__)

    def to_binary(self):
        binary = b''.join((
            struct.CEMI_MSG_CODE.pack(0x29),  # cEMI header
            struct.CEMI_ADD_LEN.pack(0),  # no additional cEMI/BAOS info here, since they are not stored in the KNX Datamodel
            struct.KNX_CTRL.pack(int(self.telegram_type), not self.repeat, 3, int(self.priority), not self.ack, not self.confirm),
            struct.KNX_CTRLE.pack(self.dest.group, self.hop_count, 0),
            self.src.to_binary(),
            self.dest.to_binary(),
            struct.KNX_LENGTH.pack(self.payload_length),
            self.payload,
            self.payload_data,
        ))

        return binary


class KnxExtendedTelegram(KnxBaseTelegram):

    def __init__(self, eff=bytes(), payload_length=None, payload=bytes(), *args, **kwargs):
        super(KnxExtendedTelegram, self).__init__(*args, **kwargs)
        self.eff = eff

        if payload_length is not None and not len(payload) == payload_length - 2:
            raise TypeError("Payload length mismatch")

        self.payload = payload
        self.payload_length = payload_length if payload_length is not None else len(payload) - 2

    def __repr__(self):
        eff = hex(self.eff)
        p = self.payload.hex()
        return """KnxExtendedTelegram(src='{src}', dest='{dest}', telegram_type={tt},
    repeat={repeat}, ack={ack}, priority={prio}, hop_count={hop_count}, timestamp='{timestamp}',
    eff=bytes.fromhex('{eff_hex}'), payload_length={payload_length}, payload=bytes.fromhex('{p}'))""".format(tt=repr(self.telegram_type), prio=repr(self.priority), p=p, eff_hex=eff, **self.__dict__)

    def to_binary(self):
        binary = b''.join((
            struct.CEMI_MSG_CODE.pack(0x29),  # cEMI header
            struct.CEMI_ADD_LEN.pack(0),  # no additional cEMI/BAOS info here, since they are not stored in the KNX Datamodel
            struct.KNX_CTRL.pack(int(self.telegram_type), not self.repeat, 3, int(self.priority), not self.ack, not self.confirm),
            struct.KNX_CTRLE.pack(self.dest.group, self.hop_count, self.eff),
            self.src.to_binary(),
            self.dest.to_binary(),
            struct.KNX_LENGTH.pack(self.payload_length),
            self.payload,
        ))

        return binary

class KnxAcknowledgementTelegram(object):

    def __init__(self, acknowledgement=TelegramAcknowledgement.ACK):
        self.acknowledgement = TelegramAcknowledgement(acknowledgement)

    def __repr__(self):
        return """KnxAcknowledgementTelegram(ack='{0}')""".format(repr(self.acknowledgement))