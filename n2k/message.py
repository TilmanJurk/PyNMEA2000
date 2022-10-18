# N2kMsg.h
from typing import List

from n2k.utils import millis, IntRef
from n2k.stream import Stream


N2K_DOUBLE_NAN = -1e9
N2K_FLOAT_NAN  = -1e9
N2K_UINT8_NA   = 0xff
N2K_INT8_NA    = 0x7f
N2K_UINT16_NA  = 0xffff
N2K_INT16_NA   = 0x7fff
N2K_UINT32_NA  = 0xffffffff
N2K_INT32_NA   = 0x7fffffff
N2K_UINT64_NA  = 0xffffffffffffffff
N2K_INT64_NA   = 0x7fffffffffffffff


def n2k_double_is_nan(v: float) -> bool:
    return v == N2K_DOUBLE_NAN


def n2k_float_is_nan(v: float) -> bool:
    return v == N2K_FLOAT_NAN


def n2k_uint8_is_nan(v: float) -> bool:
    return v == N2K_UINT8_NA


def n2k_int8_is_nan(v: float) -> bool:
    return v == N2K_INT8_NA


def n2k_uint16_is_nan(v: float) -> bool:
    return v == N2K_UINT16_NA


def n2k_int16_is_nan(v: float) -> bool:
    return v == N2K_INT16_NA


def n2k_uint32_is_nan(v: float) -> bool:
    return v == N2K_UINT32_NA


def n2k_int32_is_nan(v: float) -> bool:
    return v == N2K_INT32_NA


def n2k_uint64_is_nan(v: float) -> bool:
    return v == N2K_UINT64_NA


def n2k_int64_is_nan(v: float) -> bool:
    return v == N2K_INT64_NA


# TODO: Buffer set functions?
# TODO: Buffer get functions?


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
        if 0 < len(data) < self.max_data_len:
            self.data = data
            self.data_len = len(data)
        # self.tp_message = False
    
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
        return self.max_data_len - len(self.data)
    
    # Data Insertion
    def add_float(self, v: float, undef_val: float = N2K_FLOAT_NAN) -> None:
        print("NotImplemented add_float")
    
    def add_1_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NAN) -> None:
        print("NotImplemented add_1_byte_double")
    
    def add_2_byte_udouble(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NAN) -> None:
        print("NotImplemented add_2_byte_udouble")
    
    def add_2_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NAN) -> None:
        print("NotImplemented add_2_byte_double")

    def add_3_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NAN) -> None:
        print("NotImplemented add_3_byte_double")

    def add_4_byte_udouble(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NAN) -> None:
        print("NotImplemented add_4_byte_udouble")
    
    def add_4_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NAN) -> None:
        print("NotImplemented add_4_byte_double")
    
    def add_8_byte_double(self, v: float, precision: float, undef_val: float = N2K_DOUBLE_NAN) -> None:
        print("NotImplemented add_8_byte_double")
    
    def add_byte(self, v: int) -> None:
        print("NotImplemented add_byte")
    
    def add_2_byte_uint(self, v: int) -> None:
        print("NotImplemented add_2_byte_uint")
    
    def add_2_byte_int(self, v: int) -> None:
        print("NotImplemented add_2_byte_int")
    
    def add_3_byte_int(self, v: int) -> None:
        print("NotImplemented add_3_byte_int")
    
    def add_4_byte_uint(self, v: int) -> None:
        print("NotImplemented add_4_byte_uint")
    
    def add_uint_64(self, v: int) -> None:
        print("NotImplemented add_uint_64")
    
    def add_str(self, v: str) -> None:
        print("NotImplemented add_str")
    
    def add_var_str(self, v: str) -> None:
        print("NotImplemented add_var_str")
    
    def add_buf(self, v: bytearray) -> None:
        print("NotImplemented add_buf")
    
    # Data Retrieval
    def get_float(self, index: IntRef, default: float = N2K_FLOAT_NAN) -> float:
        print("NotImplemented get_float")
    
    def get_1_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NAN) -> float:
        print("NotImplemented get_1_byte_double")
    
    def get_1_byte_udouble(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NAN) -> float:
        print("NotImplemented get_1_byte_udouble")
    
    def get_2_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NAN) -> float:
        print("NotImplemented get_2_byte_double")
    
    def get_2_byte_udouble(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NAN) -> float:
        print("NotImplemented get_2_byte_udouble")
    
    def get_3_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NAN) -> float:
        print("NotImplemented get_3_byte_double")
    
    def get_4_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NAN) -> float:
        print("NotImplemented get_4_byte_double")
    
    def get_4_byte_udouble(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NAN) -> float:
        print("NotImplemented get_4_byte_udouble")
    
    def get_8_byte_double(self, precision: float, index: IntRef, default: float = N2K_DOUBLE_NAN) -> float:
        print("NotImplemented get_8_byte_double")
    
    def get_byte(self, index: IntRef) -> int:
        print("NotImplemented get_byte")
    
    def get_2_byte_int(self, index: IntRef, default: int = N2K_INT16_NA) -> int:
        print("NotImplemented get_2_byte_int")
    
    def get_2_byte_uint(self, index: IntRef, default: int = N2K_UINT16_NA) -> int:
        print("NotImplemented get_2_byte_uint")
    
    def get_3_byte_uint(self, index: IntRef, default: int = N2K_UINT32_NA) -> int:
        print("NotImplemented get_3_byte_uint")
    
    def get_4_byte_uint(self, index: IntRef, default: int = N2K_UINT32_NA) -> int:
        print("NotImplemented get_4_byte_uint")
    
    def get_uint_64(self, index: IntRef, default: int = N2K_UINT64_NA) -> int:
        print("NotImplemented get_uint_64")
    
    def get_str(self, length: int, index: IntRef) -> str:
        print("NotImplemented get_str")
    
    # TODO: second get_str version that writes into a provided buffer of a certain length and either terminates when
    #  the buffer is full or the length of the input has been reached and then fills the rest of the buffer with zeros.
    #  Instead of checking for '@' as the end of string char it checks for the provided char.
    
    def get_var_str(self, index: IntRef) -> str:
        print("NotImplemented get_var_str")
    
    def get_buf(self, length: int, index: IntRef) -> bytearray:
        print("NotImplemented get_buf")
    
    # Data Manipulation
    def set_byte(self, v: int, index: IntRef) -> bool:
        print("NotImplemented set_byte")
    
    def set_2_byte_uint(self, v: int, index: IntRef) -> bool:
        print("NotImplemented set_2_byte_uint")
    
    # Send message?
    def print(self, port: Stream, no_data: bool = False) -> None:
        print("NotImplemented print")
    
    def send_in_actisense_format(self, port: Stream) -> None:
        print("NotImplemented send_in_actisense_format")
    

# TODO: change all the set functions to instead subclass n2kmessage and be the constructor of the
#  corresponding subclass?
#  Or maybe just be class functions? Or static functions that return a message (probably best)

def print_buf(port: Stream, length: int, p_data: str, add_lf: bool = False):
    print("NotImplemented print_buf")
