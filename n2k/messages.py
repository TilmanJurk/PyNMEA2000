from typing import List, Optional

from n2k.device_information import DeviceInformation
from n2k.n2k import PGN
from n2k.message import Message
from n2k.types import *
from n2k.constants import *
from n2k.utils import IntRef


# System Date/Time (PGN 126992)
def set_n2k_system_time(sid: int, system_date: int, system_time: float,
                        time_source: N2kTimeSource = N2kTimeSource.GPS) -> Message:
    """
    Generate NMEA2000 message containing specified System Date/Time (PGN 126992). System Time is in UTC.
    # TODO: check if seconds since midnight is UTC or timezone specific
    
    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param system_date: Days since 1970-01-01
    :param system_time: seconds since midnight
    :param time_source: Time source, see :py:class:`n2k_types.N2kTimeSource`
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.SystemDateTime
    msg.priority = 3
    msg.add_byte_uint(sid)
    msg.add_byte_uint((time_source & 0x0f) | 0xf0)
    msg.add_2_byte_uint(system_date)
    msg.add_4_byte_double(system_time, 1e-4)
    return msg


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
    index = IntRef(0)
    return SystemTime(
        sid=msg.get_byte_uint(index),
        time_source=N2kTimeSource(msg.get_byte_uint(index) & 0x0f),
        system_date=msg.get_2_byte_uint(index),
        system_time=msg.get_4_byte_udouble(0.0001, index)
    )


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
    msg = Message()
    msg.pgn = PGN.AISSafetyRelatedBroadcastMessage
    msg.priority = 5
    msg.add_byte_uint((repeat & 0x03) << 6 | (message_id & 0x3f))
    msg.add_4_byte_uint(0xc0000000 | (source_id & 0x3fffffff))
    msg.add_byte_uint(0xe0 | (0x1f & ais_transceiver_information))
    msg.add_var_str(safety_related_text)
    return msg


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
    index = IntRef(0)
    vb = msg.get_byte_uint(index)

    return AISSafetyRelatedBroadcast(
        message_id=vb & 0x3f,
        repeat=N2kAISRepeat((vb >> 6) & 0x03),
        source_id=msg.get_4_byte_uint(index) & 0x3fffffff,
        ais_transceiver_information=N2kAISTransceiverInformation(msg.get_byte_uint(index) & 0x1f),
        safety_related_text=msg.get_var_str(index),
    )


# Man Overboard Notification (PGN 127233)
def set_n2k_mob_notification(sid: int, mob_emitter_id: int, mob_status: N2kMOBStatus, activation_time: float,
                             position_source: N2kMOBPositionSource, position_date: int, position_time: float,
                             latitude: float, longitude: float, cog_reference: N2kHeadingReference, cog: float,
                             sog: float, mmsi: int,
                             mob_emitter_battery_status: N2kMOBEmitterBatteryStatus) -> Message:
    """
    Generate NMEA2000 message containing Man Overboard Notification (PGN 127233)
    
    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        for different messages to indicate that they are measured at same time.
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
    msg = Message()
    msg.pgn = PGN.ManOverBoard
    msg.priority = 3
    msg.add_byte_uint(sid)
    msg.add_4_byte_uint(mob_emitter_id)
    msg.add_byte_uint((mob_status & 0x07) | 0xf8)
    msg.add_4_byte_udouble(activation_time, 0.0001)
    msg.add_byte_uint((position_source & 0x07) | 0xf8)
    msg.add_2_byte_uint(position_date)
    msg.add_4_byte_udouble(position_time, 0.0001)
    msg.add_4_byte_double(latitude, 1e-7)
    msg.add_4_byte_double(longitude, 1e-7)
    msg.add_byte_uint((cog_reference & 0x03) | 0xfc)
    msg.add_2_byte_udouble(cog, 0.0001)
    msg.add_2_byte_udouble(sog, 0.01)
    msg.add_4_byte_uint(mmsi)
    msg.add_byte_uint((mob_emitter_battery_status & 0x07) | 0xf8)
    return msg


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
    index = IntRef(0)

    return MOBNotification(
        sid=msg.get_byte_uint(index),
        mob_emitter_id=msg.get_4_byte_uint(index),
        mob_status=N2kMOBStatus(msg.get_byte_uint(index) & 0x07),
        activation_time=msg.get_4_byte_udouble(0.0001, index),
        position_source=N2kMOBPositionSource(msg.get_byte_uint(index) & 0x07),
        position_date=msg.get_2_byte_uint(index),
        position_time=msg.get_4_byte_udouble(0.0001, index),
        latitude=msg.get_4_byte_double(1e-7, index),
        longitude=msg.get_4_byte_double(1e-7, index),
        cog_reference=N2kHeadingReference(msg.get_byte_uint(index) & 0x03),
        cog=msg.get_2_byte_udouble(0.0001, index),
        sog=msg.get_2_byte_udouble(0.01, index),
        mmsi=msg.get_4_byte_uint(index),
        mob_emitter_battery_status=N2kMOBEmitterBatteryStatus(msg.get_byte_uint(index) & 0x07),
    )


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
    msg = Message()
    msg.pgn = PGN.HeadingTrackControl
    msg.priority = 2
    msg.add_byte_uint(
        (rudder_limit_exceeded & 0x03) << 0 |
        (off_heading_limit_exceeded & 0x03) << 2 |
        (off_track_limit_exceeded & 0x03) << 4 |
        (override & 0x03) << 6
    )
    msg.add_byte_uint(
        (steering_mode & 0x07) << 0 |
        (turn_mode & 0x07) << 3 |
        (heading_reference & 0x03) << 6
    )
    msg.add_byte_uint((commanded_rudder_direction & 0x07) << 5 | 0x1f)
    msg.add_2_byte_double(commanded_rudder_angle, 0.0001)
    msg.add_2_byte_udouble(heading_to_steer_course, 0.0001)
    msg.add_2_byte_udouble(track, 0.0001)
    msg.add_2_byte_udouble(rudder_limit, 0.0001)
    msg.add_2_byte_udouble(off_heading_limit, 0.0001)
    msg.add_2_byte_double(radius_of_turn_order, 1)
    msg.add_2_byte_double(rate_of_turn_order, 3.125e-5)
    msg.add_2_byte_double(off_track_limit, 1)
    msg.add_2_byte_udouble(vessel_heading, 0.0001)
    return msg


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
    index = IntRef(0)
    vb = msg.get_byte_uint(index)
    rudder_limit_exceeded = N2kOnOff(vb & 0x03)
    off_heading_limit_exceeded = N2kOnOff((vb >> 2) & 0x03)
    off_track_limit_exceeded = N2kOnOff((vb >> 4) & 0x03)
    override = N2kOnOff((vb >> 6) & 0x03)
    vb = msg.get_byte_uint(index)
    steering_mode = N2kSteeringMode(vb & 0x07)
    turn_mode = N2kTurnMode((vb >> 3) & 0x07)
    heading_reference = N2kHeadingReference((vb >> 6) & 0x03)
    return HeadingTrackControl(
        rudder_limit_exceeded=rudder_limit_exceeded,
        off_heading_limit_exceeded=off_heading_limit_exceeded,
        off_track_limit_exceeded=off_track_limit_exceeded,
        override=override,
        steering_mode=steering_mode,
        turn_mode=turn_mode,
        heading_reference=heading_reference,
        commanded_rudder_direction=N2kRudderDirectionOrder((msg.get_byte_uint(index) >> 5) & 0x07),
        commanded_rudder_angle=msg.get_2_byte_double(0.0001, index),
        heading_to_steer_course=msg.get_2_byte_udouble(0.0001, index),
        track=msg.get_2_byte_udouble(0.0001, index),
        rudder_limit=msg.get_2_byte_udouble(0.0001, index),
        off_heading_limit=msg.get_2_byte_udouble(0.0001, index),
        radius_of_turn_order=msg.get_2_byte_double(1, index),
        rate_of_turn_order=msg.get_2_byte_double(3.125e-5, index),
        off_track_limit=msg.get_2_byte_double(1, index),
        vessel_heading=msg.get_2_byte_udouble(0.0001, index),
    )


# Rudder (PGN 127245)
def set_n2k_rudder(rudder_position: float, instance: int = 0,
                   rudder_direction_order: N2kRudderDirectionOrder = N2kRudderDirectionOrder.NoDirectionOrder,
                   angle_order: float = N2K_DOUBLE_NA) -> Message:
    """
    Rudder
    
    :param rudder_position: Current rudder postion in radians.
    :param instance: Rudder instance.
    :param rudder_direction_order: Direction, where rudder should be turned.
    :param angle_order: Angle where rudder should be turned in radians.
    :return: NMEA2000 Message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.Rudder
    msg.priority = 2
    msg.add_byte_uint(instance)
    msg.add_byte_uint((rudder_direction_order & 0x07) | 0xf8)
    msg.add_2_byte_double(angle_order, 0.0001)
    msg.add_2_byte_double(rudder_position, 0.0001)
    msg.add_byte_uint(0xff)  # reserved
    msg.add_byte_uint(0xff)  # reserved
    return msg


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
    index = IntRef(0)
    return Rudder(
        instance=msg.get_byte_uint(index),
        rudder_direction_order=N2kRudderDirectionOrder(msg.get_byte_uint(index) & 0x07),
        angle_order=msg.get_2_byte_double(0.0001, index),
        rudder_position=msg.get_2_byte_double(0.0001, index)
    )


# Vessel Heading (PGN 127250)
def set_n2k_heading(sid: int, heading: float, deviation: float = N2K_DOUBLE_NA, variation: float = N2K_DOUBLE_NA,
                    ref: N2kHeadingReference = N2kHeadingReference.true) -> Message:
    """
    Vessel Heading (PGN 127250).
    If the true heading is used, leave the deviation and variation undefined. Else if the magnetic heading is sent,
    specify the magnetic deviation and variation.
    
    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        for different messages to indicate that they are measured at same time.
    :param heading: Heading in radians
    :param deviation: Magnetic deviation in radians. Use `N2K_DOUBLE_NA` for undefined value.
    :param variation: Magnetic variation in radians. Use `N2K_DOUBLE_NA` for undefined value.
    :param ref: Heading reference. Can be true or magnetic.
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.VesselHeading
    msg.priority = 2
    msg.add_byte_uint(sid)
    msg.add_2_byte_udouble(heading, 0.0001)
    msg.add_2_byte_double(deviation, 0.0001)
    msg.add_2_byte_double(variation, 0.0001)
    msg.add_byte_uint(0xfc | ref)
    return msg


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

    index = IntRef(0)

    return Heading(
        sid=msg.get_byte_uint(index),
        heading=msg.get_2_byte_udouble(0.0001, index),
        deviation=msg.get_2_byte_double(0.0001, index),
        variation=msg.get_2_byte_double(0.0001, index),
        ref=N2kHeadingReference(msg.get_byte_uint(index) & 0x03)
    )


