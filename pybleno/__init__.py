from .Bleno import Bleno
from .BlenoPrimaryService import BlenoPrimaryService
from .Characteristic import Characteristic
from .Descriptor import Descriptor
from .hci_socket import *
import array
import struct


def pack_U4LE(value):
    result = struct.pack('<I', value)
    return result


def unpack_U4LE(data):
    result = 0
    for i in reversed(range(0, len(data))):
        result = result << 8 | data[i]
    return result


def number_getter(handler):
    def encoded_handler(*args):
        result = handler(*args)
        encoded_result = array.array('B', pack_U4LE(result))
        return encoded_result

    return encoded_handler


def number_setter(handler):
    def decoded_handler(*args):
        decoded_result = unpack_U4LE(args[-1])
        args_list = list(args)
        args_list = args_list[:-1] + [decoded_result]
        handler(*tuple(args_list))

    return decoded_handler


def string_getter(handler):
    def encoded_handler():
        result = handler() or ''
        if isinstance(result, str):
            encoded_result = result.encode('utf8')
        elif result is not None and not isinstance(result, str):
            raise Exception("Unable to encode value as a string - type was [%s]" % type(result).__name__)
        else:
            encoded_result = array.array('B', [ord(c) for c in result])
        return encoded_result

    return encoded_handler


def string_setter(handler):
    def decoded_handler(*args):
        decoded_result = args[-1].decode("utf-8")
        args_list = list(args)
        args_list = args_list[:-1] + [decoded_result]
        handler(*tuple(args_list))

    return decoded_handler


def bool_getter(handler):
    def encoded_handler(*args):
        result = handler(*args)
        encoded_result = array.array('B', pack_U4LE(1 if result else 0))
        return encoded_result

    return encoded_handler


def bool_setter(handler):
    def decoded_handler(*args):
        decoded_result = True if args[-1][0] else False
        args_list = list(args)
        args_list = args_list[:-1] + [decoded_result]
        handler(*tuple(args_list))

    return decoded_handler


CODEC_STRING = (string_getter, string_setter)
CODEC_NUMBER = (number_getter, number_setter)
CODEC_BOOL = (bool_getter, bool_setter)
