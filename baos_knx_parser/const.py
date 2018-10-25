from .bitmask import Bitmask, BitmaskEnum


class APCI(BitmaskEnum):
    A_GROUP_VALUE_READ                          = 0b0000000000
    A_GROUP_VALUE_RESPONSE                      = Bitmask(0b0001000000, 0b1111000000)  # last 6 bit not set
    A_GROUP_VALUE_WRITE                         = Bitmask(0b0010000000, 0b1111000000)  # last 6 bit not set

    A_INDIVIDUAL_ADDRESS_WRITE                  = 0b0011000000
    A_INDIVIDUAL_ADDRESS_READ                   = 0b0100000000
    A_INDIVIDUAL_ADDRESS_RESPONSE               = 0b0101000000
    A_INDIVIDUAL_ADDRESS_SERIAL_NUMBER_READ     = 0b1111011100
    A_INDIVIDUAL_ADDRESS_SERIAL_NUMBER_RESPONSE = 0b1111011101
    A_INDIVIDUAL_ADDRESS_SERIAL_NUMBER_WRITE    = 0b1111011110

    A_SERVICE_INFORMATION_INDICATION_WRITE      = 0b1111011111
    A_DOMAIN_ADDRESS_WRITE                      = 0b1111100000
    A_DOMAIN_ADDRESS_READ                       = 0b1111100001
    A_DOMAIN_ADDRESS_RESPONSE                   = 0b1111100010

    A_PROPERTY_VALUE_READ                       = 0b1111010101
    A_PROPERTY_VALUE_RESPONSE                   = 0b1111010110
    A_PROPERTY_VALUE_WRITE                      = 0b1111010111

    A_PROPERTY_DESCRIPTION_READ                 = 0b1111011000
    A_PROPERTY_DESCRIPTION_RESPONSE             = 0b1111011001

    A_USER_MEMORY_READ                          = 0b1011000000
    A_USER_MEMORY_RESPONSE                      = 0b1011000001
    A_USER_MEMORY_WRITE                         = 0b1011000010

    A_USER_MEMORY_BIT_WRITE                     = 0b1011000100

    A_USER_MANUFACTURE_INFO_READ                = 0b1011000101 
    A_USER_MANUFACTURE_INFO_RESPONSE            = 0b1011000110

    A_ADC_READ                                  = Bitmask(0b0110000000, 0b1111000000)  # last 6 bit not set
    A_ADC_RESPONSE                              = Bitmask(0b0111000000, 0b1111000000)  # last 6 bit not set

    A_MEMORY_READ                               = Bitmask(0b1000000000, 0b1111110000)  # last 4 bit not set
    A_MEMORY_RESPONSE                           = Bitmask(0b1001000000, 0b1111110000)  # last 4 bit not set
    A_MEMORY_WRITE                              = Bitmask(0b1010000000, 0b1111110000)  # last 4 bit not set
    A_MEMORY_BIT_WRITE                          = 0b1111010000

    A_DEVICE_DESCRIPTOR_READ                    = 0b1100000000
    A_DEVICE_DESCRIPTOR_RESPONSE                = 0b1101000000

    A_RESTART                                   = 0b1110000000

    A_AUTHORIZE_REQUEST                         = 0b1111010001
    A_AUTHORIZE_RESPONSE                        = 0b1111010010
    A_KEY_WRITE                                 = 0b1111010011
    A_KEY_RESPONSE                              = 0b1111010100

    A_NETWORK_PARAMETER_READ                    = 0b1111011010
    A_NETWORK_PARAMETER_RESPONSE                = 0b1111011011
    A_NETWORK_PARAMETER_WRITE                   = 0b1111100100

    A_LINK_READ                                 = 0b1111100101
    A_LINK_RESPONSE                             = 0b1111100110
    A_LINK_WRITE                                = 0b1111100111

    A_DOMAIN_ADDRESS_SELECTIVE_READ             = 0b1111100011

class TPCI(BitmaskEnum):
    UNNUMBERED_DATA_PACKET       = 0b00
    UNNUMBERED_CONTROL_PACKET    = 0b10
    NUMBERED_DATA_PACKET         = 0b01
    NUMBERED_CONTROL_PACKET      = 0b11


class TelegramType(BitmaskEnum):
    POLL  = 0b11
    ACK   = 0b01
    DATA  = 0b10
    EXT   = 0b00


class TelegramPriority(BitmaskEnum):
    SYSTEM  = 0b00
    URGENT  = 0b10
    NORMAL  = 0b01
    LOW     = 0b11


class TelegramAcknowledgement(BitmaskEnum):
    ACK       = 0b11001100
    BUSY      = 0b11000000
    NACK      = 0b00001100
    NACK_BUSY = 0b00000000