# Rate of Turn (PGN 127251)
def set_n2k_rate_of_turn(sid: int, rate_of_turn: float) -> Message:
    """
    Rate of Turn (PGN 127251)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        for different messages to indicate that they are measured at same time.
    :param rate_of_turn: Rate of turn in radians per second
    :return:
    """
    msg = Message()
    msg.pgn = PGN.RateOfTurn
    msg.priority = 2
    msg.add_byte_uint(sid)
    msg.add_4_byte_double(rate_of_turn, 3.125E-08)  # 1e-6/32.0
    msg.add_byte_uint(0xff)
    msg.add_2_byte_uint(0xffff)
    return msg


class RateOfTurn(NamedTuple):
    sid: int
    rate_of_turn: float


def parse_n2k_rate_of_turn(msg: Message) -> RateOfTurn:
    index = IntRef(0)
    return RateOfTurn(
        sid=msg.get_byte_uint(index),
        rate_of_turn=msg.get_4_byte_double(3.125E-08, index)  # 1e-6/32.0
    )


# Attitude (PGN 127257)
def set_n2k_attitude(sid: int, yaw: float, pitch: float, roll: float) -> Message:
    """
    Attitude (PGN 127257)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        for different messages to indicate that they are measured at same time.
    :param yaw: Heading in radians.
    :param pitch: Pitch in radians. Positive, when your bow rises.
    :param roll: Roll in radians. Positive, when tilted right.
    :return: NMEA2000 message ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.Attitude
    msg.priority = 3
    msg.add_byte_uint(sid)
    msg.add_2_byte_double(yaw, 0.0001)
    msg.add_2_byte_double(pitch, 0.0001)
    msg.add_2_byte_double(roll, 0.0001)
    msg.add_byte_uint(0xff)  # Reserved
    return msg


class Attitude(NamedTuple):
    sid: int
    yaw: float
    pitch: float
    roll: float


def parse_n2k_attitude(msg: Message) -> Attitude:
    index = IntRef(0)
    return Attitude(
        sid=msg.get_byte_uint(index),
        yaw=msg.get_2_byte_double(0.0001, index),
        pitch=msg.get_2_byte_double(0.0001, index),
        roll=msg.get_2_byte_double(0.0001, index),
    )


# Magnetic Variation (PGN 127258)
def set_n2k_magnetic_variation(sid: int, source: N2kMagneticVariation, days_since_1970: int,
                               variation: float) -> Message:
    """
    Magnetic Variation (PGN 127258)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        for different messages to indicate that they are measured at same time.
    :param source: How the magnetic variation for the current location has been derived
    :param days_since_1970: UTC Date in Days since 1970
    :param variation: Variation in radians, positive values represent Easterly, negative values a Westerly variation.
    :return: NMEA2000 message ready to be sent
    """

    msg = Message()
    msg.pgn = PGN.MagneticVariation
    msg.priority = 6
    msg.add_byte_uint(sid)
    msg.add_byte_uint(source & 0x0f)
    msg.add_2_byte_uint(days_since_1970)
    msg.add_2_byte_double(variation, 0.0001)
    msg.add_2_byte_uint(0xffff)
    return msg


class MagneticVariation(NamedTuple):
    sid: int
    source: N2kMagneticVariation
    days_since_1970: int
    variation: float


def parse_n2k_magnetic_variation(msg: Message) -> MagneticVariation:
    index = IntRef(0)
    return MagneticVariation(
        sid=msg.get_byte_uint(index),
        source=N2kMagneticVariation(msg.get_byte_uint(index) & 0x0f),
        days_since_1970=msg.get_2_byte_uint(index),
        variation=msg.get_2_byte_double(0.0001, index),
    )


# Engine Parameters Rapid (PGN 127488)
def set_n2k_engine_parameters_rapid(engine_instance: int, engine_speed: float, engine_boost_pressure: float,
                                    engine_tilt_trim: int) -> Message:
    """
    Engine Parameters Rapid (PGN 127488)

    :param engine_instance: This field indicates the particular engine for which this
        data applies. A single engine will have an instance of 0. Engines in multi-engine
        boats will be numbered starting at 0 at the bow of the boat incrementing to n going
        in towards the stern of the boat. For engines at the same distance from the bow are
        stern, the engines are numbered starting from the port side and proceeding towards
        the starboard side.
    :param engine_speed: Rotational speed in RPM, stored at a precision of ¼ RPM
    :param engine_boost_pressure: Turbocharger boost pressure in Pascal, stored at a precision of 100 Pa
    :param engine_tilt_trim: Engine tilt or trim (positive or negative) in percent, stored as an integer.
    :return: NMEA2000 message ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.EngineParametersRapid
    msg.priority = 2
    msg.add_byte_uint(engine_instance)
    msg.add_2_byte_udouble(engine_speed, 0.25)
    msg.add_2_byte_udouble(engine_boost_pressure, 100)
    msg.add_byte_uint(engine_tilt_trim)  # TODO: this is proably incorrect and should instead be add_byte_int. Verify with Garmin Display
    msg.add_byte_uint(0xff)  # reserved
    msg.add_byte_uint(0xff)  # reserved
    return msg


class EngineParametersRapid(NamedTuple):
    engine_instance: int
    engine_speed: float
    engine_boost_pressure: float
    engine_tilt_trim: int


def parse_n2k_engine_parameters_rapid(msg: Message) -> EngineParametersRapid:
    index = IntRef(0)
    return EngineParametersRapid(
        engine_instance=msg.get_byte_uint(index),
        engine_speed=msg.get_2_byte_udouble(0.25, index),
        engine_boost_pressure=msg.get_2_byte_udouble(100, index),
        engine_tilt_trim=msg.get_byte_uint(index),  # TODO: see above
    )


# Engine Parameters Dynamic (PGN 127489)
def set_n2k_engine_parameters_dynamic(engine_instance: int, engine_oil_press: float, engine_oil_temp: float,
                                      engine_coolant_temp: float, alternator_voltage: float, fuel_rate: float,
                                      engine_hours: float, engine_coolant_press: float, engine_fuel_press: float,
                                      engine_load: int, engine_torque: int, status1: N2kEngineDiscreteStatus1,
                                      status2: N2kEngineDiscreteStatus2) -> Message:
    """
    Engine Parameters Dynamic (PGN 127489)

    :param engine_instance: This field indicates the particular engine for which this
        data applies. A single engine will have an instance of 0. Engines in multi-engine
        boats will be numbered starting at 0 at the bow of the boat incrementing to n going
        in towards the stern of the boat. For engines at the same distance from the bow are
        stern, the engines are numbered starting from the port side and proceeding towards
        the starboard side.
    :param engine_oil_press: Oil pressure of the engine in Pascal, precision 100Pa
    :param engine_oil_temp: Oil temperature of the engine in degrees Kelvin, precision 0.1°K
    :param engine_coolant_temp: Engine coolant temperature in degrees Kelvin, precision 0.1°K
    :param alternator_voltage: Alternator voltage in Volt, precision 0.01V
    :param fuel_rate: Fuel consumption rate in cubic meters per hour, precision 0.0001 m³/h
    :param engine_hours: Cumulative runtime of the engine in seconds
    :param engine_coolant_press: Engine coolant pressure in Pascal, precision 100 Pa
    :param engine_fuel_press: Fuel pressure in Pascal, precision 1000 Pa
    :param engine_load: Percent engine load, precision 1%
    :param engine_torque: Percent engine torque, precision 1%
    :param status1: Warning conditions part 1
    :param status2: Warning conditions part 2
    :return:
    """
    msg = Message()
    msg.pgn = PGN.EngineParametersDynamic
    msg.priority = 2
    msg.add_byte_uint(engine_instance)
    msg.add_2_byte_udouble(engine_oil_press, 100)
    msg.add_2_byte_udouble(engine_oil_temp, 0.1)
    msg.add_2_byte_udouble(engine_coolant_temp, 0.01)
    msg.add_2_byte_double(alternator_voltage, 0.01)
    msg.add_2_byte_double(fuel_rate, 0.1)
    msg.add_4_byte_udouble(engine_hours, 1)
    msg.add_2_byte_udouble(engine_coolant_press, 100)
    msg.add_2_byte_udouble(engine_fuel_press, 1000)
    msg.add_byte_uint(0xff)  # reserved
    msg.add_2_byte_uint(status1.status)
    msg.add_2_byte_uint(status2.status)
    msg.add_byte_uint(engine_load)
    msg.add_byte_uint(engine_torque)
    return msg


