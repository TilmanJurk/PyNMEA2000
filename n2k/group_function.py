# Used for e.g. configuring devices
# https://www.nmea.org/Assets/20140109%20nmea-2000-corrigendum-tc201401031%20pgn%20126208.pdf

from enum import IntEnum

import n2k.node
from n2k.message import Message


class N2kGroupFunctionCode(IntEnum):
    Request = 0
    Command = 1
    Acknowledge = 2
    Read = 3
    ReadReply = 4
    Write = 5
    WriteReply = 6


class N2kGroupFunctionPGNErrorCode(IntEnum):
    Acknowledge = 0
    PGNNotSupported = 1
    PGNTemporarilyNotAvailable = 2
    AccessDenied = 3
    RequestOrCommandNotSupported = 4
    DefinerTagNotSupported = 5
    ReadOrWriteNotSupported = 6


class N2kGroupFunctionTransmissionOrPriorityErrorCode(IntEnum):
    Acknowledge = 0
    TransmitIntervalOrPriorityNotSupported = 1
    TransmitIntervalIsLessThanMeasurementInterval = 2
    AccessDenied = 3
    RequestNotSupported = 4


class N2kGroupFunctionParameterErrorCode(IntEnum):
    Acknowledge = 0
    InvalidRequestOrCommandParameterField = 1
    TemporarilyUnableToComply = 2
    RequestOrCommandParameterOutOfRange = 3
    AccessDenied = 4
    RequestOrCommandNotSupported = 5
    ReadOrWriteIsNotSupported = 6


def match_request_field(field_val, match_val, mask) -> (bool, int):
    if field_val & mask != match_val:
        return False, N2kGroupFunctionParameterErrorCode.RequestOrCommandParameterOutOfRange
    return N2kGroupFunctionParameterErrorCode.Acknowledge


def match_request_field_str(field_val, match_val) -> (bool, int):
    match = field_val == match_val
    if match:
        return True, N2kGroupFunctionParameterErrorCode.Acknowledge
    return False, N2kGroupFunctionParameterErrorCode.RequestOrCommandParameterOutOfRange


class N2kGroupFunctionHandler:
    _pgn: int
    proprietary: bool
    n2k_node: "n2k.node.Node"

    def _get_request_group_function_transmission_or_priority_error_code(self, transmission_interval: int) \
            -> N2kGroupFunctionTransmissionOrPriorityErrorCode:
        raise NotImplementedError()

    def _handle_request(self, msg: Message, transmission_interval: int, transmission_interval_offset: int,
                        number_of_parameter_pairs: int) -> bool:
        raise NotImplementedError()

    def _handle_command(self, msg: Message, priority_setting: int, number_of_parameter_pairs: int) -> bool:
        raise NotImplementedError()

    def _handle_acknowledge(self, msg: Message, pgn_error_code: N2kGroupFunctionPGNErrorCode,
                            transmission_or_priority_error_code: N2kGroupFunctionTransmissionOrPriorityErrorCode,
                            number_of_parameter_pairs: int) -> bool:
        raise NotImplementedError()

    def _handle_read_fields(self, msg: Message, manufacturer_code: int, industry_group: int, unique_id: int,
                            number_of_selection_pairs: int, number_of_parameter_pairs: int) -> bool:
        raise NotImplementedError()

    def _handle_read_fields_reply(self, msg: Message) -> bool:
        raise NotImplementedError()

    def _handle_write_fields(self, msg: Message, manufacturer_code: int, industry_group: int, unique_id: int,
                             number_of_selection_pairs: int, number_of_parameter_pairs: int) -> bool:
        raise NotImplementedError()

    def _handle_write_fields_reply(self, msg: Message) -> bool:
        raise NotImplementedError()

    def __init__(self, n2k_node: "n2k.node.Node", pgn: int):
        self.n2k_node = n2k_node
        self._pgn = pgn

    def handle(self, msg: Message, group_function_code: N2kGroupFunctionCode, pgn_for_group_function: int) -> bool:
        raise NotImplementedError()


def get_pgn_for_group_function(msg: Message) -> int:
    raise NotImplementedError()


def parse(msg: Message, group_function_code, pgn_for_group_function) -> bool:
    raise NotImplementedError()


def parse_request_params(msg: Message, transmission_interval: int, transmission_interval_offset: int,
                         number_of_parameter_pairs: int) -> bool:
    raise NotImplementedError()


def start_parse_request_pair_parameters(msg: Message, index: int) -> bool:
    raise NotImplementedError()


def parse_command_params(msg: Message, priority_setting: int, number_of_parameter_pairs: int) -> bool:
    raise NotImplementedError()


def start_parse_command_pair_parameters(msg: Message, index: int) -> bool:
    raise NotImplementedError()


def parse_acknowledge_params(msg: Message, pgn_error_code: N2kGroupFunctionPGNErrorCode,
                             transmission_or_priority_error_code: N2kGroupFunctionTransmissionOrPriorityErrorCode,
                             number_of_parameter_pairs: int) -> bool:
    raise NotImplementedError()


def start_parse_read_or_write_parameters(msg: Message, index: int) -> bool:
    raise NotImplementedError()


def parse_read_or_write_params(msg: Message, manufacturer_code: int, industry_group: int, unique_id: int,
                               number_of_selection_pairs: int, number_of_parameter_pairs: int,
                               proprietary: bool = False) -> bool:
    raise NotImplementedError()


def set_start_read_reply(msg: Message, destination: int, pgn: int, manufacturer_code: int, industry_group: int,
                         unique_id: int, number_of_selection_pairs: int, number_of_parameter_pairs: int,
                         proprietary: bool) -> None:
    raise NotImplementedError()


def set_start_write_reply(msg: Message, destination: int, pgn: int, manufacturer_code: int, industry_group: int,
                          unique_id: int, number_of_selection_pairs: int, number_of_parameter_pairs: int,
                          proprietary: bool) -> None:
    raise NotImplementedError()


def set_start_acknowledge(msg: Message, destination: int, pgn: int, pgn_error_code: N2kGroupFunctionPGNErrorCode,
                          transmission_or_priority_error_code: N2kGroupFunctionTransmissionOrPriorityErrorCode,
                          number_of_parameter_pairs: int = 0) -> None:
    raise NotImplementedError()


def change_pgn_error_code(msg: Message, pgn_error_code: N2kGroupFunctionPGNErrorCode) -> None:
    raise NotImplementedError()


def change_transmission_or_priority_error_code(msg: Message,
                                               transmission_or_priority_error_code: N2kGroupFunctionTransmissionOrPriorityErrorCode) -> None:
    raise NotImplementedError()


def add_acknowledge_parameter(msg: Message, parameter_pair_index: int,
                              error_code: N2kGroupFunctionParameterErrorCode = N2kGroupFunctionParameterErrorCode.ReadOrWriteIsNotSupported) -> None:
    raise NotImplementedError()


def send_acknowledge(node: "n2k.node.Node", destination: int, pgn: int, pgn_error_code: N2kGroupFunctionPGNErrorCode,
                     transmission_or_priority_error_code: N2kGroupFunctionTransmissionOrPriorityErrorCode,
                     number_of_parameter_pairs: int = 0,
                     parameter_error_code_for_all: N2kGroupFunctionParameterErrorCode = N2kGroupFunctionParameterErrorCode.Acknowledge) -> None:
    raise NotImplementedError()
