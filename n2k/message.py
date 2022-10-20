# N2kMsg.h
from typing import List, Optional
import struct
from binascii import hexlify

from n2k.n2k import PGN
from n2k.utils import millis, IntRef, clamp_int
from n2k.stream import Stream
from n2k.constants import *


def n2k_double_is_na(v: float) -> bool:
    return v == N2K_DOUBLE_NA


def n2k_float_is_na(v: float) -> bool:
    return v == N2K_FLOAT_NA


def n2k_uint8_is_na(v: float) -> bool:
    return v == N2K_UINT8_NA


def n2k_int8_is_na(v: float) -> bool:
    return v == N2K_INT8_NA


def n2k_uint16_is_na(v: float) -> bool:
    return v == N2K_UINT16_NA


def n2k_int16_is_na(v: float) -> bool:
    return v == N2K_INT16_NA


def n2k_uint32_is_na(v: float) -> bool:
    return v == N2K_UINT32_NA


def n2k_int32_is_na(v: float) -> bool:
    return v == N2K_INT32_NA


def n2k_uint64_is_na(v: float) -> bool:
    return v == N2K_UINT64_NA


def n2k_int64_is_na(v: float) -> bool:
    return v == N2K_INT64_NA


# TODO: Buffer set functions?
# TODO: Buffer get functions?