class EngineParametersDynamic(NamedTuple):
    engine_instance: int
    engine_oil_press: float
    engine_oil_temp: float
    engine_coolant_temp: float
    alternator_voltage: float
    fuel_rate: float
    engine_hours: float
    engine_coolant_press: float
    engine_fuel_press: float
    engine_load: int
    engine_torque: int
    status1: N2kEngineDiscreteStatus1
    status2: N2kEngineDiscreteStatus2


def parse_n2k_engine_parameters_dynamic(msg: Message) -> EngineParametersDynamic:
    index = IntRef(0)

    epd = EngineParametersDynamic(
        engine_instance=msg.get_byte_uint(index),
        engine_oil_press=msg.get_2_byte_udouble(100, index),
        engine_oil_temp=msg.get_2_byte_udouble(0.1, index),
        engine_coolant_temp=msg.get_2_byte_udouble(0.01, index),
        alternator_voltage=msg.get_2_byte_double(0.01, index),
        fuel_rate=msg.get_2_byte_double(0.1, index),
        engine_hours=msg.get_4_byte_udouble(1, index),
        engine_coolant_press=msg.get_2_byte_udouble(100, index),
        engine_fuel_press=msg.get_2_byte_udouble(1000, index),
    )
    msg.get_byte_uint(index)
    epd.status1 = N2kEngineDiscreteStatus1(msg.get_2_byte_uint(index))
    epd.status2 = N2kEngineDiscreteStatus2(msg.get_2_byte_uint(index))
    epd.engine_load = msg.get_byte_uint(index)
    epd.engine_torque = msg.get_byte_uint(index)

    return epd


# Transmission parameters, dynamic (PGN 127493)
def set_n2k_transmission_parameters_dynamic(engine_instance: int, transmission_gear: N2kTransmissionGear,
                                            oil_pressure: float, oil_temperature: float,
                                            discrete_status1: N2kTransmissionDiscreteStatus1) -> Message:
    """
    Transmission Parameters, Dynamic (PGN 127493)

    :param engine_instance: This field indicates the particular engine for which this
        data applies. A single engine will have an instance of 0. Engines in multi-engine
        boats will be numbered starting at 0 at the bow of the boat incrementing to n going
        in towards the stern of the boat. For engines at the same distance from the bow are
        stern, the engines are numbered starting from the port side and proceeding towards
        the starboard side.
    :param transmission_gear: The current gear the transmission is in
    :param oil_pressure: Transmission oil pressure in Pascal, precision 100 Pa
    :param oil_temperature: Transmission oil temperature in degrees Kelvin, precision 0.1°K
    :param discrete_status1: Transmission warning conditions.
    :return:
    """
    msg = Message()
    msg.pgn = PGN.TransmissionParameters
    msg.priority = 2
    msg.add_byte_uint(engine_instance)
    msg.add_byte_uint((transmission_gear & 0x03) | 0xfc)
    msg.add_2_byte_udouble(oil_pressure, 100)
    msg.add_2_byte_udouble(oil_temperature, 0.1)
    msg.add_byte_uint(discrete_status1.status)
    msg.add_byte_uint(0xff)  # Reserved
    return msg


class TransmissionParametersDynamic(NamedTuple):
    engine_instance: int
    transmission_gear: N2kTransmissionGear
    oil_pressure: float
    oil_temperature: float
    discrete_status1: N2kTransmissionDiscreteStatus1


def parse_n2k_transmission_parameters_dynamic(msg: Message) -> TransmissionParametersDynamic:
    index = IntRef(0)
    return TransmissionParametersDynamic(
        engine_instance=msg.get_byte_uint(index),
        transmission_gear=N2kTransmissionGear(msg.get_byte_uint(index) & 0x03),
        oil_pressure=msg.get_2_byte_udouble(100, index),
        oil_temperature=msg.get_2_byte_udouble(0.1, index),
        discrete_status1=N2kTransmissionDiscreteStatus1(msg.get_byte_uint(index) & 0x1f)
    )


# Trip Parameters, Engine (PGN 127497)
def set_n2k_trip_parameters_engine(engine_instance: int, trip_fuel_used: float, fuel_rate_average: float,
                                   fuel_rate_economy: float, instantaneous_fuel_economy: float) -> Message:
    """
    Trip Fuel Consumption by Engine (PGN 127497)

    :param engine_instance: This field indicates the particular engine for which this
        data applies. A single engine will have an instance of 0. Engines in multi-engine
        boats will be numbered starting at 0 at the bow of the boat incrementing to n going
        in towards the stern of the boat. For engines at the same distance from the bow are
        stern, the engines are numbered starting from the port side and proceeding towards
        the starboard side.
    :param trip_fuel_used: Fuel used by this engine during the trip in Litres, precision 1L
    :param fuel_rate_average: Fuel used on average by this engine in Litres per hour, precision 0.1L/h
    :param fuel_rate_economy: in Litres per hour, precision 0.1L/h
    :param instantaneous_fuel_economy: in Litres per hour, precision 0.1L/h
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.TripFuelConsumptionEngine
    msg.priority = 2
    msg.add_byte_uint(engine_instance)
    msg.add_2_byte_udouble(trip_fuel_used, 1)
    msg.add_2_byte_double(fuel_rate_average, 0.1)
    msg.add_2_byte_double(fuel_rate_economy, 0.1)
    msg.add_2_byte_double(instantaneous_fuel_economy, 0.1)
    return msg


class TripFuelConsumptionEngine(NamedTuple):
    engine_instance: int
    trip_fuel_used: float
    fuel_rate_averate: float
    fuel_rate_economy: float
    instantaneous_fuel_economy: float


def parse_n2k_trip_parameters_engine(msg: Message) -> TripFuelConsumptionEngine:
    index = IntRef(0)
    return TripFuelConsumptionEngine(
        engine_instance=msg.get_byte_uint(index),
        trip_fuel_used=msg.get_2_byte_udouble(1, index),
        fuel_rate_averate=msg.get_2_byte_double(0.1, index),
        fuel_rate_economy=msg.get_2_byte_double(0.1, index),
        instantaneous_fuel_economy=msg.get_2_byte_double(0.1, index),
    )


N2kBinaryStatus = int


def n2k_get_status_on_binary_status(bank_status: N2kBinaryStatus, item_index: int = 1) -> N2kOnOff:
    """
    Get single status of full binary bank status returned by :py:func:`parse_n2k_binary_status`.
    
    :param bank_status: Full bank status read by :py:func:`parse_n2k_binary_status`
    :param item_index: Status item index 1-28
    :return: single status of full binary bank status
    """
    item_index -= 1
    if item_index > 27:
        return N2kOnOff.Unavailable

    return N2kOnOff((bank_status >> (2 * item_index)) & 0x03)


def n2k_set_status_binary_on_status(bank_status: N2kBinaryStatus, item_status: N2kOnOff,
                                    item_index: int = 1) -> N2kBinaryStatus:
    """
    Set single status to full binary bank status.
    
    :param bank_status: Existing Bank Status
    :param item_status: New Item Status
    :param item_index: Index of Item to be changed
    :return: New Bank Status
    """
    item_index -= 1
    if item_index > 27:
        # TODO: log warning
        return bank_status

    mask = ~(0b11 << (2 * item_index))

    return (bank_status & mask) | item_status << (2 * item_index)


# Binary status report (PGN 127501)
def set_n2k_binary_status_report(device_bank_instance: int, bank_status: N2kBinaryStatus) -> Message:
    """
    Binary Status Report (PGN 127501)

    :param device_bank_instance: Device or Bank Instance
    :param bank_status: Full bank status. Read single status by using :py:func:`n2k_get_status_on_binary_status`
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.BinaryStatusReport
    msg.priority = 3
    msg.add_uint_64((bank_status << 8) | (device_bank_instance & 0xff))
    return msg


class BinaryStatusReport(NamedTuple):
    device_bank_instance: int
    bank_status: N2kBinaryStatus


def parse_n2k_binary_status_report(msg: Message) -> BinaryStatusReport:
    index = IntRef(0)
    vb = msg.get_uint_64(index)
    return BinaryStatusReport(
        device_bank_instance=vb & 0xff,
        bank_status=vb >> 8,
    )


# Fluid level (PGN 127505)
def set_n2k_fluid_level(instance: int, fluid_type: N2kFluidType, level: float, capacity: float) -> Message:
    """
    Fluid Level (PGN 127505)

    :param instance: Tank instance. Different devices handles this a bit differently.
    :param fluid_type: Type of fluid.
    :param level: Tank level in % of full tank, precision 0.004%
    :param capacity: Tank capacity in litres, precision 0.1L
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.priority = 6
    msg.add_byte_uint((instance & 0x0f) | ((fluid_type & 0x0f) << 4))
    msg.add_2_byte_double(level, 0.004)
    msg.add_4_byte_udouble(capacity, 0.1)
    msg.add_byte_uint(0xff)  # Reserved
    return msg


class FluidLevel(NamedTuple):
    instance: int
    fluid_type: N2kFluidType
    level: float
    capacity: float


def parse_n2k_fluid_level(msg: Message) -> FluidLevel:
    index = IntRef(0)
    vb = msg.get_byte_uint(index)

    return FluidLevel(
        instance=vb & 0x0f,
        fluid_type=N2kFluidType((vb >> 4) & 0x0f),
        level=msg.get_2_byte_double(0.004, index),
        capacity=msg.get_4_byte_udouble(0.1, index),
    )


# DC Detailed Status (PGN 127506)
def set_n2k_dc_detailed_status(sid: int, dc_instance: int, dc_type: N2kDCType, state_of_charge: int, state_of_health: int,
                               time_remaining: float, ripple_voltage: float, capacity: float) -> Message:
    """
    DC Detailed Status (PGN 127506)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param dc_instance: DC Source Instance
    :param dc_type: Type of DC Source
    :param state_of_charge: Percent of charge
    :param state_of_health: Percent of health
    :param time_remaining: Time remaining in seconds
    :param ripple_voltage: DC output voltage ripple in Volt
    :param capacity: Battery capacity in coulombs
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.DCDetailedstatus
    msg.priority = 6
    msg.add_byte_uint(sid)
    msg.add_byte_uint(dc_instance)
    msg.add_byte_uint(dc_type)
    msg.add_byte_uint(state_of_charge)
    msg.add_byte_uint(state_of_health)
    msg.add_2_byte_udouble(time_remaining, 60)
    msg.add_2_byte_udouble(ripple_voltage, 0.001)
    msg.add_2_byte_udouble(capacity, 3600)
    return msg


