# convert can message to usable format somehow
# e.g. by converting id
from typing import NamedTuple


class MsgHeader(NamedTuple):
    source: int
    priority: int
    destination: int
    pgn: int


def can_id_to_n2k(can_id: int) -> MsgHeader:
    can_id_pf = (can_id >> 16) & 0xff
    can_id_ps = (can_id >> 8) & 0xff
    can_id_dp = (can_id >> 24) & 1
    
    src = (can_id >> 0) & 0xff
    prio = (can_id >> 26) & 0x7
    
    if can_id_pf < 240:
        # PDU1 format, the PS contains the destination address
        dst = can_id_ps
        pgn = (can_id_dp << 16) | (can_id_pf << 8)
    else:
        # PDU2 format, the destination is implied global and the PGN is extended
        dst = 0xff
        pgn = (can_id_dp << 16) | (can_id_pf << 8) | can_id_ps
        
    return MsgHeader(source=src, priority=prio, destination=dst, pgn=pgn)


def n2k_id_to_can(priority: int, pgn: int, source: int, destination: int) -> int:
    priority = priority & 0xff
    pgn = pgn & 0xffffffff
    source = source & 0xffffffff
    destination = destination & 0xff
    
    can_id_pf = (pgn >> 8) & 0xff
    
    if can_id_pf < 240:
        # PDU1 format
        if pgn & 0xff != 0:
            # for PDU1 format, the lowest byte of the PGN has to be 0, to leave space for the destination
            return 0
        return (priority & 0x7) << 26 | pgn << 8 | destination << 8 | source
    else:
        # PDU2 format
        return (priority & 0x7) << 26 | pgn << 8 | source
    
