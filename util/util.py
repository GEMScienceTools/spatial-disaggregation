# Load dependencies
from _config import *


# Print red text
def print_red(text):
    return print('\033[91m' + text + '\033[0m')


# Print yellow text
def print_yellow(text):
    return print('\x1b[0;40;33m' + text + '\x1b[0m')


# Round to the nearest a (e.g. 0.05)
def round_nearest(x, base=1):
    return round(round(x / base) * base, -int(math.floor(math.log10(base))))