class DCDetailedStatus(NamedTuple):
    sid: int
    dc_instance: int
    dc_type: N2kDCType
    state_of_charge: int
    state_of_health: int
    time_remaining: float
    ripple_voltage: float
    capacity: float


def parse_n2k_dc_detailed_status(msg: Message) -> DCDetailedStatus:
    index = IntRef(0)
    return DCDetailedStatus(
        sid=msg.get_byte_uint(index),
        dc_instance=msg.get_byte_uint(index),
        dc_type=N2kDCType(msg.get_byte_uint(index)),
        state_of_charge=msg.get_byte_uint(index),
        state_of_health=msg.get_byte_uint(index),
        time_remaining=msg.get_2_byte_udouble(60, index),
        ripple_voltage=msg.get_2_byte_udouble(0.001, index),
        capacity=msg.get_2_byte_udouble(3600, index),
    )


# Charger Status (PGN 127507)
def set_n2k_charger_status(instance: int, battery_instance: int, charge_state: N2kChargeState,
                           charger_mode: N2kChargerMode, enabled: N2kOnOff, equalization_pending: N2kOnOff,
                           equalization_time_remaining: float) -> Message:
    """
    Charger Status (PGN 127507)

    :param instance: Charger Instance
    :param battery_instance: Battery Instance
    :param charge_state: Operating State
    :param charger_mode: Charger Mode
    :param enabled: Yes/No
    :param equalization_pending: Yes/No
    :param equalization_time_remaining: in seconds, precision 1s
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.ChargerStatus
    msg.priority = 6
    msg.add_byte_uint(instance)
    msg.add_byte_uint(battery_instance)
    msg.add_byte_uint((charger_mode & 0x0f) << 4 | (charge_state & 0x0f))
    msg.add_byte_uint(0x0f << 4 | (equalization_pending & 0x03) << 2 | (enabled & 0x03))
    msg.add_2_byte_udouble(equalization_time_remaining, 1)
    return msg


class ChargerStatus(NamedTuple):
    instance: int
    battery_instance: int
    charge_state: N2kChargeState
    charger_mode: N2kChargerMode
    enabled: N2kOnOff
    equalization_pending: N2kOnOff
    equalization_time_remaining: float


def parse_n2k_charger_status(msg: Message) -> ChargerStatus:
    index = IntRef(0)

    instance = msg.get_byte_uint(index)
    battery_instance = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    charge_state = N2kChargeState(vb & 0x0f)
    charger_mode = N2kChargerMode((vb >> 4) & 0x0f)
    vb = msg.get_byte_uint(index)
    enabled = N2kOnOff(vb & 0x03)
    equalization_pending = N2kOnOff((vb >> 2) & 0x03)
    equalization_time_remaining = msg.get_2_byte_double(60, index)

    return ChargerStatus(
        instance=instance,
        battery_instance=battery_instance,
        charge_state=charge_state,
        charger_mode=charger_mode,
        enabled=enabled,
        equalization_pending=equalization_pending,
        equalization_time_remaining=equalization_time_remaining,
    )


# Battery Status (PGN 127508)
def set_n2k_battery_status(battery_instance: int, battery_voltage: float, battery_current: float,
                           battery_temperature: float, sid: int) -> Message:
    """
    Battery Status (PGN 127508)

    :param battery_instance: Battery Instance
    :param battery_voltage: Battery Voltage in Volt, precision 0.01V
    :param battery_current: Battery Current in Ampere, precision 0.1A
    :param battery_temperature: Battery Temperature in Kelvin, precision 0.01K
    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.BatteryStatus
    msg.priority = 6
    msg.add_byte_uint(battery_instance)
    msg.add_2_byte_double(battery_voltage, 0.01)
    msg.add_2_byte_double(battery_current, 0.1)
    msg.add_2_byte_udouble(battery_temperature, 0.01)
    msg.add_byte_uint(sid)
    return msg


class BatteryStatus(NamedTuple):
    battery_instance: int
    battery_voltage: float
    battery_current: float
    battery_temperature: float
    sid: int


def parse_n2k_battery_status(msg: Message) -> BatteryStatus:
    index = IntRef(0)
    return BatteryStatus(
        battery_instance=msg.get_byte_uint(index),
        battery_voltage=msg.get_2_byte_double(0.01, index),
        battery_current=msg.get_2_byte_double(0.1, index),
        battery_temperature=msg.get_2_byte_udouble(0.01, index),
        sid=msg.get_byte_uint(index),
    )


# Battery Configuration Status (PGN 127513)
def set_n2k_battery_configuration_status(battery_instance: int, battery_type: N2kBatType,
                                         supports_equal: N2kBatEqSupport, battery_nominal_voltage: N2kBatNomVolt,
                                         battery_chemistry: N2kBatChem, battery_capacity: float,
                                         battery_temperature_coefficient: int, peukert_exponent: float,
                                         charge_efficiency_factor: int) -> Message:
    """
    Battery Configuration Status (PGN 127513)

    :param battery_instance: Battery Instance
    :param battery_type: Battery Type, see type
    :param supports_equal: Whether the battery supports equalization
    :param battery_nominal_voltage: Battery nominal voltage, see type
    :param battery_chemistry: Battery chemistry, see type
    :param battery_capacity: Battery capacity in Coulombs (aka Ampere Seconds), stored at a precision of 1Ah
    :param battery_temperature_coefficient: Battery temperature coefficient in %
    :param peukert_exponent: Peukert Exponent, describing the relation between discharge rate and effective capacity.
        Value between 1.0 and 1.504
    :param charge_efficiency_factor: Charge efficiency factor
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.BatteryConfigurationStatus
    msg.priority = 6
    msg.add_byte_uint(battery_instance)
    msg.add_byte_uint(0xc0 | ((supports_equal & 0x03) << 4) | (battery_type & 0x0f))  # BatType (4 bit), SupportsEqual (2 bit), Reserved (2 bit)
    msg.add_byte_uint(((battery_chemistry & 0x0f) << 4) | (battery_nominal_voltage & 0x0f))
    msg.add_2_byte_double(battery_capacity, 3600)
    msg.add_byte_uint(battery_temperature_coefficient)
    # Original code was unsure if this is correct.
    # I am fairly certain it is as the exponent can't be better than 1 and shouldn't be worse than 1.5
    peukert_exponent -= 1
    if peukert_exponent < 0 or peukert_exponent > 0.504:
        msg.add_byte_uint(0xff)
    else:
        msg.add_1_byte_udouble(peukert_exponent, 0.002, -1)
    msg.add_byte_uint(charge_efficiency_factor)
    return msg


class BatteryConfigurationStatus(NamedTuple):
    battery_instance: int
    battery_type: N2kBatType
    supports_equal: N2kBatEqSupport
    battery_nominal_voltage: N2kBatNomVolt
    battery_chemistry: N2kBatChem
    battery_capacity: float
    battery_temperature_coefficient: int
    peukert_exponent: float
    charge_efficiency_factor: int


def parse_n2k_battery_configuration_status(msg: Message) -> BatteryConfigurationStatus:
    index = IntRef(0)

    battery_instance = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    battery_type = N2kBatType(vb & 0x0f)
    supports_equal = N2kBatEqSupport((vb >> 4) & 0x03)
    vb = msg.get_byte_uint(index)
    battery_nominal_voltage = N2kBatNomVolt(vb & 0x0f)
    battery_chemistry = N2kBatChem((vb >> 4) & 0x0f)

    return BatteryConfigurationStatus(
        battery_instance=battery_instance,
        battery_type=battery_type,
        supports_equal=supports_equal,
        battery_nominal_voltage=battery_nominal_voltage,
        battery_chemistry=battery_chemistry,
        battery_capacity=msg.get_2_byte_double(3600, index),
        battery_temperature_coefficient=msg.get_byte_uint(index),
        peukert_exponent=msg.get_1_byte_udouble(0.002, index) + 1,
        charge_efficiency_factor=msg.get_byte_uint(index),
    )


# Leeway (PGN 128000)
def set_n2k_leeway(sid: int, leeway: float) -> Message:
    """
    Leeway (PGN 128000)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param leeway: Positive angles indicate slippage to starboard, that is, the vessel is tracking to the right of its
        heading, and negative angles indicate slippage to port. Angle in radians, stored at a precision of 0.0001rad
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.Leeway
    msg.priority = 4
    msg.add_byte_uint(sid)
    msg.add_2_byte_double(leeway, 0.0001)
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    return msg


class Leeway(NamedTuple):
    sid: int
    leeway: float


def parse_n2k_leeway(msg: Message) -> Leeway:
    index = IntRef(0)

    return Leeway(
        sid=msg.get_byte_uint(index),
        leeway=msg.get_2_byte_double(0.0001, index)
    )


