
from . import struct


def construct_payload(tpci, sequence_number, apci, payload=None):
    binary = struct.KNX_TPCI_APCI.pack(int(tpci), int(sequence_number), int(apci))
    if payload:
        binary += payload

    return binary
