from n2k.message import Message
import n2k


class MessageHandler:
    _node: 'n2k.Node'
    pgn: int

    # def handle_msg(self, n2k_node: N2kNode, msg: N2kMessage) -> None:
    def handle_msg(self, msg: Message) -> None:
        print("NotImplemented handle_msg")

    def __init__(self, pgn: int, node: 'n2k.Node'):
        self._node = node
        self.pgn = pgn

    # TODO how is dropping & unregistering of the handler done?