# Boat Speed (PGN 128259)
def set_n2k_boat_speed(sid: int, water_referenced: float, ground_referenced: float,
                       swrt: N2kSpeedWaterReferenceType) -> Message:
    """
    Boat Speed (PGN 128259)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param water_referenced: Speed through the water in meters per second, precision 0.01m/s
    :param ground_referenced: Speed over ground in meters per second, precision 0.01m/s
    :param swrt: Type of transducer for the water referenced speed, see type
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.BoatSpeed
    msg.priority = 2
    msg.add_byte_uint(sid)
    msg.add_2_byte_udouble(water_referenced, 0.01)
    msg.add_2_byte_udouble(ground_referenced, 0.01)
    msg.add_byte_uint(swrt)
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    return msg


class BoatSpeed(NamedTuple):
    sid: int
    water_referenced: float
    ground_referenced: float
    swrt: N2kSpeedWaterReferenceType


def parse_n2k_boat_speed(msg: Message) -> BoatSpeed:
    index = IntRef(0)
    return BoatSpeed(
        sid=msg.get_byte_uint(index),
        water_referenced=msg.get_2_byte_udouble(0.01, index),
        ground_referenced=msg.get_2_byte_udouble(0.01, index),
        swrt=N2kSpeedWaterReferenceType(msg.get_byte_uint(index)),
    )


# Water depth (PGN 128267)
def set_n2k_water_depth(sid: int, depth_below_transducer: float, offset: float, max_range: float) -> Message:
    """
    Water Depth (PGN 128267)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param depth_below_transducer: Water depth below transducer in meters, precision 0.01m
    :param offset: Distance in meters between transducer and water surface (positive) or transducer and keel (negative),
        precision 0.001m
    :param max_range: maximum depth that can be measured
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.WaterDepth,
    msg.priority = 3
    msg.add_byte_uint(sid)
    msg.add_4_byte_udouble(depth_below_transducer, 0.01)
    msg.add_2_byte_double(offset, 0.001)
    msg.add_1_byte_udouble(max_range, 10)
    return msg


class WaterDepth(NamedTuple):
    sid: int
    depth_below_transducer: float
    offset: float
    max_range: float


def parse_n2k_water_depth(msg: Message) -> WaterDepth:
    index = IntRef(0)
    return WaterDepth(
        sid=msg.get_byte_uint(index),
        depth_below_transducer=msg.get_4_byte_udouble(0.01, index),
        offset=msg.get_2_byte_double(0.001, index),
        max_range=msg.get_1_byte_udouble(10, index),
    )


# Distance log (PGN 128275)
def set_n2k_distance_log(days_since_1970: int, seconds_since_midnight: float, log: int, trip_log: int) -> Message:
    """
    Distance Log (PGN 128275)

    :param days_since_1970: Days since 1.1.1970 UTC
    :param seconds_since_midnight: Seconds since midnight, stored at a precision of 0.0001s (TODO: UTC?)
    :param log: Total distance traveled through the water since the installation of the device in meters.
    :param trip_log: Total distance traveled through the water since the last trip reset in meters.
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.DistanceLog
    msg.priority = 6
    msg.add_2_byte_uint(days_since_1970)
    msg.add_4_byte_udouble(seconds_since_midnight, 0.0001)
    msg.add_4_byte_uint(log)
    msg.add_4_byte_uint(trip_log)
    return msg


class DistanceLog(NamedTuple):
    days_since_1970: int
    seconds_since_midnight: float
    log: int
    trip_log: int


def parse_n2k_distance_log(msg: Message) -> DistanceLog:
    index = IntRef(0)
    return DistanceLog(
        days_since_1970=msg.get_2_byte_uint(index),
        seconds_since_midnight=msg.get_4_byte_udouble(0.0001, index),
        log=msg.get_4_byte_uint(index),
        trip_log=msg.get_4_byte_uint(index),
    )


# Anchor Windlass Control Status (PGN 128776)
def set_n2k_anchor_windlass_control_status(
        sid: int,
        windlass_identifier: int,
        windlass_direction_control: N2kWindlassDirectionControl,
        speed_control: int,
        speed_control_type: N2kSpeedType,
        anchor_docking_control: N2kGenericStatusPair,
        power_enable: N2kGenericStatusPair,
        mechanical_lock: N2kGenericStatusPair,
        deck_and_anchor_wash: N2kGenericStatusPair,
        anchor_light: N2kGenericStatusPair,
        command_timeout: float,
        windlass_control_events: N2kWindlassControlEvents,
    ) -> Message:
    """
    Anchor Windlass Control Status (PGN 128776)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param windlass_identifier: Windlass Identifier
    :param windlass_direction_control: Windlass Direction, see type
    :param speed_control: Single Speed: 0=off, 1-100=on\n
        Dual Speed: 0=0ff, 1-49=slow, 50-100=fast\n
        Proportional speed: 0=off, 1-100=speed
    :param speed_control_type: Speed control type, Single, Dual or Proportional
    :param anchor_docking_control: Anchor Docking Control, Yes/No
    :param power_enable: Power Enable, Yes/No
    :param mechanical_lock: Mechanical Lock, Yes/No
    :param deck_and_anchor_wash: Deck and Anchor Wash, Yes/No
    :param anchor_light: Anchor Light, Yes/No
    :param command_timeout: Command Timeout. Range 0.0 to 1.275 seconds, precision 0.005s
    :param windlass_control_events: Windlass Control Events, see type
    :return:
    """
    msg = Message()
    msg.pgn = PGN.AnchorWindlassControlStatus
    msg.priority = 2
    msg.add_byte_uint(sid)
    msg.add_byte_uint(windlass_identifier)
    msg.add_byte_uint(
        0x03 << 6 |
        (speed_control_type & 0x03) << 4 |
        (anchor_docking_control & 0x03) << 2 |
        windlass_direction_control & 0x03
    )
    msg.add_byte_uint(speed_control)
    msg.add_byte_uint(
        (anchor_light & 0x03) << 6 |
        (deck_and_anchor_wash & 0x03) << 4 |
        (mechanical_lock & 0x03) << 2 |
        power_enable & 0x03
    )
    msg.add_1_byte_udouble(command_timeout, 0.005)
    msg.add_byte_uint(windlass_control_events.events)
    return msg


class AnchorWindlassControlStatus(NamedTuple):
    sid: int
    windlass_identifier: int
    windlass_direction_control: N2kWindlassDirectionControl
    speed_control: int
    speed_control_type: N2kSpeedType
    anchor_docking_control: N2kGenericStatusPair
    power_enable: N2kGenericStatusPair
    mechanical_lock: N2kGenericStatusPair
    deck_and_anchor_wash: N2kGenericStatusPair
    anchor_light: N2kGenericStatusPair
    command_timeout: float
    windlass_control_events: N2kWindlassControlEvents


def parse_n2k_anchor_windlass_control_status(msg: Message) -> AnchorWindlassControlStatus:
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    windlass_identifier = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    windlass_direction_control = N2kWindlassDirectionControl(vb & 0x03)
    anchor_docking_control = N2kGenericStatusPair((vb >> 2) & 0x03)
    speed_control_type = N2kSpeedType((vb >> 4) & 0x03)
    speed_control = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    power_enable = N2kGenericStatusPair(vb & 0x03)
    mechanical_lock = N2kGenericStatusPair((vb >> 2) & 0x03)
    deck_and_anchor_wash = N2kGenericStatusPair((vb >> 4) & 0x03)
    anchor_light = N2kGenericStatusPair((vb >> 6) & 0x03)
    command_timeout = msg.get_1_byte_udouble(0.005, index)
    windlass_control_events = N2kWindlassControlEvents(msg.get_byte_uint(index))

    return AnchorWindlassControlStatus(
        sid=sid,
        windlass_identifier=windlass_identifier,
        windlass_direction_control=windlass_direction_control,
        speed_control=speed_control,
        speed_control_type=speed_control_type,
        anchor_docking_control=anchor_docking_control,
        power_enable=power_enable,
        mechanical_lock=mechanical_lock,
        deck_and_anchor_wash=deck_and_anchor_wash,
        anchor_light=anchor_light,
        command_timeout=command_timeout,
        windlass_control_events=windlass_control_events,
    )


# Anchor Windlass Operating Status (PGN 128777)
def set_n2k_anchor_windlass_operating_status(
        sid: int, windlass_identifier: int, rode_counter_value: float,
        windlass_line_speed: float,
        windlass_motion_status: N2kWindlassMotionStates = N2kWindlassMotionStates.Unavailable,
        rode_type_status: N2kRodeTypeStates = N2kRodeTypeStates.Unavailable,
        anchor_docking_status: N2kAnchorDockingStates = N2kAnchorDockingStates.DataNotAvailable,
        windlass_operating_events: N2kWindlassOperatingEvents = N2kWindlassOperatingEvents()
    ) -> Message:
    """
    Anchor Windlass Operating Status (PGN 128777)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param windlass_identifier: Identifier of the windlass instance
    :param rode_counter_value: Amount of rode deployed, in metres
    :param windlass_line_speed: Deployment speed in metres per second
    :param windlass_motion_status: see type
    :param rode_type_status: see type
    :param anchor_docking_status: see type
    :param windlass_operating_events: see type
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AnchorWindlassOperatingStatus
    msg.add_byte_uint(sid)
    msg.add_byte_uint(windlass_identifier)
    msg.add_byte_uint(0xf0 | ((rode_type_status & 0x03) << 2) | (windlass_motion_status & 0x03))
    msg.add_2_byte_udouble(rode_counter_value, 0.1)
    msg.add_2_byte_udouble(windlass_line_speed, 0.01)
    msg.add_byte_uint((windlass_operating_events.event << 2) | (anchor_docking_status & 0x03))
    return msg


class AnchorWindlassOperatingStatus(NamedTuple):
    sid: int
    windlass_identifier: int
    rode_counter_value: float
    windlass_line_speed: float
    windlass_motion_status: N2kWindlassMotionStates
    rode_type_status: N2kRodeTypeStates
    anchor_docking_status: N2kAnchorDockingStates
    windlass_operating_events: N2kWindlassOperatingEvents


