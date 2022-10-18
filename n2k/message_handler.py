from n2k.message import Message


class MessageHandler:
    # __n2k_node: N2kNode
    pgn: int

    # def handle_msg(self, n2k_node: N2kNode, msg: N2kMessage) -> None:
    def handle_msg(self, msg: Message) -> None:
        raise NotImplementedError()

    def __init__(self, pgn: int) -> 'MessageHandler':
        self.pgn = pgn

    # TODO how is dropping & unregistering of the handler done?
