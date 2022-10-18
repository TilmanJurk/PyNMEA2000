import math
from typing import NamedTuple, List

from n2k.message import n2k_double_is_nan, Message, N2K_DOUBLE_NAN
from n2k.can_message import N2kCANMessage
from n2k.types import N2kTimeSource, N2kAISRepeat, N2kAISTransceiverInformation, N2kMOBStatus, N2kMOBPositionSource, \
    N2kHeadingReference, N2kMOBEmitterBatteryStatus, N2kOnOff, N2kSteeringMode, N2kTurnMode, N2kRudderDirectionOrder, \
    ProductInformation, ConfigurationInformation


def rad_to_deg(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return math.degrees(v)


def deg_to_rad(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return math.radians(v)


def c_to_kelvin(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v + 273.15


def kelvin_to_c(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v - 273.15


def f_to_kelvin(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return (v - 32) * 5.0 / 9.0 + 273.15


def kelvin_to_f(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return (v - 273.15) * 9.0 / 4.0 + 32


def mbar_to_pascal(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v * 100


def pascal_to_mbar(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v / 1000


def hpa_to_pascal(v: float) -> float:
    return mbar_to_pascal(v)


def pascal_to_hpa(v: float) -> float:
    return pascal_to_mbar(v)


def ah_to_coulomb(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v * 3600


def coulomb_to_ah(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v / 3600


def hours_to_seconds(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v * 3600


def seconds_to_hours(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v / 3600


def meters_per_second_to_knots(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v * 3600 / 1852


def knots_to_meters_per_second(v: float) -> float:
    if n2k_double_is_nan(v):
        return v
    return v * 1852 / 3600


class SystemTime(Message):
    def __init__(self, sid: int, system_date: int, system_time: float, time_source: N2kTimeSource = N2kTimeSource.GPS):
        super().__init__()
        self.pgn = 126992
        self.priority = 3
        self.add_byte(sid)
        self.add_byte((time_source & 0x0f) | 0xf0)
        self.add_2_byte_uint(system_date)
        self.add_4_byte_double(system_time, 1e-4)
        
    @staticmethod
    def from_can(self, buf: bytearray) -> 'SystemTime':
        return None


# System Date/Time (PGN 126992)
def set_n2k_system_time(sid: int, system_date: int, system_time: float,
                        time_source: N2kTimeSource = N2kTimeSource.GPS) -> Message:
    """
    Generate NMEA2000 message containing specified System Date/Time (PGN 126992). System Time is in UTC.
    
    :param sid: Sequence ID. If your device is e.g. boat speed and heading at same time, you can set same SID for
        different messages to indicate that they are measured at same time
    :param system_date: Days since 1970-01-01
    :param system_time: seconds since midnight
    :param time_source: Time source, see :py:class:`n2k_types.N2kTimeSource`
    :return: NMEA2000 message ready to be sent.
    """
    raise NotImplementedError()


class SystemTime(NamedTuple):
    sid: int
    system_date: int
    system_time: float
    time_source: N2kTimeSource


def parse_n2k_system_time(msg: Message) -> SystemTime:
    """
    Parse current system time from a PGN 126992 message
    
    :param msg: NMEA2000 Message with PGN 126992
    :return: Dictionary containing the parsed information.
    """
    raise NotImplementedError()


# AIS Safety Related Broadcast Message (PGN 129802)
def set_n2k_ais_related_broadcast_msg(message_id: int, repeat: N2kAISRepeat, source_id: int,
                                      ais_transceiver_information: N2kAISTransceiverInformation,
                                      safety_related_text: str) -> Message:
    """
    Generate NMEA2000 message containing AIS Safety Related Broadcast Message. (PGN 129802)
    
    :param message_id: Message Type. Identifier for AIS Safety Related Broadcast Message aka Message 14; always 14.
    :param repeat: Repeat indicator. Used by the repeater to indicate how many times a message has been repeated.
        0-3; 0 = default; 3 = do not repeat anymore
    :param source_id: MMSI number of source station of message
    :param ais_transceiver_information: see :py:class:`n2k_types.N2kAISTransceiverInformation`
    :param safety_related_text: Maximum 121 bytes. Encoded as 6-bit ASCII
    :return: NMEA2000 message ready to be sent.
    """
    raise NotImplementedError()


class AISSafetyRelatedBroadcast(NamedTuple):
    message_id: int
    repeat: N2kAISRepeat
    source_id: int
    ais_transceiver_information: N2kAISTransceiverInformation
    safety_related_text: str


def parse_n2k_ais_related_broadcast_msg(msg: Message) -> AISSafetyRelatedBroadcast:
    """
    Parse current system time from a PGN 126992 message
    
    :param msg: NMEA2000 Message with PGN 126992
    :return: Dictionary containing the parsed information.
    """
    raise NotImplementedError()


# Man Overboard Notification (PGN 127233)
def set_n2k_mob_notification(sid: int, mob_emitter_id: int, mob_status: N2kMOBStatus, activation_time: float,
                             position_source: N2kMOBPositionSource, position_date: int, position_time: float,
                             latitude: float, longitude: float, cog_reference: N2kHeadingReference, cog: float,
                             sog: float, mmsi: int,
                             mob_emitter_battery_status: N2kMOBEmitterBatteryStatus) -> Message:
    """
    Generate NMEA2000 message containing Man Overboard Notification (PGN 127233)
    
    :param sid: Sequence ID. If your device is e.g. boat speed and heading at same time, you can set same SID for
        different messages to indicate that they are measured at same time.
    :param mob_emitter_id: Identifier for each MOB emitter, unique to the vessel
    :param mob_status: MOB Status, see :py:class:`n2k_types.N2kMOBStatus`
    :param activation_time: Time of day (UTC) in seconds when MOB was initially activated
    :param position_source: Position Source, see :py:class:`n2k_types.N2kMOBPositionSource`
    :param position_date: Date of MOB position in days since 1970-01-01 (UTC)
    :param position_time: Time of day of MOB position (UTC) in seconds
    :param latitude: Latitude in degrees
    :param longitude: Longitude in degrees
    :param cog_reference: True or Magnetic
    :param cog: Course Over Ground in radians with a resolution of 1x10E-4 rad
    :param sog: Speed Over Ground in m/s with a resolution of 1x10E-2 m/s
    :param mmsi: MMSI of vessel of Origin. Can be set to 2,147,483,647 if unknown
    :param mob_emitter_battery_status: see :py:class:`n2k_types.N2kMOBEmitterBatteryStatus`
    :return: NMEA2000 message ready to be sent.
    """
    raise NotImplementedError()


class MOBNotification(NamedTuple):
    sid: int
    mob_emitter_id: int
    mob_status: N2kMOBStatus
    activation_time: float
    position_source: N2kMOBPositionSource
    position_date: int
    position_time: float
    latitude: float
    longitude: float
    cog_reference: N2kHeadingReference
    cog: float
    sog: float
    mmsi: int
    mob_emitter_battery_status: N2kMOBEmitterBatteryStatus
    
    
def parse_n2k_mob_notification(msg: Message) -> MOBNotification:
    """
    Parse Man Over Board Notification from a PGN 127233 message

    :param msg: NMEA2000 Message with PGN 127233
    :return: Dictionary containing the parsed information.
    """
    raise NotImplementedError()


# Heading/Track Control (PGN 127237)
def set_n2k_heading_track_control(rudder_limit_exceeded: N2kOnOff, off_heading_limit_exceeded: N2kOnOff,
                                  off_track_limit_exceeded: N2kOnOff, override: N2kOnOff,
                                  steering_mode: N2kSteeringMode, turn_mode: N2kTurnMode,
                                  heading_reference: N2kHeadingReference,
                                  commanded_rudder_direction: N2kRudderDirectionOrder,
                                  commanded_rudder_angle: float, heading_to_steer_course: float, track: float,
                                  rudder_limit: float, off_heading_limit: float, radius_of_turn_order: float,
                                  rate_of_turn_order: float, off_track_limit: float,
                                  vessel_heading: float) -> Message:
    """
    Generate NMEA2000 message containing Heading/Track Control information (PGN 127233)
    
    :param rudder_limit_exceeded: Yes/No
    :param off_heading_limit_exceeded: Yes/No
    :param off_track_limit_exceeded: Yes/No
    :param override: Yes/No
    :param steering_mode: Steering Mode
    :param turn_mode: Turn Mode
    :param heading_reference: True or Magnetic
    :param commanded_rudder_direction: Port or Starboard
    :param commanded_rudder_angle: In radians
    :param heading_to_steer_course: In radians
    :param track: In radians
    :param rudder_limit: In radians
    :param off_heading_limit: In radians
    :param radius_of_turn_order: In meters
    :param rate_of_turn_order: In radians/s
    :param off_track_limit: In meters
    :param vessel_heading: In radians
    :return: NMEA2000 message ready to be sent.
    """
    raise NotImplementedError()


class HeadingTrackControl(NamedTuple):
    rudder_limit_exceeded: N2kOnOff
    off_heading_limit_exceeded: N2kOnOff
    off_track_limit_exceeded: N2kOnOff
    override: N2kOnOff
    steering_mode: N2kSteeringMode
    turn_mode: N2kTurnMode
    heading_reference: N2kHeadingReference
    commanded_rudder_direction: N2kRudderDirectionOrder
    commanded_rudder_angle: float
    heading_to_steer_course: float
    track: float
    rudder_limit: float
    off_heading_limit: float
    radius_of_turn_order: float
    rate_of_turn_order: float
    off_track_limit: float
    vessel_heading: float
    

def parse_n2k_heading_track_control(msg: Message) -> HeadingTrackControl:
    """
    Parse heading/track control information from a PGN 127237 message

    :param msg: NMEA2000 Message with PGN 127237
    :return: Dictionary containing the parsed information.
    """
    raise NotImplementedError()


# Rudder (PGN 127245)
def set_n2k_rudder(rudder_position: float, instance: int = 0,
                   rudder_direction_order: N2kRudderDirectionOrder = N2kRudderDirectionOrder.NoDirectionOrder,
                   angle_order: float = N2K_DOUBLE_NAN) -> Message:
    """
    Rudder
    
    :param rudder_position: Current rudder postion in radians.
    :param instance: Rudder instance.
    :param rudder_direction_order: Direction, where rudder should be turned.
    :param angle_order: Angle where rudder should be turned in radians.
    :return: NMEA2000 Message ready to be sent.
    """
    raise NotImplementedError()


class Rudder(NamedTuple):
    rudder_position: float
    instance: int
    rudder_direction_order: N2kRudderDirectionOrder
    angle_order: float
    

def parse_n2k_rudder(msg: Message) -> Rudder:
    """
    Parse rudder control information from a PGN 127245 message
    
    :param msg: NMEA2000 Message with PGN 127245
    :return: Dictionary containing the parsed information
    """
    raise NotImplementedError()


# Vessel Heading (PGN 127250)
def set_n2k_heading(sid: int, heading: float, deviation: float = N2K_DOUBLE_NAN, variation: float = N2K_DOUBLE_NAN,
                    ref: N2kHeadingReference = N2kHeadingReference.true) -> Message:
    """
    Vessel Heading (PGN 127250).
    If the true heading is used, leave the deviation and variation undefined. Else if the magnetic heading is sent,
    specify the magnetic deviation and variation.
    
    :param sid: Sequence ID. If your device is e.g. boat speed and heading at same time, you can set same SID for
        different messages to indicate that they are measured at same time.
    :param heading: Heading in radians
    :param deviation: Magnetic deviation in radians. Use `N2K_DOUBLE_NAN` for undefined value.
    :param variation: Magnetic variation in radians. Use `N2K_DOUBLE_NAN` for undefined value.
    :param ref: Heading reference. Can be true or magnetic.
    :return: NMEA2000 message ready to be sent.
    """
    raise NotImplementedError()


class Heading(NamedTuple):
    sid: int
    heading: float
    deviation: float
    variation: float
    ref: N2kHeadingReference


def parse_n2k_heading(msg: Message) -> Heading:
    """
    Parse heading information from a PGN 127250 message
    
    :param msg: NMEA2000 Message with PGN 127250
    :return: Dictionary containing the parsed information
    """
    raise NotImplementedError()


# Rate of Turn (PGN 127251)
# TODO


# Attitude (PGN 127257)
# TODO


# Magnetic Variation (PGN 127258)
# TODO


# Engine parameters rapid (PGN 127488)
# TODO


# Engine parameters dynamic (PGN 127489)
# TODO


# Transmission parameters, dynamic (PGN 127493)
# TODO


# Trip Parameters, Engine (PGN 127497)
# TODO


N2kBinaryStatus = int


def n2k_get_status_on_binary_status(bank_status: N2kBinaryStatus, item_index: int = 1) -> N2kOnOff:
    """
    Get single status of full binary bank status returned by :py:func:`parse_n2k_binary_status`.
    
    :param bank_status: Full bank status read by :py:func:`parse_n2k_binary_status`
    :param item_index: Status item index 1-28
    :return: single status of full binary bank status
    """
    raise NotImplementedError()


def n2k_reset_binary_status(bank_status: N2kBinaryStatus) -> None:
    # TODO: can't pass int as reference in python so this doesn't make any sense
    raise NotImplementedError()


def n2k_set_status_binary_on_status(bank_status: N2kBinaryStatus, item_status: N2kOnOff, item_index: int = 1) -> N2kBinaryStatus:
    """
    Set single status to full binary bank status.
    
    :param bank_status: Existing Bank Status
    :param item_status: New Item Status
    :param item_index: Index of Item to be changed
    :return: New Bank Status
    """
    raise NotImplementedError()


# Binary status report (PGN 127501)
# TODO


# Fluid level (PGN 127505)
# TODO


# DC Detailed Status (PGN 127506)
# TODO


# Charger Status (PGN 127507)
# TODO


# Battery Status (PGN 127508)
# TODO


# Battery Configuration Status (PGN 127513)
# TODO


# Leeway (PGN 128000)
# TODO


# Boat Speed (PGN 128259)
# TODO


# Water depth (PGN 128267)
# TODO


# Distance log (PGN 128275)
# TODO


# Anchor Windlass Control Status (PGN 128776)
# TODO


# Anchor Windlass Operating Status (PGN 128777)
# TODO


# Anchor Windlass Monitoring Status (PGN 128778)
# TODO


# Lat/lon rapid (PGN 129025)
# TODO


# COG SOG rapid (PGN 129026)
# TODO


# GNSS Position Data (PGN 129029)
# TODO


# Date,Time & Local offset (PGN 129033, see also PGN 126992)
# TODO


# AIS position reports for Class A (PGN 129038)
# TODO


# AIS position reports for Class B (PGN 129039)
# TODO


# AIS Aids to Navigation (AtoN) Report (PGN 129041)
# TODO


# Cross Track Error (PGN 129283)
# TODO


# Navigation info (PGN 129284)
# TODO


# Route/WP information (PGN 129285)
# TODO


# GNSS DOP data (PGN 129539)
# TODO


# GNSS Satellites in View (PGN 129540)
# TODO


# AIS static data class A (PGN 129794)
# TODO


# AIS static data class B part A (PGN 129809)
# TODO


# AIS static data class B part B (PGN 129810)
# TODO


# Waypoint list (PGN 130074)
# TODO


# Wind Speed (PGN 130306)
# TODO


# Outside Environmental parameters (PGN 130310)
# TODO


# Environmental parameters (PGN 130311)
# TODO


# Temperature [deprecated] (PGN 130312)
# TODO


# Humidity (PGN 130313)
# TODO


# Pressure (PGN 130314)
# TODO


# Set pressure (PGN 130315)
# TODO


# Temperature (PGN 130316)
# TODO


# Meteorological Station Data (PGN 130323)
# TODO


# Small Craft Status (Trim Tab Position) (PGN 130576)
# TODO


# Direction Data (PGN 130577)
# TODO


# ISO Acknowledgement (PGN 59392)
def set_n2k_pgn_iso_acknowledgement(msg: Message, control: int, group_function: int, pgn: int) -> None:
    raise NotImplementedError()


# ISO Address Claim (PGN 60928)
def set_n2k_iso_address_claim(msg: Message, unique_number: int, manufacturer_code: int, device_function: int,
                              device_class: int, device_instance: int = 0, system_instance: int = 0,
                              industry_group: int = 4) -> None:
    raise NotImplementedError()


def set_n2k_iso_address_claim_by_name(msg: Message, name: int) -> None:
    raise NotImplementedError()


# Product Information (PGN 126996)
def set_n2k_product_information(msg: Message, n2k_version: int, product_code: int, model_id: str, sw_code: str,
                                model_version: str, model_serial_code: str, certification_level: int = 1,
                                load_equivalency: int = 1) -> None:
    raise NotImplementedError()


# TODO: parser
def parse_n2k_pgn_126996(msg: Message) -> ProductInformation:
    raise NotImplementedError()


# Configuration Information (PGN: 126998)
def set_n2k_configuration_information(msg: Message, manufacturer_information: str, installation_description1: str,
                                      installation_description2: str) -> None:
    raise NotImplementedError()


# TODO: parser
def parse_n2k_pgn_126998(msg: Message) -> ConfigurationInformation:
    raise NotImplementedError()


# ISO Request (PGN 59904)
def set_n2k_pgn_iso_request(msg: Message, destination: int, requested_pgn: int) -> None:
    raise NotImplementedError()


def parse_n2k_pgn_59904(msg: Message) -> int:
    raise NotImplementedError()

# enum tN2kPGNList {N2kpgnl_transmit=0, N2kpgnl_receive=1 };


# PGN List (Transmit and Receive)
def set_n2k_pgn_transmit_list(msg: Message, destination: int, pgns: List[int]):
    raise NotImplementedError()


# Heartbeat (PGN: 126993)
# time_interval_ms: between 10 and 655'320ms
def set_heartbeat(msg: Message, time_interval_ms: int, status_byte: int) -> None:
    raise NotImplementedError()