def parse_n2k_anchor_windlass_operating_status(msg: Message) -> AnchorWindlassOperatingStatus:
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    windlass_identifier = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)
    windlass_motion_status = N2kWindlassMotionStates(vb & 0x03)
    rode_type_status = N2kRodeTypeStates((vb >> 2) & 0x03)
    rode_counter_value = msg.get_2_byte_udouble(0.1, index)
    windlass_line_speed = msg.get_2_byte_udouble(0.01, index)
    vb = msg.get_byte_uint(index)
    anchor_docking_status = N2kAnchorDockingStates(vb & 0x03)
    windlass_operating_events = N2kWindlassOperatingEvents(vb >> 2)
    return AnchorWindlassOperatingStatus(
        sid=sid,
        windlass_identifier=windlass_identifier,
        rode_counter_value=rode_counter_value,
        windlass_line_speed=windlass_line_speed,
        windlass_motion_status=windlass_motion_status,
        rode_type_status=rode_type_status,
        anchor_docking_status=anchor_docking_status,
        windlass_operating_events=windlass_operating_events,
    )


# Anchor Windlass Monitoring Status (PGN 128778)
def set_n2k_anchor_windlass_monitoring_status(
        sid: int,
        windlass_identifier: int,
        total_motor_time: float,
        controller_voltage: float = N2K_DOUBLE_NA,
        motor_current: float = N2K_DOUBLE_NA,
        windlass_monitoring_events: N2kWindlassMonitoringEvents = N2kWindlassMonitoringEvents()
    ) -> Message:
    """
    Anchor Windlass Monitoring Status (PGN 128778)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param windlass_identifier: Identifier of the windlass instance
    :param total_motor_time: Total runtime of the motor in seconds
    :param controller_voltage: Voltage in Volts, precision 0.2V
    :param motor_current: Current in Amperes, precision 1A
    :param windlass_monitoring_events: see type
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AnchorWindlassMonitoringStatus
    msg.priority = 2
    msg.add_byte_uint(sid)
    msg.add_byte_uint(windlass_identifier)
    msg.add_byte_uint(windlass_monitoring_events.events)
    msg.add_1_byte_udouble(controller_voltage, 0.2)
    msg.add_1_byte_udouble(motor_current, 1.0)
    msg.add_2_byte_udouble(total_motor_time, 60.0)
    msg.add_byte_uint(0xff)
    return msg


class AnchorWindlassMonitoringStatus(NamedTuple):
    sid: int
    windlass_identifier: int
    total_motor_time: float
    controller_voltage: float
    motor_current: float
    windlass_monitoring_events: N2kWindlassMonitoringEvents


def parse_n2k_anchor_windlass_monitoring_status(msg: Message) -> AnchorWindlassMonitoringStatus:
    index = IntRef(0)

    return AnchorWindlassMonitoringStatus(
        sid=msg.get_byte_uint(index),
        windlass_identifier=msg.get_byte_uint(index),
        windlass_monitoring_events=N2kWindlassMonitoringEvents(msg.get_byte_uint(index)),
        controller_voltage=msg.get_1_byte_udouble(0.2, index),
        motor_current=msg.get_1_byte_udouble(1.0, index),
        total_motor_time=msg.get_2_byte_udouble(60.0, index),
    )


# Lat/lon rapid (PGN 129025)
def set_n2k_lat_long_rapid(latitude: float, longitude: float) -> Message:
    """
    Position rapid update (PGN 129025)

    :param latitude: Latitude in degrees, precision approx 1.1cm (1e-7 deg)
    :param longitude: Longitude in degrees, precision approx 1.1cm at the equator (1e-7 deg)
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.LatLonRapid
    msg.priority = 2
    msg.add_4_byte_double(latitude, 1e-7)
    msg.add_4_byte_double(longitude, 1e-7)
    return msg


class LatLonRapid(NamedTuple):
    latitude: float
    longitude: float


def parse_n2k_lat_long_rapid(msg: Message) -> LatLonRapid:
    index = IntRef(0)

    return LatLonRapid(
        latitude=msg.get_4_byte_double(1e-7, index),
        longitude=msg.get_4_byte_double(1e-7, index),
    )


# COG SOG rapid (PGN 129026)
def set_n2k_cog_sog_rapid(sid: int, heading_reference: N2kHeadingReference, cog: float, sog: float) -> Message:
    """
    Course and Speed over Ground, rapid update (PGN 129026)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param heading_reference: Course over Ground reference, see type
    :param cog: Course over Ground in radians, precision 0.0001rad
    :param sog: Speed over Ground in meters per second, precision 0.01m/s
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.CogSogRapid
    msg.priority = 2
    msg.add_byte_uint(sid)
    msg.add_byte_uint((heading_reference & 0x03) | 0xfc)
    msg.add_2_byte_udouble(cog, 0.0001)  # Radians
    msg.add_2_byte_udouble(sog, 0.01)  # Meters per second
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    return msg


class CogSogRapid(NamedTuple):
    sid: int
    heading_reference: N2kHeadingReference
    cog: float
    sog: float


def parse_n2k_cog_sog_rapid(msg: Message) -> CogSogRapid:
    index = IntRef(0)

    return CogSogRapid(
        sid=msg.get_byte_uint(index),
        heading_reference=N2kHeadingReference(msg.get_byte_uint(index) & 0x03),
        cog=msg.get_2_byte_udouble(0.0001, index),
        sog=msg.get_2_byte_udouble(0.01, index),
    )


# GNSS Position Data (PGN 129029)
# TODO: check if seconds since midnight is UTC or timezone specific
def set_n2k_gnss_data(sid: int, days_since_1970: int, seconds_since_midnight: float,
                      latitude: float, longitude: float, altitude: float,
                      gnss_type: N2kGNSSType, gnss_method: N2kGNSSMethod, n_satellites: int, hdop: float, pdop: float,
                      geoidal_separation: float, n_reference_station: int, reference_station_type: Optional[N2kGNSSType],
                      reference_station_id: Optional[int], age_of_correction: Optional[float]) -> Message:
    """
    GNSS Position Data (PGN 129029)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param days_since_1970: Days since 1.1.1970 UTC
    :param seconds_since_midnight: Seconds since midnight, stored at a precision of 0.0001s (TODO: UTC?)
    :param latitude: Latitude in degrees, precision approx 11 pico metre
        (a fifth of the diameter of a helium atom, 1e-16 deg). Negative values indicate south, positive indicate north.
    :param longitude: Longitude in degrees, precision approx 11 pico metre at the equator (1e-16 deg).
        Negative values indicate west, positive indicate east.
    :param altitude: Altitude in reference to the WGS-84 model in metres, precision 1 micrometer.
    :param gnss_type: GNSS Type, see type
    :param gnss_method: GNSS Method type, see type
    :param n_satellites: Number of satellites used for the provided data
    :param hdop: Horizontal Dilution Of Precision in meters, precision 0.01m
    :param pdop: Positional Dilution Of Precision in meters, precision 0.01m
    :param geoidal_separation: Geoidal separation in meters, precision 0.01m
    :param n_reference_station: Number of Reference Stations
    :param reference_station_type: Reference Station type, see type
    :param reference_station_id: Reference Station ID
    :param age_of_correction: Age of DGNSS Correction
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.GNSSPositionData
    msg.priority = 3
    msg.add_byte_uint(sid)
    msg.add_2_byte_uint(days_since_1970)
    msg.add_4_byte_udouble(seconds_since_midnight, 0.0001)
    msg.add_8_byte_double(latitude, 1e-16)
    msg.add_8_byte_double(longitude, 1e-16)
    msg.add_8_byte_double(altitude, 1e-6)
    msg.add_byte_uint((gnss_type & 0x0f) | (gnss_method & 0x0f) << 4)
    msg.add_byte_uint(1 | 0xfc)  # Integrity byte, reserved 6 bits
    msg.add_byte_uint(n_satellites)
    msg.add_2_byte_double(hdop, 0.01)
    msg.add_2_byte_double(pdop, 0.01)
    msg.add_4_byte_double(geoidal_separation, 0.01)
    if 0 < n_reference_station < 0xff:
        msg.add_byte_uint(1)  # Note that we have values for only one reference station, so pass only one values.
        msg.add_2_byte_int((reference_station_type & 0x0f) | reference_station_id << 4)
        msg.add_2_byte_udouble(age_of_correction, 0.01)
    else:
        msg.add_byte_uint(n_reference_station)
    return msg


class GNSSPositionData(NamedTuple):
    sid: int
    days_since_1970: int
    seconds_since_midnight: float
    latitude: float
    longitude: float
    altitude: float
    gnss_type: N2kGNSSType
    gnss_method: N2kGNSSMethod
    n_satellites: int
    hdop: float
    pdop: float
    geoidal_separation: float
    n_reference_station: int
    reference_station_type: Optional[N2kGNSSType]
    reference_station_id: Optional[int]
    age_of_correction: Optional[float]


