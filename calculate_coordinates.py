import re

def parse_dms_string(dms_string):
    matches = re.findall(r'(\d+)°(\d+)[\'’](\d+(?:\.\d+)?)["”]?([NSEW])', dms_string)
    decimals = []
    for deg, min_, sec, dir_ in matches:
        decimal = dms_to_decimal(int(deg), int(min_), float(sec), dir_)
        decimals.append(decimal)
    return decimals

def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal