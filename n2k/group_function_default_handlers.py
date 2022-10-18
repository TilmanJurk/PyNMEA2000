from n2k.group_function import N2kGroupFunctionHandler
import n2k.node
from n2k.message import Message


class N2kGroupFunctionHandlerForPGN60928(N2kGroupFunctionHandler):
    def _handle_request(self, msg: Message, transmission_interval: int, transmission_interval_offset: int,
                        number_of_parameter_pairs: int) -> bool:
        print("NotImplemented _handle_request")

    def _handle_command(self, msg: Message, priority_setting: int, number_of_parameter_pairs: int) -> bool:
        print("NotImplemented _handle_command")

    def __init__(self, n2k_node: n2k.node.Node):
        super().__init__(n2k_node, 60928)


class N2kGroupFunctionHandlerForPGN126464(N2kGroupFunctionHandler):
    def _handle_request(self, msg: Message, transmission_interval: int, transmission_interval_offset: int,
                        number_of_parameter_pairs: int) -> bool:
        print("NotImplemented _handle_request")

    def __init__(self, n2k_node: n2k.node.Node):
        super().__init__(n2k_node, 126464)


class N2kGroupFunctionHandlerForPGN126993(N2kGroupFunctionHandler):
    def _handle_request(self, msg: Message, transmission_interval: int, transmission_interval_offset: int,
                        number_of_parameter_pairs: int) -> bool:
        print("NotImplemented _handle_request")

    def __init__(self, n2k_node: n2k.node.Node):
        super().__init__(n2k_node, 126993)


class N2kGroupFunctionHandlerForPGN126996(N2kGroupFunctionHandler):
    def _handle_request(self, msg: Message, transmission_interval: int, transmission_interval_offset: int,
                        number_of_parameter_pairs: int) -> bool:
        print("NotImplemented _handle_request")

    def __init__(self, n2k_node: n2k.node.Node):
        super().__init__(n2k_node, 126996)


class N2kGroupFunctionHandlerForPGN126998(N2kGroupFunctionHandler):
    def _handle_request(self, msg: Message, transmission_interval: int, transmission_interval_offset: int,
                        number_of_parameter_pairs: int) -> bool:
        print("NotImplemented _handle_request")

    def _handle_command(self, msg: Message, priority_setting: int, number_of_parameter_pairs: int) -> bool:
        print("NotImplemented _handle_command")

    def __init__(self, n2k_node: n2k.node.Node):
        super().__init__(n2k_node, 126998)