def parse_n2k_gnss_data(msg: Message) -> GNSSPositionData:
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    days_since_1970 = msg.get_2_byte_uint(index)
    seconds_since_midnight = msg.get_4_byte_udouble(0.0001, index)
    latitude = msg.get_8_byte_double(1e-16, index)
    longitude = msg.get_8_byte_double(1e-16, index)
    altitude = msg.get_8_byte_double(1e-6, index)
    vb = msg.get_byte_uint(index)
    gnss_type = N2kGNSSType(vb & 0x0f)
    gnss_method = N2kGNSSMethod((vb >> 4) & 0x0f)
    vb = msg.get_byte_uint(index)  # Integrity 2 bit + reserved 6 bit
    n_satellites = msg.get_byte_uint(index)
    hdop = msg.get_2_byte_double(0.01, index)
    pdop = msg.get_2_byte_double(0.01, index)
    geoidal_separation = msg.get_4_byte_double(0.01, index)
    n_reference_stations = msg.get_byte_uint(index)
    reference_station_type = None
    reference_station_id = None
    age_of_correction = None
    if 0 < n_reference_stations < N2K_UINT8_NA:
        # Note that we return real number of stations, but we only have variables for one.
        vi = msg.get_2_byte_uint(index)
        reference_station_type = N2kGNSSType(vi & 0x0f)
        reference_station_id = vi >> 4
        age_of_correction = msg.get_2_byte_udouble(0.01, index)

    return GNSSPositionData(
        sid,
        days_since_1970,
        seconds_since_midnight,
        latitude,
        longitude,
        altitude,
        gnss_type,
        gnss_method,
        n_satellites,
        hdop,
        pdop,
        geoidal_separation,
        n_reference_stations,
        reference_station_type,
        reference_station_id,
        age_of_correction,
    )


# Date,Time & Local offset (PGN 129033, see also PGN 126992)
def set_n2k_date_time_local_offset(days_since_1970: int, seconds_since_midnight: float, local_offset: int) -> Message:
    """
    Date, Time & Local offset (PGN 129033), see also PGN 126992

    :param days_since_1970: Days since 1.1.1970 UTC
    :param seconds_since_midnight: Seconds since midnight, stored at a precision of 0.0001s (TODO: UTC?)
    :param local_offset: Local offset in minutes
    :return:
    """
    msg = Message()
    msg.pgn = PGN.DateTimeLocalOffset
    msg.priority = 3
    msg.add_2_byte_uint(days_since_1970)
    msg.add_4_byte_udouble(seconds_since_midnight, 0.0001)
    msg.add_2_byte_int(local_offset)
    return msg


class DateTimeLocalOffset(NamedTuple):
    days_since_1970: int
    seconds_since_midnight: float
    local_offset: int


def parse_n2k_date_time_local_offset(msg: Message) -> DateTimeLocalOffset:
    index = IntRef(0)

    return DateTimeLocalOffset(
        days_since_1970=msg.get_2_byte_uint(index),
        seconds_since_midnight=msg.get_4_byte_udouble(0.0001, index),
        local_offset=msg.get_2_byte_int(index),
    )


# AIS position reports for Class A (PGN 129038)
def set_n2k_ais_class_a_position(message_id: int, repeat: N2kAISRepeat, user_id: int, latitude: float, longitude: float,
                                 accuracy: bool, raim: bool, seconds: int, cog: float, sog: float, heading: float,
                                 rot: float, nav_status: N2kAISNavStatus) -> Message:
    """
    AIS Position Reports for Class A (PGN 129038)

    :param message_id: Message Type ID according to https://www.itu.int/rec/R-REC-M.1371
    :param repeat: Repeat indicator, Used by the repeater to indicate how many times a message has been repeated.
    :param user_id: MMSI Number
    :param latitude: Latitude in degrees, precision approx 1.1cm (1e-7 deg)
    :param longitude: Longitude in degrees, precision approx 1.1cm at the equator (1e-7 deg)
    :param accuracy: Position accuracy, 0 = low (> 10m), 1 = high (≤ 10m)
    :param raim: Receiver autonomous integrity monitoring (RAIM) flag of the electronic position fixing device.
    :param seconds: UTC second when the report was generated by the EPFS (0-59).\n
        60: timestamp not available, default\n
        61: positioning system in manual input mode\n
        62: electronic position fixing system operates in estimated (dead reckoning) mode\n
        63: positioning system is inoperative
    :param cog: Course over Ground in radians, precision 0.0001rad
    :param sog: Speed over Ground in meters per second, precision 0.01m/s
    :param heading: Compass heading
    :param rot: Rate of Turn
    :param nav_status: Navigational status
    :return: NMEA2000 Messag, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.AISClassAPositionReport
    msg.priority = 4
    msg.add_byte_uint((repeat & 0x03) << 6 | (message_id & 0x3f))
    msg.add_4_byte_uint(user_id)
    msg.add_4_byte_double(longitude, 1e-7)
    msg.add_4_byte_double(latitude, 1e-7)
    msg.add_byte_uint((seconds & 0x3f) << 2 | (raim & 0x01) << 1 | (accuracy & 0x01))
    msg.add_2_byte_udouble(cog, 1e-4)
    msg.add_2_byte_udouble(sog, 0.01)
    msg.add_byte_uint(0xff)  # Communication State (19 bits)
    msg.add_byte_uint(0xff)
    msg.add_byte_uint(0xff)  # AIS transceiver information (5 bits)
    msg.add_2_byte_udouble(heading, 1e-4)
    msg.add_2_byte_double(rot, 3.125e-5)  # 1e-3/32.0
    msg.add_byte_uint(0xf0 | (nav_status & 0x0f))
    msg.add_byte_uint(0xff)  # reserved
    return msg


class AISClassAPositionReport(NamedTuple):
    message_id: int
    repeat: N2kAISRepeat
    user_id: int
    latitude: float
    longitude: float
    accuracy: bool
    raim: bool
    seconds: int
    cog: float
    sog: float
    heading: float
    rot: float
    nav_status: N2kAISNavStatus


def parse_n2k_ais_class_a_position(msg: Message) -> AISClassAPositionReport:
    index = IntRef(0)

    vb = msg.get_byte_uint(index)
    message_id = vb & 0x3f
    repeat = N2kAISRepeat((vb >> 6) & 0x03)
    user_id = msg.get_byte_uint(index)
    longitude = msg.get_4_byte_double(1e-7, index)
    latitude = msg.get_4_byte_double(1e-7, index)
    vb = msg.get_byte_uint(index)
    accuracy = bool(vb & 0x01)
    raim = bool((vb >> 1) & 0x01)
    seconds = (vb >> 2) & 0x3f
    cog = msg.get_2_byte_udouble(1e-4, index)
    sog = msg.get_2_byte_udouble(0.01, index)
    msg.get_byte_uint(index)  # Communication State (19 bits)
    msg.get_byte_uint(index)
    msg.get_byte_uint(index)  # AIS tranceiver information (5 bits)
    heading = msg.get_2_byte_udouble(1e-4, index)
    rot = msg.get_2_byte_double(3.125e-5, index)
    vb = msg.get_byte_uint(index)
    nav_status = N2kAISNavStatus(vb & 0x03)

    return AISClassAPositionReport(
        message_id=message_id,
        repeat=repeat,
        user_id=user_id,
        longitude=longitude,
        latitude=latitude,
        accuracy=accuracy,
        raim=raim,
        seconds=seconds,
        cog=cog,
        sog=sog,
        heading=heading,
        rot=rot,
        nav_status=nav_status,
    )


# AIS position reports for Class B (PGN 129039)
# TODO


# AIS Aids to Navigation (AtoN) Report (PGN 129041)
# TODO


# Cross Track Error (PGN 129283)
# TODO


# Navigation info (PGN 129284)
# TODO !!!


# Route/WP information (PGN 129285)
# TODO


# GNSS DOP data (PGN 129539)
def set_n2k_gnss_dop(sid: int, desired_mode: N2kGNSSDOPmode, actual_mode: N2kGNSSDOPmode, hdop: float, vdop: float,
                     tdop: float) -> Message:
    """
    GNSS DOP Data (PGN 129539)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param desired_mode: Desired DOP Mode
    :param actual_mode: Actual DOP Mode
    :param hdop: Horizontal Dilution of Precision in meters.
    :param vdop: Vertical Dilution of Precision in meters.
    :param tdop: Time Dilution of Precision
    :return: NMEA2000 message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.GNSSDOPData
    msg.priority = 6
    msg.add_byte_uint(sid)
    msg.add_byte_uint((desired_mode & 0x07) << 5 | ((actual_mode & 0x07) << 2))
    msg.add_2_byte_double(hdop, 0.01)
    msg.add_2_byte_double(vdop, 0.01)
    msg.add_2_byte_double(tdop, 0.01)
    return msg


class GNSSDOPData(NamedTuple):
    sid: int
    desired_mode: N2kGNSSDOPmode
    actual_mode: N2kGNSSDOPmode
    hdop: float
    vdop: float
    tdop: float


def parse_n2k_gnss_dop(msg: Message) -> GNSSDOPData:
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    vb = msg.get_byte_uint(index)

    return GNSSDOPData(
        sid=sid,
        desired_mode=N2kGNSSDOPmode((vb >> 5) & 0x07),
        actual_mode=N2kGNSSDOPmode((vb >> 2) & 0x07),
        hdop=msg.get_2_byte_double(0.01, index),
        vdop=msg.get_2_byte_double(0.01, index),
        tdop=msg.get_2_byte_double(0.01, index),
    )


MAX_SATELLITE_INFO_COUNT = 18  # Maximum amount of satellites that fit into fast packet. TODO: extend using tp message


class SatelliteInfo(NamedTuple):
    # TODO: figure out a way to type NamedTuples properly.
    prn: int
    elevation: float
    azimuth: float
    snr: float
    range_residuals: float
    usage_status: N2kPRNUsageStatus


