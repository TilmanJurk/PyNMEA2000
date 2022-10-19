from typing import List, Optional

from n2k import N2kCANMessage
from n2k.utils import millis
from n2k.constants import MAX_N2K_MSG_BUF_TIME


class N2kCANMessageBuffer:
    _buffer: List[N2kCANMessage]
    
    def __init__(self, size: int):
        assert size > 0

        self._buffer = []
        for i in range(size):
            self._buffer.append(N2kCANMessage())
    
    def find_free_slot(self, pgn: int = 0, source: int = 0, destination: int = 0,
                       tp_msg: bool = False) -> Optional[N2kCANMessage]:
        cur_time = millis()
        oldest_msg_time = millis()
        oldest_msg: N2kCANMessage = self._buffer[0]
        
        for msg in self._buffer:
            if msg.free_msg or (msg.n2k_msg.pgn == pgn and msg.n2k_msg.source == source and
                                msg.n2k_msg.destination == destination):  # and msg.n2k_msg.tp_message == tp_msg): # TODO: ISO Multipacket
                return msg
            if msg.n2k_msg.msg_time < oldest_msg_time:
                oldest_msg = msg
                oldest_msg_time = msg.n2k_msg.msg_time
        
        if oldest_msg_time + MAX_N2K_MSG_BUF_TIME < cur_time:
            oldest_msg.free_message()
            return oldest_msg

        # TODO: log warning to either increase buffer size or reduce message age grace period
        return None
        
    def find_matching(self, pgn: int, source: int) -> Optional[N2kCANMessage]:
        for msg in self._buffer:
            if msg.n2k_msg.pgn == pgn and msg.n2k_msg.source == source: #  and not msg.n2k_msg.is_tp_message: # TODO: ISO Multicast
                return msg
        return None
