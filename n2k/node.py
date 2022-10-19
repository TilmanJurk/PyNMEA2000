from collections import deque

import can
from typing import Optional, List, Callable, Set, Deque

from n2k import DeviceList
from n2k.can_message_buffer import N2kCANMessageBuffer
from n2k.can_tools import can_id_to_n2k, n2k_id_to_can
from n2k.device_information import DeviceInformation
from n2k.message import Message
from n2k.message_handler import MessageHandler
from n2k.can_message import N2kCANMessage
from n2k.messages import set_n2k_iso_address_claim, parse_n2k_pgn_iso_request, set_n2k_pgn_iso_acknowledgement, \
    set_n2k_product_information, set_n2k_configuration_information
from n2k.n2k import is_fast_packet_first_frame, DefaultTransmitMessages, DefaultReceiveMessages, \
    is_default_single_frame_message, is_mandatory_fast_packet_message, is_default_fast_packet_message, \
    is_fast_packet_system_message, is_single_frame_system_message, is_proprietary_fast_packet_message, PGN, is_broadcast
from n2k.types import ProductInformation, CANSendFrame, ConfigurationInformation, N2kPGNList
from n2k.utils import millis, IntRef
from n2k.constants import *


class Node(can.Listener):
    # Connect to CAN Bus via python-can
    # Listen to messages and automatically respond to
    #  - Address claim
    #  - what else?
    # Automatically send heartbeat
    # Provide easy option to let device be configured by nmea2000 mfd
    # Send messages
    # Add callbacks by message types
    
    # MsgHandler Class?
    
    # Ignored
    # - ForwardType
    # - N2kMode
    # - DebugMode
    # - Internal Device (why necessary?; maybe to have multiple devices operate via the same library instance?)
    
    ### Start Internal Device ###
    # TODO: Default values - change to sensible values
    n2k_source: int = 0  # uint8_t
    device_information: DeviceInformation
    product_information: ProductInformation = ProductInformation(2101, 666, "", "", "", "", 0, 1)
    manufacturer_serial_code: str = ""
    pending_iso_address_claim: Optional[int] = None  # unsigned long
    pending_product_information: Optional[int] = None  # unsigned long
    pending_configuration_information: Optional[int] = None  # unsigned long
    address_claim_started: int = 0  # unsigned long
    address_claim_end_source: int = N2K_MAX_CAN_BUS_ADDRESS  # uint8_t
    
    transmit_messages: List[int]
    receive_messages: List[int]
    
    max_pgn_sequence_counters: int = 0  # size_t
    pgn_sequence_counters: List[int] = None  # unsigned long | array pointer?
    
    # ISO Multi Packet Support
    # pending_tp_msg: N2kMessage
    # next_dt_send_time: int = 0  # Time, when next data packet can be sent on TP broadcast
    # next_dt_sequence: int = 0  # uint8_t
    
    # Heartbeat
    heartbeat_interval: int
    default_heartbeat_interval: int
    next_heartbeat_send_time: int
    
    def set_pending_iso_address_claim(self, from_now: int = 2) -> None:
        self.pending_iso_address_claim = millis() + from_now
    
    def clear_pending_iso_address_claim(self) -> None:
        self.pending_iso_address_claim = None
    
    def query_pending_iso_address_claim(self) -> bool:
        if self.pending_iso_address_claim is not None:
            return self.pending_iso_address_claim < millis()
        return False
    
    def set_pending_product_information(self) -> None:
        self.pending_product_information = millis() + 187 + self.n2k_source * 8  # TODO: investigate weird offsets
    
    def clear_pending_product_information(self) -> None:
        self.pending_product_information = None
    
    def query_pending_product_information(self) -> bool:
        if self.pending_product_information is not None:
            return self.pending_product_information < millis()
        return False
    
    def set_pending_configuration_information(self) -> None:
        self.pending_configuration_information = millis() + 187 + self.n2k_source * 10
    
    def clear_pending_configuration_information(self) -> None:
        self.pending_configuration_information = None
    
    def query_pending_configuration_information(self) -> bool:
        if self.pending_configuration_information is not None:
            return self.pending_configuration_information < millis()
        return False
    
    def update_address_claim_end_source(self) -> None:
        self.address_claim_end_source = self.n2k_source
        if self.address_claim_end_source > 0:
            self.address_claim_end_source -= 1
        else:
            self.address_claim_end_source = N2K_MAX_CAN_BUS_ADDRESS
    
    ### End Internal Device ###
    
    bus: can.BusABC
    device_list: DeviceList
    can_msg_buffer: N2kCANMessageBuffer
    
    def __init__(self, bus: can.BusABC, can_msg_buffer_size=20):
        super().__init__()
        self.bus = bus
        self.device_list = DeviceList(self)
        self.message_handlers = set()
        self.message_handlers.add(self.device_list)
        self.can_msg_buffer = N2kCANMessageBuffer(can_msg_buffer_size)
        self._can_send_frame_buf = deque()
        
        self.transmit_messages = []
        self.receive_messages = []

        self._start_address_claim()
    
    def on_message_received(self, msg: can.Message) -> None:
        msg_header = can_id_to_n2k(msg.arbitration_id)
        print(msg_header)

        # TODO: refactor, split into multiple functions
        
        # TODO: handle multi frame messages; NMEA2000.cpp:1626-1694
        # TODO: iso multi packet support
        # if self._test_handle_tp_message(msg_header.pgn, msg_header.source, msg_header.destination, len(msg_header.data)):
        if True:
            known_message, system_message, fast_packet = self._check_known_message(msg_header.pgn)
            # TODO: assert msg.data is not empty
            assert msg.data is not None
            if not fast_packet or is_fast_packet_first_frame(msg.data[0]):
                # This is the first frame of a message
                # Find free Slot to store the CAN Msg
                n2k_can_msg = self.can_msg_buffer.find_free_slot()
                if n2k_can_msg is not None:
                    n2k_can_msg.free_msg = False
                    n2k_can_msg.n2k_msg.priority = msg_header.priority
                    n2k_can_msg.n2k_msg.pgn = msg_header.pgn
                    n2k_can_msg.n2k_msg.source = msg_header.source
                    n2k_can_msg.n2k_msg.destination = msg_header.destination
                    n2k_can_msg.known_message = known_message
                    n2k_can_msg.system_message = system_message
                    # n2k_can_msg.n2k_msg.tp_message = False
                    n2k_can_msg.copied_len = 0
                    if fast_packet:
                        # First Frame
                        n2k_can_msg.n2k_msg.data = msg.data[2:msg.dlc]
                        n2k_can_msg.last_frame = msg.data[0]
                        n2k_can_msg.n2k_msg.data_len = msg.data[1]
                    else:
                        # Single Frame Message
                        n2k_can_msg.n2k_msg.data = msg.data[0:msg.dlc]
                        n2k_can_msg.last_frame = 0
                        n2k_can_msg.n2k_msg.data_len = msg.dlc
            else:
                # This is not the first frame of a fast_packet, therefore we have to find the previous frames
                n2k_can_msg = self.can_msg_buffer.find_matching(pgn=msg_header.pgn, source=msg_header.source)
                if n2k_can_msg is not None:
                    if n2k_can_msg.last_frame + 1 == msg.data[0]:
                        # This is the next message in the sequence
                        n2k_can_msg.last_frame = msg.data[0]
                        n2k_can_msg.n2k_msg.data.append(msg.data[1:])
                        if len(n2k_can_msg.n2k_msg.data) > n2k_can_msg.n2k_msg.max_data_len:
                            # Malformed message, TODO: log warning
                            n2k_can_msg.n2k_msg.data = n2k_can_msg.n2k_msg.data[:n2k_can_msg.n2k_msg.max_data_len]
                        if len(n2k_can_msg.n2k_msg.data) > n2k_can_msg.n2k_msg.data_len:
                            # Malformed message, TODO: log warning
                            pass
                    else:
                        # Sequence number doesn't match up, meaning that a frame has been lost
                        # Free the message, we can't use it anymore
                        n2k_can_msg.free_message()
                        n2k_can_msg = None
                else:
                    # Orphan frame, TODO: log
                    pass
        
        if n2k_can_msg is not None:
            n2k_can_msg.ready = len(n2k_can_msg.n2k_msg.data) >= n2k_can_msg.n2k_msg.data_len
            if n2k_can_msg.ready:
                self._handle_received_system_message(n2k_can_msg)
                for handler in self.message_handlers:
                    if handler.pgn == 0 or handler.pgn == n2k_can_msg.n2k_msg.pgn:
                        handler.handle_msg(n2k_can_msg.n2k_msg)
                n2k_can_msg.free_message()
    
    def on_error(self, exc: Exception) -> None:
        # TODO
        print(exc)
    
    def set_product_information(self, name: str, firmware_version: str, model_version: str, model_serial_code: str,
                                load_equivalency: int = 1, certification_level: int = 0,
                                product_code: int = 666) -> None:
        """
        Set the product information. This will be visible in e.g. multi function displays when viewing the device list.
        All strings have a maximum length of :py:const:`MAX_N2K_PRODUCT_INFO_STR_LEN`
        
        :param name: The Name / Model ID
        :param firmware_version: The Firmware Version
        :param model_version: The Model Version / Revision, e.g. '1.0'
        :param model_serial_code: The Model Serial Number
        :param load_equivalency: The Load Equivalency Number specifies the power draw of the device.
               To get it simply take the estimated current draw in mA and divide it by 50 (and round up)
        :param certification_level:
        :param product_code: The Product Code granted by the NMEA. Using 666 by default for Open Source projects.
        """
        self.product_information = ProductInformation(
            n2k_version=2101,
            product_code=product_code,
            n2k_model_id=name[:MAX_N2K_MODEL_ID_LEN],
            n2k_sw_code=firmware_version[:MAX_N2K_SW_CODE_LEN],
            n2k_model_version=model_version[:MAX_N2K_MODEL_VERSION_LEN],
            n2k_model_serial_code=model_serial_code[:MAX_N2K_MODEL_SERIAL_CODE_LEN],
            certification_level=certification_level,
            load_equivalency=load_equivalency,
        )
    
    def set_configuration_information(self,
                                      manufacturer_information: str = "NMEA2000 Library "
                                                                      "https://github.com/finnboeger/NMEA2000",
                                      installation_description1: str = "",
                                      installation_description2: str = "") -> None:
        """
        Set the configuration Information.
        All strings have a maximum length of :py:const:`Max_N2K_CONFIGURATION_INFO_FIELD_LEN`
        
        :param manufacturer_information:
        :param installation_description1:
        :param installation_description2:
        """
        self.configuration_information = ConfigurationInformation(
            manufacturer_information=manufacturer_information[:Max_N2K_CONFIGURATION_INFO_FIELD_LEN],
            installation_description1=installation_description1[:Max_N2K_CONFIGURATION_INFO_FIELD_LEN],
            installation_description2=installation_description2[:Max_N2K_CONFIGURATION_INFO_FIELD_LEN]
        )
    
    def set_device_information(self, unique_number: int, device_function: int = 130, device_class: int = 25,
                               manufacturer_code: int = 2046) -> None:
        """
        Set the device information.
        
        :param unique_number: 21bit large number (max. 2097151), each device from the same manufacturer should have
                              a different unique number
        :param device_function: Defaults to 130 (with Device Class: 25 => PC Gateway). `Device Codes can be found here
               <https://www.nmea.org/Assets/20120726%20nmea%202000%20class%20&%20function%20codes%20v%202.00.pdf>`_
        :param device_class: Defaults to 25 (Inter-/Intranet Device). See above for codes.
        :param manufacturer_code: Maximum of 2046. Has to be bought from the NMEA. `List of registered codes
               <https://www.nmea.org/Assets/20121020%20nmea%202000%20registration%20list.pdf>`_
        """
        self.device_information = DeviceInformation()
        self.device_information.unique_number = unique_number
        self.device_information.manufacturer_code = manufacturer_code
        self.device_information.device_function = device_function
        self.device_information.device_class = device_class
        """
        1 - On-Highway Equipment\n
        2 - Agricultural and Forestry Equipment\n
        3 - Construction Equipment\n
        4 - Marine Equipment\n
        5 - Industrial, Process Control, Stationary Equipment\n
        """
        self.device_information.industry_group = 4
        # TODO: device_instance, system_instance
    
    message_handlers: Set[MessageHandler]
    address_changed_callback: Callable[['Node'], None]
    device_information_changed_callback: Callable[['Node'], None]
    address_changed: bool = False
    device_information_changed: bool = False
    
    # Configuration Information
    configuration_information: ConfigurationInformation = ConfigurationInformation("", "", "")
    
    custom_single_frame_messages: Optional[List[int]] = None
    custom_fast_packet_messages: Optional[List[int]] = None
    
    # buffer for received messages
    _n2k_can_msg_buf: List[Message] # TODO: init if we keep it
    _max_n2k_can_msgs: int  # uint8_t
    
    _can_send_frame_buf: Deque[can.message.Message]
    _max_can_send_frames: int = 40
    _can_send_frame_buffer_write: int  # uint16_t
    _can_send_frame_buffer_read: int  # uint16_t
    _max_can_receive_frames: int  # uint16_t
    
    # TODO: Message Handler for normal messages
    # TODO: Message Handler for request messages
    _request_handler: Optional[Callable[[int, int], bool]]
    
    # TODO: Message Handler for group functions
    
    def _send_frames(self) -> bool:
        while len(self._can_send_frame_buf) > 0:
            can_msg = self._can_send_frame_buf.popleft()
            if not self._send_frame(can_msg.arbitration_id, can_msg.dlc, can_msg.data):
                return False
        return True
    
    def _send_frame(self, frame_id: int, length: int, buf: bytearray) -> bool:
        if not self._send_frames():
            return False
        
        can_msg = can.message.Message(arbitration_id=frame_id, data=buf, dlc=length)
        try:
            self.bus.send(can_msg)
        except can.CanOperationError:
            if len(self._can_send_frame_buf) < self._max_can_send_frames:
                # Todo: log that we buffered the message
                self._can_send_frame_buf.append(can_msg)
            else:
                # Todo: log that we failed to send frame and couldn't even store it on the buffer to be retried
                pass
            return False
        return True
    
    def _get_next_free_can_send_frame(self) -> CANSendFrame:
        print("NotImplemented _get_next_free_can_send_frame")
    
    def _send_pending_information(self) -> None:
        print("NotImplemented _send_pending_information")
    
    def _is_initialized(self) -> bool:
        print("NotImplemented _is_initialized")
    
    # ISO Multi Packet Support
    # def _find_free_can_msg_index(self, pgn: int, source: int, destination: int, tp_msg: bool, msg_index: int) -> None:
    def _find_free_can_msg_index(self, pgn: int, source: int, destination: int, msg_index: int) -> None:
        print("NotImplemented _find_free_can_msg_index")
    
    def _set_n2k_can_buf_msg(self, can_id: int, length: int, buf: bytearray):
        print("NotImplemented _set_n2k_can_buf_msg")
    
    def _is_fast_packet_pgn(self, pgn: int) -> bool:
        return is_fast_packet_system_message(pgn) or is_mandatory_fast_packet_message(pgn) or \
               is_default_fast_packet_message(pgn) or is_proprietary_fast_packet_message(pgn) or \
               (self.custom_fast_packet_messages is not None and pgn in self.custom_fast_packet_messages)
    
    def _is_fast_packet(self, msg: Message) -> bool:
        if msg.priority >= 0x80:
            # Special handling for force to send message as single frame # TODO: force?
            return False
        return self._is_fast_packet_pgn(msg.pgn)
    
    def _check_known_message(self, pgn: int) -> (bool, bool, bool):
        # TODO: refactor
        system_message = False
        fast_packet = False
        if pgn == 0:
            # Unknown message
            return False, system_message, fast_packet
        
        if is_default_single_frame_message(pgn):
            return True, system_message, fast_packet
        
        fast_packet = is_mandatory_fast_packet_message(pgn)
        if fast_packet:
            return True, system_message, fast_packet
        
        fast_packet = is_default_fast_packet_message(pgn)
        if fast_packet:
            return True, system_message, fast_packet
        
        fast_packet = is_fast_packet_system_message(pgn)
        if is_single_frame_system_message(pgn) or fast_packet:
            system_message = True
            return True, system_message, fast_packet
        
        if self.custom_single_frame_messages is not None and pgn in self.custom_single_frame_messages:
            return True, system_message, fast_packet
        
        fast_packet = self.custom_fast_packet_messages is not None and pgn in self.custom_fast_packet_messages
        if fast_packet:
            return True, system_message, fast_packet
        
        fast_packet = is_proprietary_fast_packet_message(pgn)
        
        return False, system_message, fast_packet
    
    def _handle_received_system_message(self, msg: N2kCANMessage) -> bool:
        if msg.system_message:
            if msg.n2k_msg.pgn == PGN.IsoAcknowledgement:
                pass
            elif msg.n2k_msg.pgn == PGN.IsoRequest:
                self._handle_iso_request(msg.n2k_msg)
            elif msg.n2k_msg.pgn == PGN.IsoAddressClaim:
                self._handle_iso_address_claim(msg.n2k_msg)
            elif msg.n2k_msg.pgn == PGN.CommandedAddress:
                self._handle_commanded_address(msg.n2k_msg)
            # if msg.n2k_msg.pgn == PGN.RequestGroupFunction:
            #    self._handle_group_function(msg.n2k_msg)
            return True
        return False
    
    def _respond_iso_request(self, msg: Message, requested_pgn: int) -> None:
        if self._is_address_claim_started():
            # We don't respond to any queries during address claiming
            return
        if requested_pgn == PGN.IsoAddressClaim:
            # Someone is asking others to claim their addresses
            self.send_iso_address_claim(0xff)
        elif requested_pgn == PGN.SupportedPGNList:
            self.send_tx_pgn_list(msg.source)
            self.send_rx_pgn_list(msg.source)
        elif requested_pgn == PGN.ProductInformation:
            self.send_product_information()
        elif requested_pgn == PGN.ConfigurationInformation:
            self.send_configuration_information()
        else:
            if self._request_handler is not None and self._request_handler(requested_pgn, msg.source):
                return
            ack_msg = Message()
            set_n2k_pgn_iso_acknowledgement(msg, 1, 0xff, requested_pgn)
            ack_msg.destination = msg.source
            self.send_msg(ack_msg)
    
    def _handle_iso_request(self, msg: Message) -> None:
        if not (is_broadcast(msg.destination) or msg.destination == self.n2k_source):
            requested_pgn = parse_n2k_pgn_iso_request(msg)
            if requested_pgn is not None:
                self._respond_iso_request(msg, requested_pgn)
    
    #  TOOD
    # def _respond_group_function(self, msg: N2kMessage, group_function_code: GroupFunctionCode, pgn_for_group_function: int) -> None:
    #     raise NotImplementedError()
    
    # def _handle_group_function(self, msg: N2kMessage) -> None:
    #    raise NotImplementedError()
    
    def _start_address_claim(self) -> None:
        if self.n2k_source == N2K_NULL_CAN_BUS_ADDRESS:
            self._get_next_address(True)
        self.address_claim_started = 0
        self.send_iso_address_claim()
        self.address_claim_started = millis()
    
    def _is_address_claim_started(self) -> bool:
        if self.address_claim_started != 0 and \
                self.address_claim_started + N2K_ADDRESS_CLAIM_TIMEOUT < millis():
            self.address_claim_started = 0
            # We have claimed our address. Save end source for next possible claim run.
            # TODO: why do it here? assuming to allow for contest of source address? where is contest handled?
            self.update_address_claim_end_source()
        
        return self.address_claim_started != 0
    
    def _handle_iso_address_claim(self, msg: Message) -> None:
        if msg.source == N2K_NULL_CAN_BUS_ADDRESS or msg.source != self.n2k_source:
            # Not claiming our address, so we don't care
            return
        
        index = IntRef(0)
        caller_name = msg.get_uint_64(index)
        
        if self.device_information.name < caller_name:
            # We can keep our information, so reclaim it.
            self.send_iso_address_claim()
        else:
            # We have to move to another address
            if self.device_information.name == caller_name and self._is_address_claim_started():
                # If the name is the same, then the first instance will win the claim and get the address.
                # This shouldn't happen, if the user takes care to set a unique ID for device information.
                # If he does not there is no problem with this class, but e.g. Garmin gets crazy.
                # Try to solve situation by changing our device instance.
                self.device_information.device_instance += 1
                self.device_information_changed = True
            else:
                self._get_next_address()
            self._start_address_claim()
    
    def _handle_commanded_address(self, msg: Message) -> None:
        if msg.pgn != PGN.CommandedAddress or not msg.tp_message or msg.data_len != 9:
            return
        if not is_broadcast(msg.destination) and msg.destination != self.n2k_source:
            return
        index = IntRef(0)
        commanded_name = msg.get_uint_64(index)
        new_address = msg.get_byte(index)
        if new_address >= 252:
            return
        if self.device_information.name == commanded_name and self.n2k_source != new_address:
            # We have been commanded to set our address
            self.n2k_source = new_address
            self.update_address_claim_end_source()
            self._start_address_claim()
            self.address_changed = True
    
    def _get_next_address(self, restart_at_end: bool = False):
        if self.n2k_source == N2K_NULL_CAN_BUS_ADDRESS:
            if restart_at_end:
                # For Null address start at beginning
                self.n2k_source = 14
                self.update_address_claim_end_source()
            else:
                return
        elif self.n2k_source != self.address_claim_end_source:
            self.n2k_source += 1
            if self.n2k_source > N2K_MAX_CAN_BUS_ADDRESS:
                self.n2k_source = 0
        else:
            # Cannot claim address
            self.n2k_source = N2K_NULL_CAN_BUS_ADDRESS

        self.address_changed = True
        return
    
    def _get_sequence_counter(self, pgn: int):
        if self.pgn_sequence_counters is None:
            # One sequence counter per outbound fast packet PGN plus one for undefined PGNs
            self.max_pgn_sequence_counters = self._get_fast_packet_tx_pgn_count() + 1
            self.pgn_sequence_counters = []
        
        for i in range(len(self.pgn_sequence_counters)):
            if self.pgn_sequence_counters[i] & 0x00ffffff == pgn:
                # found our counter
                value = self.pgn_sequence_counters[i] >> 24 + 1
                if value > 7:
                    value = 0
                self.pgn_sequence_counters[i] = pgn | (value << 24)
                return value
        self.pgn_sequence_counters.append(pgn)
        return 0
    
    def _get_fast_packet_tx_pgn_count(self) -> int:
        counter = 0
        for pgn in DefaultTransmitMessages + self.transmit_messages:
            if self._is_fast_packet_pgn(pgn):
                counter += 1
        return counter
    
    # Forward Handling Code Skipped
    
    def _run_message_handlers(self, msg: Message) -> None:
        print("NotImplemented _run_message_handlers")
    
    # ISO Multi Packet Support
    # def _test_handle_tp_message(self, pgn: int, source: int, destination: int) -> bool:
    #     raise NotImplementedError()
    #
    # def _send_tpcm_bam(self) -> bool:
    #     raise NotImplementedError()
    #
    # def _send_tpcm_rts(self) -> bool:
    #     raise NotImplementedError()
    #
    # def _send_tpcm_cts(self, pgn: int, destination: int, n_packets: int, next_packet_number: int) -> None:
    #     raise NotImplementedError()
    #
    # def _send_tpcm_end_ack(self, pgn: int, destination: int, n_bytes: int, n_packets: int) -> None:
    #     raise NotImplementedError()
    #
    # def _send_tpcm_abort(self, pgn: int, destination: int, abort_code: int) -> None:
    #     raise NotImplementedError()
    #
    # def _send_tpdt(self) -> bool:
    #     raise NotImplementedError()
    #
    # def _has_all_tpdt_sent(self) -> bool:
    #     raise NotImplementedError()
    #
    # def _start_send_tp_message(self, msg: N2kMessage) -> bool:
    #     raise NotImplementedError()
    #
    # def _end_send_tp_message(self) -> None:
    #     raise NotImplementedError()
    #
    # def _send_pending_tp_messages(self) -> None:
    #     raise NotImplementedError()
    
    # Group Function Support
    # def _copy_progmem_configuration_information_to_local(self) -> None:
    #     raise NotImplementedError()
    #
    # installation_description_changed: bool
    
    def set_n2k_can_msg_buf_size(self, max_n2k_can_msgs: int) -> None:
        self._max_n2k_can_msgs = max_n2k_can_msgs
    
    def set_n2k_can_send_frame_buf_size(self, max_can_send_frames: int) -> None:
        if not self._is_initialized():
            self._max_can_send_frames = max_can_send_frames
    
    def set_n2k_can_receive_frame_buf_size(self, max_can_receive_frames) -> None:
        if not self._is_initialized():
            self._max_can_receive_frames = max_can_receive_frames
    
    # Group Function Support
    # bool IsTxPGN(unsigned long PGN, int iDev=0);
    # const tNMEA2000::tProductInformation * GetProductInformation(int iDev, bool &IsProgMem) const;
    # unsigned short GetN2kVersion(int iDev=0) const;
    # unsigned short GetProductCode(int iDev=0) const;
    # void GetModelID(char *buf, size_t max_len, int iDev=0) const;
    # void GetSwCode(char *buf, size_t max_len, int iDev=0) const;
    # void GetModelVersion(char *buf, size_t max_len, int iDev=0) const;
    # void GetModelSerialCode(char *buf, size_t max_len, int iDev=0) const;
    # unsigned char GetCertificationLevel(int iDev=0) const;
    # unsigned char GetLoadEquivalency(int iDev=0) const;
    # void SetInstallationDescription1(const char *InstallationDescription1);
    # void SetInstallationDescription2(const char *InstallationDescription2);
    # void GetInstallationDescription1(char *buf, size_t max_len);
    # void GetInstallationDescription2(char *buf, size_t max_len);
    # void GetManufacturerInformation(char *buf, size_t max_len);
    # bool ReadResetInstallationDescriptionChanged();
    
    # TODO: override / extend supported packets
    # // Call these if you wish to override the default message packets supported.  Pointers must be in PROGMEM
    # void SetSingleFrameMessages(const unsigned long *_SingleFrameMessages);
    # void SetFastPacketMessages (const unsigned long *_FastPacketMessages);
    # // Call these if you wish to add own list of supported message packets.  Pointers must be in PROGMEM
    # // Note that currently subsequent calls will override previously set list.
    # void ExtendSingleFrameMessages(const unsigned long *_SingleFrameMessages);
    # void ExtendFastPacketMessages (const unsigned long *_FastPacketMessages);
    # // Define information about PGNs, what your system can handle.  Pointers must be in PROGMEM
    # // As default for request to PGN list library responds with default messages it handles internally.
    # // With these messages you can extent that list. See example TemperatureMonitor
    # void ExtendTransmitMessages(const unsigned long *_SingleFrameMessages, int iDev=0);
    # void ExtendReceiveMessages(const unsigned long *_FastPacketMessages, int iDev=0);
    
    def send_iso_address_claim(self, destination: int = 0xff, delay: int = 0) -> None:
        """
        Some Devices (Garmin) constantly request information about others on the network.
        Thus, we need to re-send our address claim, or they will stop detecting us.
        :param destination:
        :param delay:
        :return:
        """
        
        if delay > 0:
            self.set_pending_iso_address_claim(delay)
            return
        
        msg = Message(self.n2k_source)
        msg.destination = destination
        set_n2k_iso_address_claim(msg=msg,
                                  unique_number=self.device_information.unique_number,
                                  manufacturer_code=self.device_information.manufacturer_code,
                                  device_function=self.device_information.device_function,
                                  device_class=self.device_information.device_class,
                                  device_instance=self.device_information.device_instance,
                                  system_instance=self.device_information.system_instance,
                                  industry_group=self.device_information.industry_group)
        self.send_msg(msg)
    
    # ISO Multi Packet Support
    # bool SendProductInformation(unsigned char Destination, int DeviceIndex, bool UseTP);
    # bool SendConfigurationInformation(unsigned char Destination, int DeviceIndex, bool UseTP);
    # void SendTxPGNList(unsigned char Destination, int DeviceIndex, bool UseTP=false);
    # void SendRxPGNList(unsigned char Destination, int DeviceIndex, bool UseTP=false);
    
    def send_tx_pgn_list(self, destination: int) -> None:  # todo: use_tp
        msg = Message(self.n2k_source)
        msg.destination = destination
        msg.pgn = PGN.SupportedPGNList
        msg.priority = 6
        # msg.tp_message = use_tp
        msg.add_byte(N2kPGNList.transmit)
        for supported_pgn in DefaultTransmitMessages + self.transmit_messages:
            msg.add_3_byte_int(supported_pgn)
        self.send_msg(msg)
    
    def send_rx_pgn_list(self, destination: int) -> None:  # todo: use_tp
        msg = Message(self.n2k_source)
        msg.destination = destination
        msg.pgn = PGN.SupportedPGNList
        msg.priority = 6
        # msg.tp_message = use_tp
        msg.add_byte(N2kPGNList.receive)
        for supported_pgn in DefaultReceiveMessages + self.receive_messages:
            msg.add_3_byte_int(supported_pgn)
        self.send_msg(msg)
    
    def send_product_information(self, destination: int = 0xff) -> bool:  # use_tp: bool = False
        msg = Message(self.n2k_source)
        msg.destination = destination
        # msg.tp_message = use_tp
        msg.pgn = PGN.ProductInformation
        set_n2k_product_information(msg=msg,
                                    n2k_version=self.product_information.n2k_version,
                                    product_code=self.product_information.product_code,
                                    model_id=self.product_information.n2k_model_id,
                                    sw_code=self.product_information.n2k_sw_code,
                                    model_version=self.product_information.n2k_model_version,
                                    model_serial_code=self.product_information.n2k_model_serial_code,
                                    certification_level=self.product_information.certification_level,
                                    load_equivalency=self.product_information.load_equivalency)
        if self.send_msg(msg):
            self.clear_pending_product_information()
            return True
        self.set_pending_product_information()
        return False
    
    def send_configuration_information(self, destination = 0xff) -> bool: #  use_tp: bool = False
        msg = Message(self.n2k_source)
        msg.destination = destination
        # msg.tp_message = ust_tp
        if self.configuration_information.manufacturer_information == "" and \
                self.configuration_information.installation_description1 == "" and \
                self.configuration_information.installation_description2 == "":
            # No information provided
            set_n2k_pgn_iso_acknowledgement(msg, 1, 0xff, PGN.ConfigurationInformation)
        else:
            set_n2k_configuration_information(
                msg=msg,
                manufacturer_information=self.configuration_information.manufacturer_information,
                installation_description1=self.configuration_information.installation_description1,
                installation_description2=self.configuration_information.installation_description2,
            )
        if self.send_msg(msg):
            self.clear_pending_configuration_information()
            return True
        self.set_pending_configuration_information()
        return False
    
    # Heartbeat Support
    def send_heartbeat(self, force: bool = False):
        print("NotImplemented send_heartbeat")
    
    # Send message to the bus
    def send_msg(self, msg: Message) -> bool:
        result = False
        
        msg.check_destination()
        msg.source = self.n2k_source
        
        if msg.source > N2K_MAX_CAN_BUS_ADDRESS and msg.pgn != PGN.IsoAddressClaim:
            # CAN bus address range is 0-251. Allow ISO Address claim messages nevertheless. TODO: why?
            return False
        
        can_id = n2k_id_to_can(priority=msg.priority, pgn=msg.pgn, source=msg.source, destination=msg.destination)
        
        if can_id is None or msg.pgn == 0:
            return False
        
        if self._is_address_claim_started() and msg.pgn != PGN.IsoAddressClaim:
            return False
        
        if msg.data_len <= 8 and self._is_fast_packet(msg):
            # Can be sent as a single packet
            result = self._send_frame(can_id, msg.data_len, msg.data)
        else:
            # Has to be sent as fast packet in multiple frames
            # if msg.tp_message:  # TODO: iso multi packet support
            #     result = self.start_send_tp_message(msg)
            # else:
            frames: int = ((msg.data_len-6-1) // 7)+1+1 if msg.data_len > 6 else 1
            order = self._get_sequence_counter(msg.pgn) << 5  # TODO: what is this good for?? gives us 3 bit for the front
            result = True
            cur = 2
            for i in range(frames):
                buf = bytearray(i | order)
                if i == 0:
                    buf.extend(msg.data[cur:cur+6])
                    cur += 6
                else:
                    buf.extend(msg.data[cur:cur+7])
                    cur += 7
                    while len(buf) < 8:
                        buf.append(0xff)
                result = self._send_frame(can_id, 8, buf)
                if not result:
                    break
        
        return result
    
    def attach_msg_handler(self, msg_handler: MessageHandler) -> None:
        self.message_handlers.add(msg_handler)
    
    def detach_msg_handler(self, msg_handler: MessageHandler) -> None:
        self.message_handlers.remove(msg_handler)
    
    def set_iso_request_handler(self, request_handler: Callable[[int, int], bool]) -> None:
        self._request_handler = request_handler
    
    def remove_iso_request_handler(self) -> None:
        self._request_handler = None
    
    # Group Function Support
    # def add_group_function_handler(self, group_function_handler: GroupFunctionHandler) -> None:
    #     raise NotImplementedError()
    #
    # def remove_group_function_handler(self, group_function_handler: GroupFunctionHandler) -> None:
    #     raise NotImplementedError()