# GNSS Satellites in View (PGN 129540)
def set_n2k_gnss_satellites_in_view(sid: int, mode: N2kRangeResidualMode, satellites: List[SatelliteInfo]) -> Message:
    """
    GNSS Satellites in View (PGN 129540)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        different messages to indicate that they are measured at same time
    :param mode: Range residual mode
    :param satellites: List of the info of the satellites used
    :return: NMEA2000 Message, ready to be sent
    """
    msg = Message()
    msg.pgn = PGN.GNSSSatellitesInView
    msg.priority = 6
    msg.add_byte_uint(sid)
    msg.add_byte_uint(mode | 0xfc)  # 2 bit mode, 6 bit reserved

    if len(satellites) > MAX_SATELLITE_INFO_COUNT:
        # TODO: Log warning
        satellites = satellites[:MAX_SATELLITE_INFO_COUNT]
    msg.add_byte_uint(len(satellites))

    for satellite in satellites:
        msg.add_byte_uint(satellite.prn)
        msg.add_2_byte_double(satellite.elevation, 1e-4)
        msg.add_2_byte_udouble(satellite.azimuth, 1e-4)
        msg.add_2_byte_double(satellite.snr, 1e-2)
        msg.add_4_byte_double(satellite.range_residuals, 1e-4)
        msg.add_byte_uint(satellite.usage_status | 0xf0)

    return msg


class GNSSSatellitesInView(NamedTuple):
    sid: int
    mode: N2kRangeResidualMode
    satellites: List[SatelliteInfo]


def parse_n2k_gnss_satellites_in_view(msg: Message) -> GNSSSatellitesInView:
    index = IntRef(0)

    sid = msg.get_byte_uint(index)
    mode = N2kRangeResidualMode(msg.get_byte_uint(index) & 0x03)
    number_of_satellites = msg.get_byte_uint(index)
    satellites = []

    if number_of_satellites > MAX_SATELLITE_INFO_COUNT:
        # TODO: Log warning
        pass
    else:
        for i in range(number_of_satellites):
            satellites.append(SatelliteInfo(
                prn=msg.get_byte_uint(index),
                elevation=msg.get_2_byte_double(1e-4, index),
                azimuth=msg.get_2_byte_udouble(1e-4, index),
                snr=msg.get_2_byte_double(1e-2, index),
                range_residuals=msg.get_4_byte_double(1e-5, index),
                usage_status=N2kPRNUsageStatus(msg.get_byte_uint(index) & 0x0f),
            ))

    return GNSSSatellitesInView(
        sid=sid,
        mode=mode,
        satellites=satellites,
    )


# AIS static data class A (PGN 129794)
# TODO


# AIS static data class B part A (PGN 129809)
# TODO


# AIS static data class B part B (PGN 129810)
# TODO


# Waypoint list (PGN 130074)
# TODO


# Wind Speed (PGN 130306)
def set_n2k_wind_speed(sid: int, wind_speed: float, wind_angle: float, wind_reference: N2kWindReference) -> Message:
    """
    Wind Speed (PGN 130306)

    :param sid: Sequence ID. If your device provides e.g. boat speed and heading at same time, you can set the same SID
        for different messages to indicate that they are measured at same time.
    :param wind_speed: Wind Speed in meters per second
    :param wind_angle: Wind Angle in radians
    :param wind_reference: Can be e.g. Theoretical Wind using True North or Magnetic North,
        Apparent Wind as measured, ...\n
        See :py:class:`n2k.types.N2kWindReference`
    :return: NMEA2000 message ready to be sent.
    """
    msg = Message()
    msg.pgn = PGN.WindSpeed
    msg.priority = 2
    msg.add_byte_uint(sid)
    msg.add_2_byte_udouble(wind_speed, 0.01)
    msg.add_2_byte_udouble(wind_angle, 0.0001)
    msg.add_byte_uint(wind_reference)
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    return msg


class WindSpeed(NamedTuple):
    sid: int
    wind_speed: float
    wind_angle: float
    wind_reference: N2kWindReference


def parse_n2k_wind_speed(msg: Message) -> WindSpeed:
    """
    Parse heading information from a PGN 127250 message

    :param msg: NMEA2000 Message with PGN 127250
    :return: Dictionary containing the parsed information
    """
    index = IntRef(0)
    return WindSpeed(
        sid=msg.get_byte_uint(index),
        wind_speed=msg.get_2_byte_udouble(0.01, index),
        wind_angle=msg.get_2_byte_udouble(0.0001, index),
        wind_reference=N2kWindReference(msg.get_byte_uint(index) & 0x07)
    )


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
    msg.pgn = PGN.IsoAcknowledgement
    msg.priority = 6
    msg.add_byte_uint(control)
    msg.add_byte_uint(group_function)
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_byte_uint(0xff)  # Reserved
    msg.add_3_byte_int(pgn)


# ISO Address Claim (PGN 60928)
def set_n2k_iso_address_claim(msg: Message, unique_number: int, manufacturer_code: int, device_function: int,
                              device_class: int, device_instance: int = 0, system_instance: int = 0,
                              industry_group: int = 4) -> None:
    device_information = DeviceInformation()
    device_information.unique_number = unique_number
    device_information.manufacturer_code = manufacturer_code
    device_information.device_function = device_function
    device_information.device_class = device_class
    device_information.device_instance = device_instance
    device_information.system_instance = system_instance
    device_information.industry_group = industry_group

    set_n2k_iso_address_claim_by_name(msg, device_information.name)


def set_n2k_iso_address_claim_by_name(msg: Message, name: int) -> None:
    msg.pgn = PGN.IsoAddressClaim
    msg.priority = 6
    msg.add_uint_64(name)


# Product Information (PGN 126996)
def set_n2k_product_information(msg: Message, n2k_version: int, product_code: int, model_id: str, sw_code: str,
                                model_version: str, model_serial_code: str, certification_level: int = 1,
                                load_equivalency: int = 1) -> None:
    msg.pgn = PGN.ProductInformation
    msg.priority = 6
    msg.add_2_byte_uint(n2k_version)
    msg.add_2_byte_uint(product_code)
    msg.add_str(model_id, MAX_N2K_MODEL_ID_LEN)
    msg.add_str(sw_code, MAX_N2K_SW_CODE_LEN)
    msg.add_str(model_version, MAX_N2K_MODEL_VERSION_LEN)
    msg.add_str(model_serial_code, MAX_N2K_MODEL_SERIAL_CODE_LEN)
    msg.add_byte_uint(certification_level)
    msg.add_byte_uint(load_equivalency)


# TODO: parser
def parse_n2k_pgn_product_information(msg: Message) -> ProductInformation:
    assert msg.pgn == PGN.ProductInformation

    index = IntRef(0)
    return ProductInformation(
        n2k_version=msg.get_2_byte_uint(index),
        product_code=msg.get_2_byte_uint(index),
        n2k_model_id=msg.get_str(MAX_N2K_MODEL_ID_LEN, index),
        n2k_sw_code=msg.get_str(MAX_N2K_SW_CODE_LEN, index),
        n2k_model_version=msg.get_str(MAX_N2K_MODEL_VERSION_LEN, index),
        n2k_model_serial_code=msg.get_str(MAX_N2K_MODEL_SERIAL_CODE_LEN, index),
        certification_level=msg.get_byte_uint(index),
        load_equivalency=msg.get_byte_uint(index),
    )


# Configuration Information (PGN: 126998)
def set_n2k_configuration_information(msg: Message, manufacturer_information: str, installation_description1: str,
                                      installation_description2: str) -> None:
    total_len = 0
    max_len = msg.max_data_len - 6  # each field has 2 extra bytes
    man_info_len = min(len(manufacturer_information), Max_N2K_CONFIGURATION_INFO_FIELD_LEN)
    inst_desc1_len = min(len(installation_description1), Max_N2K_CONFIGURATION_INFO_FIELD_LEN)
    inst_desc2_len = min(len(installation_description2), Max_N2K_CONFIGURATION_INFO_FIELD_LEN)

    if total_len + man_info_len > max_len:
        man_info_len = max_len - total_len
    total_len += man_info_len
    if total_len + inst_desc1_len > max_len:
        inst_desc1_len = max_len - total_len
    total_len += inst_desc1_len
    if total_len + inst_desc2_len > max_len:
        inst_desc2_len = max_len - total_len
    total_len += inst_desc2_len

    msg.pgn = PGN.ConfigurationInformation
    msg.priority = 6

    # Installation Description 1
    msg.add_byte_uint(inst_desc1_len + 2)
    msg.add_byte_uint(0x01)
    msg.add_str(installation_description1, inst_desc1_len)

    # Installation Description 2
    msg.add_byte_uint(inst_desc2_len + 2)
    msg.add_byte_uint(0x01)
    msg.add_str(installation_description2, inst_desc1_len)

    # Manufacturer Information
    msg.add_byte_uint(man_info_len + 2)
    msg.add_byte_uint(0x01)
    msg.add_str(manufacturer_information, man_info_len)


# TODO: parser
def parse_n2k_pgn_configuration_information(msg: Message) -> ConfigurationInformation:
    assert msg.pgn == PGN.ConfigurationInformation
    index = IntRef(0)

    return ConfigurationInformation(
        installation_description1=msg.get_var_str(index) or "",
        installation_description2=msg.get_var_str(index) or "",
        manufacturer_information=msg.get_var_str(index) or "",
    )


# ISO Request (PGN 59904)
def set_n2k_pgn_iso_request(msg: Message, destination: int, requested_pgn: int) -> None:
    msg.pgn = PGN.IsoRequest
    msg.destination = destination
    msg.priority = 6
    msg.add_3_byte_int(requested_pgn)


def parse_n2k_pgn_iso_request(msg: Message) -> Optional[int]:
    if 3 <= msg.data_len <= 8:
        return msg.get_3_byte_uint(IntRef(0))
    return None

# enum tN2kPGNList {N2kpgnl_transmit=0, N2kpgnl_receive=1 };


# PGN List (Transmit and Receive)
def set_n2k_pgn_transmit_list(msg: Message, destination: int, pgns: List[int]):
    print("NotImplemented set_n2k_pgn_transmit_list")


# Heartbeat (PGN: 126993)
# time_interval_ms: between 10 and 655'320ms
def set_heartbeat(msg: Message, time_interval_ms: int, status_byte: int) -> None:
    print("NotImplemented set_heartbeat")
