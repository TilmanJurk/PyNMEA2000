from typing import Optional, List

import n2k.device
from n2k.message import Message, N2K_UINT16_NA, N2K_UINT32_NA
from n2k.message_handler import MessageHandler
import n2k.messages
from n2k.n2k import PGN
from n2k.types import N2kPGNList
from n2k.utils import IntRef, millis
from n2k.constants import *


class DeviceList(MessageHandler):
    sources: List[Optional["n2k.device.Device"]]
    max_devices: int
    list_updated: bool
    has_pending_requests: bool
    
    def __init__(self, node: 'n2k.node.Node'):
        """
        Initialize Device List
        """
        super().__init__(0, node)
        self.sources = [None] * N2K_MAX_BUS_DEVICES
        self.max_devices = 0
        self.list_updated = False
        self.has_pending_requests = True
    
    def handle_msg(self, msg: Message) -> None:
        # assert that source is valid (0<=s<254), 254 = null, 255 = broadcast
        if not 0 <= msg.source < 254:
            return
        
        # if message destination has not been added to our device list yet
        if self.sources[msg.source] is None:
            # Address Claim -> do nothing
            if msg.pgn == PGN.IsoAddressClaim:
                pass
            elif msg.pgn in [PGN.ProductInformation, PGN.ConfigurationInformation, PGN.SupportedPGNList]:
                # Product Information | Configuration Information | PGN List -> create device
                self._add_device(msg.source)
            else:
                # Other Message -> create device and early return
                self._add_device(msg.source)
                return
        
        # Call corresponding handler
        if msg.pgn == PGN.IsoAddressClaim:
            self._handle_iso_address_claim(msg)
        elif msg.pgn == PGN.ProductInformation:
            self._handle_product_information(msg)
        elif msg.pgn == PGN.ConfigurationInformation:
            self._handle_configuration_information(msg)
        elif msg.pgn == PGN.SupportedPGNList:
            self._handle_supported_pgn_list(msg)
        else:
            self._handle_other(msg)
             
        # if message destination has been added to our devicelist by now
        #  (should always be the case - address claim does it in handle address claim)
        dev = self.sources[msg.source]
        if dev is not None:
            # If device has no name, the name has already been requested and the last message by this device has been
            # over one minute ago, assume it has been turned off in the meantime and now reconnected.
            if dev.dev_i.name == 0 and dev.n_name_requested > 0 and dev.last_message_time + 60*1000 < millis():
                # Reset the number of name requests that have been sent.
                dev.n_name_requested = 0
                self.has_pending_requests = True
                
        # set last message time to now
        dev.last_message_time = millis()
    
    def _handle_iso_address_claim(self, msg: Message) -> None:
        if msg.pgn != PGN.IsoAddressClaim:
            return
        
        # initialize index
        index: IntRef = IntRef(0)
        # get NAME from message. TODO: verify order
        caller_name: int = msg.get_uint_64(index)
        
        dev: Optional[n2k.device.Device] = None
        
        # verify source is valid and check if we already have a device at that address
        if 0 <= msg.source < N2K_MAX_BUS_DEVICES and self.sources[msg.source] is not None:
            # set current device to stored device
            dev: n2k.device.Device = self.sources[msg.source]
            # check if it has a name
            if dev.dev_i.name == 0:
                # if it doesn't, check if we have a device with the current name at a different address
                dev2 = self.find_device_by_name(caller_name)
                
                if dev2 is not None:
                    # if we do, remove the device at the claimed address
                    self.sources[msg.source] = None
                    self.sources[dev2.source] = None
                    # and move the device with the matching name there
                    self._save_device(dev2, msg.source)
                    dev = dev2
                else:
                    # if we don't, set device at claimed address to have the provided name and set list_updated to true
                    dev.dev_i.name = caller_name
                    self.list_updated = True
            elif dev.dev_i.name != caller_name:
                # if the device has a name, but it does not match the provided one
                try:
                    # move the old device to some unused spot in list
                    first_free_index = self.sources.index(None)
                    self._save_device(dev, first_free_index)
                except ValueError:
                    # if no free spot is available just drop it
                    pass
                # send broadcast iso address claim request
                self._request_iso_address_claim(0xff)
                # Clear the moved source old position in device list
                self.sources[msg.source] = None
                dev = None
                # Move new claimant to this position in next block
            else:
                # the device has a name and it matches, therefore we don't have to do anything
                return
        
        if dev is None:
            # No device exists at the source address yet or the device that did exist has been moved somewhere else
            # or dropped due to a collision
            dev = self.find_device_by_name(caller_name)
            if dev is not None:
                # Address has been changed, move the device to the new address in our list
                self._save_device(dev, msg.source)
            else:
                # New Device
                dev = n2k.device.Device(caller_name)
                self._save_device(dev, msg.source)
        
        # Either we have a new device or the address has changed, so we re-request the product information
        dev.clear_product_information_loaded()
        self.has_pending_requests = True

        self.list_updated = True
    
    def _handle_product_information(self, msg: Message) -> None:
        # Check if device exists in our list
        if not 0 <= msg.source < N2K_MAX_BUS_DEVICES or self.sources[msg.source] is None:
            return
        dev: n2k.device.Device = self.sources[msg.source]
        
        # If the product information has not been loaded yet
        if not dev.prod_i_loaded:
            # parse the product information from the message
            prod_i = n2k.messages.parse_n2k_pgn_126996(msg)
            # check if it is different from the current product information
            #  (can be the same if it was triggered by an address change)
            if dev.prod_i != prod_i:
                # and replace it with the new product information
                dev.prod_i = prod_i
                self.list_updated = True
            dev.prod_i_loaded = True
    
    def _handle_configuration_information(self, msg: Message) -> None:
        # Check if device exists in our list
        if not 0 <= msg.source < N2K_MAX_BUS_DEVICES or self.sources[msg.source] is None:
            return
        dev: n2k.device.Device = self.sources[msg.source]
        
        # If the configuration information has not been loaded yet
        if not dev.conf_i_loaded:
            # parse the configuration information from the message
            conf_i = n2k.messages.parse_n2k_pgn_126998(msg)
            # check if it is different from the current configuration information
            if dev.conf_i != conf_i:
                # and replace it with the new configuration information
                dev.conf_i = conf_i
                self.list_updated = True
            dev.conf_i_loaded = True
    
    def _handle_supported_pgn_list(self, msg: Message) -> None:
        # Check if device exists in our list
        if not 0 <= msg.source < N2K_MAX_BUS_DEVICES or self.sources[msg.source] is None:
            return
        dev: n2k.device.Device = self.sources[msg.source]
        
        # Create an IntRef that we can pass to our get functions so that we can keep track of
        # where we are in the binary data
        index: IntRef = IntRef(0)
        # Parse if this is a list of receivable or transmittable PGNs
        n2k_pgn_list: N2kPGNList = N2kPGNList(msg.get_byte(index))
        # Each PGN takes up 3 bytes. If we get a remainder something is wrong with the data.
        pgn_count, rem = divmod(msg.data_len - index, 3)
        assert rem == 0
        
        # Clear the corresponding list and select it
        pgn_list: Optional[List] = None
        if n2k_pgn_list == N2kPGNList.transmit:
            dev.transmit_pgns = []
            pgn_list = dev.transmit_pgns
        elif n2k_pgn_list == N2kPGNList.receive:
            dev.receive_pgns = []
            pgn_list = dev.receive_pgns

        if pgn_list is not None:
            # Add all PGNs to the list
            for i in range(pgn_count):
                pgn_list.append(msg.get_3_byte_uint(index))
            pgn_list.append(0)  # Todo: why does the original code do this?
                
        self.list_updated = True
    
    def _handle_other(self, msg: Message) -> None:
        # assert that source is valid (0<=s<254), 254 = null, 255 = broadcast
        if not 0 <= msg.source < N2K_MAX_BUS_DEVICES:
            return
        
        # if has_pending_requests is false we already know everything we want, therefore we can return early
        if not self.has_pending_requests:
            return
        
        # set has_pending_requests to false, will be set to true again if we find something we're still missing
        self.has_pending_requests = False
        
        # if device has no name, check if name should be requested and then request name
        # (assumes a device exists at this index, as this is a condition for _handle_other to be called)
        if self.sources[msg.source].should_request_name() and self._request_iso_address_claim(msg.source):
            # increase requested counter
            self.sources[msg.source].n_name_requested += 1
            # set has_pending_requests to true
            self.has_pending_requests = True
        
        ## Get Product Information for every device
        # Iterate over all devices
        for dev in self.sources:
            # For all not-None devices check if it is ready for a product info request and request it in that case.
            if dev is not None:
                if dev.ready_for_request_product_information():
                    if self._request_product_information(dev.source):
                        # If request has been sent
                        # TODO: write to debug log
                        # set product info as requested for device
                        dev.n_prod_i_requested += 1
                        dev.prod_i_requested = millis()
                        self.has_pending_requests = True
                        # early return (therefore we will only ever request product information of one device at a time,
                        # to prevent spamming. Next request would only be sent after another message has been received)
                        return
                else:
                    # set has_pending_requests to result of (should_request_product_information or has_pending_requests)
                    self.has_pending_requests |= dev.should_request_product_information()
        
        if self.has_pending_requests:
            return

        ## Get Configuration Information for every device
        # Iterate over all devices
        for dev in self.sources:
            # For all not-None devices check if it is ready for a config info request and request it in that case.
            if dev is not None:
                if dev.ready_for_request_configuration_information():
                    if self._request_configuration_information(dev.source):
                        # If request has been sent
                        # TODO: write to debug log
                        # set configuration info as requested for device
                        dev.n_conf_i_requested += 1
                        dev.conf_i_requested = millis()
                        self.has_pending_requests = True
                        # early return (therefore we will only ever request config information of one device at a time,
                        # to prevent spamming. Next request would only be sent after another message has been received)
                        return
                else:
                    # set has_pending_requests to result of (should_request_conf_information or has_pending_requests)
                    self.has_pending_requests |= dev.should_request_configuration_information()

        if self.has_pending_requests:
            return

        ## Get PGN Lists for every device
        # Iterate over all devices
        for dev in self.sources:
            # For all not-None devices check if it is ready for a pgn list request and request it in that case.
            if dev is not None:
                if dev.ready_for_request_pgn_list():
                    if self._request_supported_pgn_list(dev.source):
                        # If request has been sent
                        # TODO: write to debug log
                        # set pgn lists as requested for device
                        dev.n_pgns_requested += 1
                        dev.pgns_requested = millis()
                        self.has_pending_requests = True
                        # early return (therefore we will only ever request pgns of one device at a time,
                        # to prevent spamming. Next request would only be sent after another message has been received)
                        return
                else:
                    # set has_pending_requests to result of (should_request_pgn_list() or has_pending_requests)
                    self.has_pending_requests |= dev.should_request_pgn_list()

            if self.has_pending_requests:
                return
    
    def _request_product_information(self, source: int) -> bool:
        """
        Send ISO Request Message, requesting Product Information, to ``source``

        :param source: Address of NMEA2000 Device.
        :return: Whether message was sent successfully.
        """
        # TODO
        print("NotImplemented _request_product_information")
    
    def _request_configuration_information(self, source: int) -> bool:
        """
        Send ISO Request Message, requesting Configuration Information, to ``source``

        :param source: Address of NMEA2000 Device.
        :return: Whether message was sent successfully.
        """
        # TODO
        print("NotImplemented, _request_configuration_information")
    
    def _request_supported_pgn_list(self, source: int) -> bool:
        """
        Send ISO Request Message, requesting a list of supported PGNs, to ``source``

        :param source: Address of NMEA2000 Device.
        :return: Whether message was sent successfully.
        """
        # TODO
        print("NotImplemented, _request_supported_pgn_list")
    
    def _request_iso_address_claim(self, source: int) -> bool:
        """
        Send ISO Request Message, requesting the device to claim the address it is currently using, to ``source``

        :param source: Address of NMEA2000 Device.
        :return: Whether message was sent successfully.
        """
        msg = Message()
        n2k.messages.set_n2k_pgn_iso_request(msg, source, PGN.IsoAddressClaim)
        return self._node.send_msg(msg)
    
    def _add_device(self, source: int) -> None:
        # request iso address claim from device. If message is sent call save device with a new device
        if self._request_iso_address_claim(source):
            self._save_device(n2k.device.Device(0), source)
            self.has_pending_requests = True
    
    def _save_device(self, dev: "n2k.device.Device", source: int) -> None:
        # assert that source id is valid
        if not 0 <= source <= N2K_MAX_BUS_DEVICES:
            return
        
        # update source on device
        dev.source = source
        # save device at self.sources[source]
        self.sources[source] = dev
        # raise max_devices to source+1 i it is lower
        if source >= self.max_devices:
            self.max_devices = source + 1
    
    def find_device_by_source(self, source: int) -> Optional["n2k.device.Device"]:
        if source >= N2K_MAX_BUS_DEVICES:
            return None
        return self.sources[source]
    
    def find_device_by_name(self, name: int) -> Optional["n2k.device.Device"]:
        for source in self.sources:
            if source is not None and source.dev_i.name == name:
                return source
        return None
    
    def find_device_by_ids(self, manufacturer_code: int, unique_number: int) -> Optional["n2k.device.Device"]:
        if manufacturer_code == N2K_UINT16_NA or unique_number == N2K_UINT32_NA:
            return None
        
        for source in self.sources:
            if source is not None and \
                    (manufacturer_code == N2K_UINT16_NA or
                     source.dev_i.manufacturer_code == manufacturer_code) and \
                    (unique_number == N2K_UINT32_NA or
                     source.dev_i.unique_number == unique_number):
                return source
        
        return None
    
    def find_device_by_product(self, manufacturer_code: int, product_code: int,
                               source: int = 0xff) -> Optional["n2k.device.Device"]:
        """
        This function seems to look for the next device with a given manufacturer_code and product_code behind
         the provided source.
         This means to find the first device by code you would need to provide source >= max_devices.
         As this is weird behaviour it is subject to change and source will be probably renamed to starting_source, ...
        
        :param manufacturer_code:
        :param product_code:
        :param source:
        :return:
        """
        if manufacturer_code == N2K_UINT16_NA or product_code == N2K_UINT16_NA:
            return None
        
        # TODO: Why do we do this source manipulation and discard devices with a lower source number?
        if source < self.max_devices:
            source += 1
        else:
            source = 0
        
        for dev in self.sources[source:]:
            if dev.dev_i.manufacturer_code == manufacturer_code and dev.prod_i.product_code == product_code:
                return dev
        
        return None
    
    def get_device_last_message_time(self, source: int) -> int:
        dev = self.find_device_by_source(source)
        if dev is None:
            return 0
        else:
            return dev.last_message_time
    
    def read_reset_is_list_updated(self):
        if self.list_updated:
            self.list_updated = False
            return True
        return False
    
    def count(self):
        c = 0
        for x in self.sources:
            if x is not None:
                c += 1
        return c
