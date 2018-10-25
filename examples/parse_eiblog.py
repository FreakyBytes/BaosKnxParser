import csv
import binascii
from datetime import datetime
from pprint import pprint

import baos_knx_parser as knx

import numpy as np
import pandas as pd

"""
This example parses the `eiblog.txt` file, takes the BAOS KNX packets and puts
their content into a vector. All data is casted into an int, so it is easier to
deal with them in whatever statistics you want to do.
Reading the entire log into RAM takes a while (a very long while).
Therefore I would advice to shorten the list for testing purposes:

  `head -n 10000 eiblog.txt > eiblog_short.txt`

This command will take the first 10 000 lines and will output them into `eiblog_short.txt`

----

This example requires the additional libraries pandas and numpy
"""


DUMP_FILE = 'eiblog.txt'
TELEGRAM_VECTOR_COLUMNS = ('src', 'dest', 'telegram_type', 'repeat', 'ack',
                           'priority', 'confirm', 'hop_count', 'apci', 'tpci',
                           'packet_number', 'payload_length', 'payload', 'payload_data')


def telegram2vector(telegram):
    return (getattr(telegram, prop) for prop in TELEGRAM_VECTOR_COLUMNS)


# def telegramlist2vectorlist(tlist):
#     for telegram in tlist:
#         yield telegram2vector(telegram)


def read_telegramlog(file):
    with open(file) as tsv:
        for row in csv.reader(tsv, delimiter='\t'):
            timestamp = datetime.strptime(' '.join(row[0:2]), '%H:%M:%S %Y-%m-%d')
            telegram = knx.parse_knx_telegram(bytes.fromhex(row[5]), timestamp)
            yield telegram2vector(telegram)


# reads the eiblog into a Pandas DataFrame
telegram_df = pd.DataFrame(
    data=read_telegramlog(DUMP_FILE),
    columns=TELEGRAM_VECTOR_COLUMNS,
)

print(telegram_df.to_string())
# print(int(telegram_df['payload_data'][0], 16))
# print(telegram_df['payload_data'][0])
