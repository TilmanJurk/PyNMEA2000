from n2k.message import Message


class N2kCANMessage:
    n2k_msg: Message
    ready: bool = False
    free_msg: bool = True
    system_message: bool = False
    known_message: bool = False
    # ISO Multi Packet Support
    # tp_required_cts: int = False  # =0 no, n=after each n frames
    # tp_max_packets: int = 0  # =0 not TP message. >0 number of packets can be received.
    last_frame: int  # Last received frame sequence number on fast packets or multi packet
    copied_len: int

    def __init__(self):
        self.n2k_msg = Message()

    def free_message(self) -> None:
        self.free_msg = True
        self.ready = False
        self.system_message = False
        self.known_message = False
        # self.tp_required_cts = False
        # self.tp_max_packets = 0
        self.n2k_msg = Message()