# WARNING: The round method employed by python differs from the one written in the ported C code
#  However this is the correct method for IEEE floating point numbers
#  https://en.wikipedia.org/wiki/Rounding#Round_half_to_even
class Message:
    # subclassed for each pgn; maybe use typed & named tuple or something else instead?
    max_data_len: int = 223
    priority: int
    pgn: int = 0  # unsigned long: 4 bytes
    source: int
    destination: int
    data: bytearray
    data_len: int
    msg_time: int = 0
    # ISO Multi Packet Support
    # tp_message: bool
    
    def __init__(self, source: int = 15, priority: int = 6, pgn: int = 0, data: bytearray = bytearray()) -> None:
        self.source = source
        self.destination = 255
        self.priority = priority & 0x7
        self.pgn = pgn
        self.msg_time = millis()
        self.data = data[:self.max_data_len]
        self.data_len = len(data)
        # self.tp_message = False

    def __repr__(self):
        s = "Message("
        s += "source=" + str(self.source) + ","
        s += "destination=" + str(self.destination) + ","
        s += "priority=" + str(self.priority) + ","

        pgn = self.pgn
        try:
            pgn = PGN(pgn)
        except ValueError:
            pass

        s += "pgn=" + str(pgn) + ","
        s += "msg_time=" + str(self.msg_time) + ","
        s += "data=" + str(hexlify(self.data)) + ","
        s += "data_len=" + str(self.data_len) + ","
        return s

    def check_destination(self) -> None:
        """
        Verify the destination, as only PGNs where the lower byte is 0 can be sent to specific addresses.
        :return:
        """
        if self.pgn & 0xff != 0:
            # set destination to broadcast
            self.destination = 0xff
    
    def is_valid(self) -> bool:
        return self.pgn != 0 and len(self.data) > 0
    
    def get_remaining_data_length(self, index: int) -> int:
        if len(self.data) > index:
            return len(self.data) - index
        return 0
    
    def get_available_data_length(self):
        return max(0, self.max_data_len - len(self.data))
    
    # Data Insertion
    def add_float(self, v: float, undef_val: float = N2K_FLOAT_NA) -> None:
        if v != undef_val:
            self.data.extend(struct.pack("<f", v))
        else:
            self.data.extend(struct.pack("<i", N2K_INT32_NA))
        self.data_len += 4

    def add_1_byte_udouble(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NA) -> None:
        if v != undef_val:
            v = clamp_int(0, round(v / precision), N2K_UINT8_OR)
            self.data.extend(struct.pack("<B", v))
        else:
            self.data.extend(struct.pack("<B", N2K_UINT8_NA))
        self.data_len += 1

    def add_1_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NA) -> None:
        if v != undef_val:
            v = clamp_int(N2K_INT8_MIN, round(v / precision), N2K_INT8_OR)
            self.data.extend(struct.pack("<b", v))
        else:
            self.data.extend(struct.pack("<b", N2K_INT8_NA))
        self.data_len += 1

    def add_2_byte_udouble(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NA) -> None:
        if v != undef_val:
            v = clamp_int(0, round(v / precision), N2K_UINT16_OR)
            self.data.extend(struct.pack("<H", v))
        else:
            self.data.extend(struct.pack("<H", N2K_UINT16_NA))
        self.data_len += 2

    def add_2_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NA) -> None:
        if v != undef_val:
            v = clamp_int(N2K_INT16_MIN, round(v / precision), N2K_INT16_OR)
            self.data.extend(struct.pack("<h", v))
        else:
            self.data.extend(struct.pack("<h", N2K_INT16_NA))
        self.data_len += 2

    def add_3_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NA) -> None:
        if v != undef_val:
            v = clamp_int(N2K_INT24_MIN, round(v / precision), N2K_INT24_OR)
            self.data.extend(struct.pack("<i", v)[:3])
        else:
            self.data.extend(struct.pack("<i", N2K_INT24_NA)[:3])
        self.data_len += 3

    def add_4_byte_udouble(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NA) -> None:
        if v != undef_val:
            v = clamp_int(0, round(v / precision), N2K_UINT32_OR)
            self.data.extend(struct.pack("<I", v))
        else:
            self.data.extend(struct.pack("<I", N2K_UINT32_NA))
        self.data_len += 4

    def add_4_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NA) -> None:
        if v != undef_val:
            v = clamp_int(N2K_INT32_MIN, round(v / precision), N2K_INT32_OR)
            self.data.extend(struct.pack("<i", v))
        else:
            self.data.extend(struct.pack("<i", N2K_INT32_NA))
        self.data_len += 4

    def add_8_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NA) -> None:
        if v != undef_val:
            self.data.extend(struct.pack("<q", int(v/precision)))
        else:
            self.data.extend(struct.pack("<q", N2K_INT64_NA))
        self.data_len += 8

    def add_byte_uint(self, v: int) -> None:
        self.data.extend(struct.pack("<B", v))
        self.data_len += 1

    def add_byte_int(self, v: int) -> None:
        self.data.extend(struct.pack("<b", v))
        self.data_len += 1

    def add_2_byte_uint(self, v: int) -> None:
        self.data.extend(struct.pack("<H", v))
        self.data_len += 2
    
    def add_2_byte_int(self, v: int) -> None:
        self.data.extend(struct.pack("<h", v))
        self.data_len += 2
    
    def add_3_byte_int(self, v: int) -> None:
        self.data.extend(struct.pack("<i", v)[:3])
        self.data_len += 3
    
    def add_4_byte_uint(self, v: int) -> None:
        self.data.extend(struct.pack("<I", v))
        self.data_len += 4
    
    def add_uint_64(self, v: int) -> None:
        self.data.extend(struct.pack("<Q", v))
        self.data_len += 8
    
    def add_str(self, v: str, length: int) -> None:
        encoded = v.encode("utf-8")[:length]
        for b in encoded:
            self.add_byte_uint(b)
        # fill up to length using 0xff
        for b in range(length - len(encoded)):
            self.add_byte_uint(0xff)
    
    def add_var_str(self, v: str) -> None:
        self.add_byte_uint(len(v) + 2)
        self.add_byte_uint(1)
        self.add_str(v, len(v))

    def add_buf(self, v: bytearray) -> None:
        v = bytearray[:self.get_available_data_length()]
        for b in v:
            self.add_byte_uint(b)

    # Data Retrieval
    def get_float(self, index: IntRef, default: float = N2K_FLOAT_NA) -> float:
        length = 4
        if index.value + length > self.data_len:
            return default
        if struct.unpack("<i", self.data[index.value:index.value + length])[0] == N2K_INT32_NA:
            index.value += length
            return default
        v = struct.unpack("<f", self.data[index.value:index.value + length])[0]
        index.value += length
        return v
    
    def get_1_byte_udouble(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NA) -> float:
        v = self.get_byte_uint(index)
        if v == N2K_UINT8_NA:
            return default
        return v * precision

    def get_1_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NA) -> float:
        v = self.get_byte_int(index)
        if v == N2K_INT8_NA:
            return default
        return v * precision

    def get_2_byte_udouble(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NA) -> float:
        v = self.get_2_byte_uint(index)
        if v == N2K_UINT16_NA:
            return default
        return v * precision

    def get_2_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NA) -> float:
        v = self.get_2_byte_int(index)
        if v == N2K_INT16_NA:
            return default
        return v * precision

    def get_3_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NA) -> float:
        v = self.get_3_byte_int(index)
        if v == N2K_INT24_NA:
            return default
        return v * precision

    def get_4_byte_udouble(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NA) -> float:
        v = self.get_4_byte_uint(index)
        if v == N2K_UINT32_NA:
            return default
        return v * precision

    def get_4_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NA) -> float:
        v = self.get_4_byte_int(index)
        if v == N2K_INT32_NA:
            return default
        return v * precision

    def get_8_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NA) -> float:
        v = self.get_8_byte_int(index)
        if v == N2K_INT64_NA:
            return default
        return v * precision

    def get_byte_uint(self, index: IntRef) -> int:
        length = 1
        if index.value + length > self.data_len:
            return N2K_UINT8_NA
        v = struct.unpack("<B", self.data[index.value:index.value + length])[0]
        index.value += length
        return v

    def get_byte_int(self, index: IntRef) -> int:
        length = 1
        if index.value + length > self.data_len:
            return N2K_INT8_NA
        v = struct.unpack("<b", self.data[index.value:index.value+length])[0]
        index.value += length
        return v

    def get_2_byte_uint(self, index: IntRef, default: int = N2K_UINT16_NA) -> int:
        length = 2
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<H", self.data[index.value:index.value + length])[0]
        index.value += length
        return v

    def get_2_byte_int(self, index: IntRef, default: int = N2K_INT16_NA) -> int:
        length = 2
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<h", self.data[index.value:index.value + length])[0]
        index.value += length
        return v

    def get_3_byte_uint(self, index: IntRef, default: int = N2K_UINT24_NA) -> int:
        length = 3
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<I", self.data[index.value:index.value + length]+b'\x00')[0]
        index.value += length
        return v

    def get_3_byte_int(self, index: IntRef, default: int = N2K_INT24_NA) -> int:
        length = 3
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<i", self.data[index.value:index.value + length]+b'\x00')[0]
        index.value += length
        return v
    
    def get_4_byte_uint(self, index: IntRef, default: int = N2K_UINT32_NA) -> int:
        length = 4
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<I", self.data[index.value:index.value + length])[0]
        index.value += length
        return v

    def get_4_byte_int(self, index: IntRef, default: int = N2K_UINT32_NA) -> int:
        length = 4
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<i", self.data[index.value:index.value + length])[0]
        index.value += length
        return v
    
    def get_uint_64(self, index: IntRef, default: int = N2K_UINT64_NA) -> int:
        length = 8
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<Q", self.data[index.value:index.value + length])[0]
        index.value += length
        return v

    def get_8_byte_int(self, index: IntRef, default: int = N2K_INT64_NA) -> int:
        length = 8
        if index.value + length > self.data_len:
            return default
        v = struct.unpack("<q", self.data[index.value:index.value + length])[0]
        index.value += length
        return v

    def get_str(self, length: int, index: IntRef, nul_char: bytes = b'@') -> str:
        # TODO: original function fills the end of the buffer (that the string is copied to) with zeros
        #  or at least with 2 zeros, depending on version
        ret = bytearray()
        if index.value + length > self.data_len:
            return ret.decode("utf-8")
        i = -1
        for i in range(length):
            b = self.get_byte_uint(index)
            if b == 0x00 or b == ord(nul_char):
                # either null terminator or custom nul char (e.g. '@' for AIS)
                break
            ret.append(b)
        # ensure that the index gets advanced to correct amount, even if we find the null byte early
        index.value += length - (i + 1)
        return ret.decode("utf-8")
    
    def get_var_str(self, index: IntRef) -> Optional[str]:
        length = self.get_byte_uint(index) - 2
        str_type = self.get_byte_uint(index)
        if str_type != 0x01:
            return None
        return self.get_str(length, index, b'\xff')
    
    def get_buf(self, length: int, index: IntRef) -> bytearray:
        print("NotImplemented get_buf")
    
    # Data Manipulation
    def set_byte_uint(self, v: int, index: IntRef) -> bool:
        if index.value < self.data_len:
            self.data[index.value] = struct.pack("<B", v)[0]
            index.value += 1
            return True
        return False
    
    def set_2_byte_uint(self, v: int, index: IntRef) -> bool:
        if index.value + 1 < self.data_len:
            self.data[index.value:index.value+1] = struct.pack("<H", v)[0]
            index.value += 2
            return True
        return False
    

# TODO: change all the set functions to instead subclass n2kmessage and be the constructor of the
#  corresponding subclass?
#  Or maybe just be class functions? Or static functions that return a message (probably best)

def print_buf(port: Stream, length: int, p_data: str, add_lf: bool = False):
    print("NotImplemented print_buf")
