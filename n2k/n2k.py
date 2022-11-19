# static functions and helpers probably?
from enum import IntEnum


def is_broadcast(source: int) -> bool:
    return source == 0xff


def is_fast_packet_first_frame(byte: int):
    return byte & 0x1f == 0


class PGN(IntEnum):
    IsoAcknowledgement = 59392  # prio: 6, period: NA
    IsoRequest = 59904  # prio: 6, period: NA
    TransportProtocolDataTransfer = 60160  # prio: 6, period: NA
    TransportProtocolConnectionManagement = 60416  # prio: 6, period: NA
    IsoAddressClaim = 60928  # prio: 6, period: NA
    CommandedAddress = 65240  # prio: 6, period: NA
    RequestGroupFunction = 126208  # prio: 3, period: NA
    CommandGroupFunction = 126208  # prio: 3, period: NA
    AcknowledgeGroupFunction = 126208  # prio: 3, period: NA
    SupportedPGNList = 126464  # prio: 6, period: NA
    SystemDateTime = 126992  # prio: 3, period: 1000
    Heartbeat = 126993  # prio: 7, period: 60000
    ProductInformation = 126996  # prio: 6, period: NA
    ConfigurationInformation = 126998  # prio: 6, period: NA
    Rudder = 127245  # prio: 2, period: 100
    VesselHeading = 127250  # prio: 2, period: 100
    RateOfTurn = 127251  # prio: 2, period: 100
    Attitude = 127257  # prio: 3, period: 1000
    EngineParametersRapid = 127488  # prio: 2, period: 100, rapid update
    TransmissionParameters = 127493  # prio: 2, period: 100, dynamic
    BinaryStatusReport = 127501  # prio: 3, period: NA
    FluidLevel = 127505  # prio: 6, period: 2500
    BatteryStatus = 127508  # prio: 6, period: 1500
    MagneticVariation = 127258  # prio: 6, period: NA
    BoatSpeed = 128259  # prio: 2, period: 1000
    WaterDepth = 128267  # prio: 3, period: 1000
    LatLonRapid = 129025  # prio: 2, period: 100
    CogSogRapid = 129026  # prio: 2, period: 250
    CrossTrackError = 129283  # prio: 3, period: 1000
    WindSpeed = 130306  # prio: 2, period: 100
    OutsideEnvironmentalParameters = 130310  # prio: 5, period: 500
    Temperature = 130312  # prio: 5, period: 2000
    Humidity = 130313  # prio: 5, period: 2000
    Pressure = 130314  # prio: 5, period: 2000
    TemperatureExtendedRange = 130316  # prio: 5, period: NA
    SmallCraftStatusTrimTabPosition = 130576  # prio: 2, period: 200
    
    # Default Messages
    Alert = 126983  # prio: 2, period: 1000
    AlertResponse = 126984  # prio: 2, period: NA
    AlertText = 126985  # prio: 2, period: 10000
    AlertConfiguration = 126986  # prio: 2, period: NA
    AlertThreshold = 126987  # prio: 2, period: NA
    AlertValue = 126988  # prio: 2, period: 10000
    ManOverBoard = 127233  # prio: 3, period: NA
    HeadingTrackControl = 127237  # prio: 2, period: 250
    EngineParametersDynamic = 127489  # prio: 2, period: 500
    TripFuelConsumptionVessel = 127496  # prio: 5, period: 1000
    TripFuelConsumptionEngine = 127497  # prio: 5, period: 1000
    EngineParametersStatic = 127498  # prio: 5, period: NA
    ACInputStatus = 127503  # prio: 6, period: 1500
    ACOutputStatus = 127504  # prio: 6, period: 1500
    DCDetailedstatus = 127506  # prio: 6, period: 1500
    ChargerStatus = 127507  # prio: 6, period: 1500
    InverterStatus = 127509  # prio: 6, period: 1500
    ChargerConfigurationStatus = 127510  # prio: 6, period: NA
    InverterConfigurationStatus = 127511  # prio: 6, period: NA
    AGSConfigurationstatus = 127512  # prio: 6, period: NA
    BatteryConfigurationStatus = 127513  # prio: 6, period: NA
    AGSStatus = 127514  # prio: 6, period: 1500
    DistanceLog = 128275  # prio: 6, period: 1000
    TrackedTargetData = 128520  # prio: 2, period: 1000
    GNSSPositionData = 129029  # prio: 3, period: 1000
    AISClassAPositionReport = 129038  # prio: 4, period: NA
    AISClassBPositionReport = 129039  # prio: 4, period: NA
    AISClassBExtendedPositionReport = 129040  # prio: 4, period: NA
    AISAidstoNavigationReport = 129041  # prio: 4, period: NA (AtoN)
    Datum = 129044  # prio: 6, period: 10000
    UserDatumSettings = 129045  # prio: 6, period: NA
    NavigationInfo = 129284  # prio: 3, period: 1000
    WaypointList = 129285  # prio: 3, period: NA
    TimeToMark = 129301  # prio: 3, period: 1000
    BearingAndDistanceBetweenTwoMarks = 129302  # prio: 6, period: NA
    GNSSControlStatus = 129538  # prio: 6, period: NA
    GNSSSatellitesInView = 129540  # prio: 6, period: 1000
    GPSAlmanacData = 129541  # prio: 6, period: NA
    GNSSPseudorangeNoiseStatistics = 129542  # prio: 6, period: 1000
    GNSS_RAIM_Output = 129545  # prio: 6, period: NA
    GNSSPseudorangeErrorStatistics = 129547  # prio: 6, period: NA
    DGNSSCorrections = 129549  # prio: 6, period: NA
    GNSSDifferentialCorrectionReceiverSignal = 129551  # prio: 6, period: NA
    GLONASSAlmanacData = 129556  # prio: 6, period: NA
    AIS_DGNSS_Broadcast_Binary_Message = 129792  # prio: 6, period: NA
    AIS_UTC_And_Date_Report = 129793  # prio: 7, period: NA
    AISClassAStaticData = 129794  # prio: 6, period: NA
    AISAddressedBinaryMessage = 129795  # prio: 5, period: NA
    AISAcknowledge = 129796  # prio: 7, period: NA
    AISBinaryBroadcastMessage = 129797  # prio: 5, period: NA
    AIS_SAR_Aircraft_Position_Report = 129798  # prio: 4, period: NA
    RadioFrequencyModePower = 129799  # prio: 3, period: NA
    AIS_UTC_Date_Inquiry = 129800  # prio: 7, period: NA
    AISAddressedSafetyRelatedMessage = 129801  # prio: 5, period: NA
    AISSafetyRelatedBroadcastMessage = 129802  # prio: 5, period: NA
    AISInterrogationPGN = 129803  # prio: 7, period: NA
    AISAssignmentModeCommand = 129804  # prio: 7, period: NA
    AISDataLinkManagementMessage = 129805  # prio: 7, period: NA
    AISChannelManagement = 129806  # prio: 7, period: NA
    AISGroupAssignment = 129807  # prio: 7, period: NA
    DSCCallInformation = 129808  # prio: 8, period: NA
    AISClassBStaticDataPartA = 129809  # prio: 6, period: NA
    AISClassBStaticDataPartB = 129810  # prio: 6, period: NA
    AISSingleSlotBinaryMessage = 129811  # prio: 5, period: NA
    AISMultiSlotBinaryMessage = 129812  # prio: 5, period: NA
    AISLongRangeBroadcastMessage = 129813  # prio: 5, period: NA
    LoranCTDData = 130052  # prio: 3, period: 1000
    LoranCRangeData = 130053  # prio: 3, period: 1000
    LoranCSignalData = 130054  # prio: 3, period: 1000
    Label = 130060  # prio: 7, period: NA
    ChannelSourceConfiguration = 130061  # prio: 7, period: NA
    RouteAndWaypointServiceDatabaseList = 130064  # prio: 7, period: NA
    RouteAndWaypointServiceRouteList = 130065  # prio: 7, period: NA
    RouteAndWaypointServiceRouteWPListAttributes = 130066  # prio: 7, period: NA
    RouteAndWaypointServiceRouteWPNameAndPosition = 130067  # prio: 7, period: NA
    RouteAndWaypointServiceRouteWPName = 130068  # prio: 7, period: NA
    RouteAndWaypointServiceXTELimitAndNavigationMethod = 130069  # prio: 7, period: NA
    RouteAndWaypointServiceWPComment = 130070  # prio: 7, period: NA
    RouteAndWaypointServiceRouteComment = 130071  # prio: 7, period: NA
    RouteAndWaypointServiceDatabaseComment = 130072  # prio: 7, period: NA
    RouteAndWaypointServiceRadiusOfTurn = 130073  # prio: 7, period: NA
    RouteAndWaypointServiceWPListWPNameAndPosition = 130074  # prio: 7, period: NA
    TideStationData = 130320  # prio: 6, period: 1000
    SalinityStationData = 130321  # prio: 6, period: 1000
    CurrentStationData = 130322  # prio: 6, period: 1000
    MeteorologicalStationData = 130323  # prio: 6, period: 1000
    MooredBuoyStationData = 130324  # prio: 6, period: 1000
    WatermakerInputSettingAndStatus = 130567  # prio: 6, period: 2500
    DirectionDataPGN = 130577  # prio: 3, period: 1000
    VesselSpeedComponents = 130578  # prio: 2, period: 250


DefaultTransmitMessages = [
    PGN.IsoAcknowledgement,
    PGN.IsoRequest,
    PGN.TransportProtocolDataTransfer,
    PGN.TransportProtocolConnectionManagement,
    PGN.IsoAddressClaim,
    PGN.RequestGroupFunction,  # same number as command and acknowledge versions
    PGN.SupportedPGNList,
    PGN.Heartbeat,
    PGN.ProductInformation,
    PGN.ConfigurationInformation,
]

DefaultReceiveMessages = [
    PGN.IsoAcknowledgement,
    PGN.IsoRequest,
    PGN.TransportProtocolDataTransfer,
    PGN.TransportProtocolConnectionManagement,
    PGN.IsoAddressClaim,
    PGN.CommandedAddress,
    PGN.RequestGroupFunction,  # same number as command and acknowledge versions
]


def is_single_frame_system_message(pgn: int) -> bool:
    return pgn in [PGN.IsoAcknowledgement, PGN.TransportProtocolDataTransfer,
                   PGN.TransportProtocolConnectionManagement, PGN.IsoRequest, PGN.IsoAddressClaim]
        

def is_fast_packet_system_message(pgn: int) -> bool:
    return pgn == PGN.CommandedAddress or pgn == PGN.RequestGroupFunction


def is_default_single_frame_message(pgn: int) -> bool:
    return pgn in [PGN.SystemDateTime, PGN.Heartbeat, PGN.Rudder, PGN.VesselHeading, PGN.RateOfTurn, PGN.Attitude,
                   PGN.EngineParametersRapid, PGN.TransmissionParameters, PGN.BinaryStatusReport, PGN.FluidLevel,
                   PGN.BatteryStatus, PGN.BoatSpeed, PGN.WaterDepth, PGN.LatLonRapid, PGN.CogSogRapid,
                   PGN.CrossTrackError, PGN.WindSpeed, PGN.OutsideEnvironmentalParameters, PGN.Temperature,
                   PGN.Humidity, PGN.Pressure, PGN.TemperatureExtendedRange, PGN.SmallCraftStatusTrimTabPosition]


def is_mandatory_fast_packet_message(pgn: int) -> bool:
    return pgn in [PGN.SupportedPGNList, PGN.ProductInformation, PGN.ConfigurationInformation]


def is_default_fast_packet_message(pgn: int) -> bool:
    return pgn in [PGN.Alert, PGN.AlertResponse, PGN.AlertText, PGN.AlertConfiguration, PGN.AlertThreshold,
                   PGN.AlertValue, PGN.ManOverBoard, PGN.HeadingTrackControl, PGN.EngineParametersDynamic,
                   PGN.TripFuelConsumptionVessel, PGN.TripFuelConsumptionEngine, PGN.EngineParametersStatic,
                   PGN.ACInputStatus, PGN.ACOutputStatus, PGN.DCDetailedstatus, PGN.ChargerStatus, PGN.InverterStatus,
                   PGN.ChargerConfigurationStatus, PGN.InverterConfigurationStatus, PGN.AGSConfigurationstatus,
                   PGN.BatteryConfigurationStatus, PGN.AGSStatus, PGN.DistanceLog, PGN.TrackedTargetData,
                   PGN.GNSSPositionData, PGN.AISClassAPositionReport, PGN.AISClassBPositionReport,
                   PGN.AISClassBExtendedPositionReport, PGN.AISAidstoNavigationReport, PGN.Datum, PGN.UserDatumSettings,
                   PGN.NavigationInfo, PGN.WaypointList, PGN.TimeToMark, PGN.BearingAndDistanceBetweenTwoMarks,
                   PGN.GNSSControlStatus, PGN.GNSSSatellitesInView, PGN.GPSAlmanacData,
                   PGN.GNSSPseudorangeNoiseStatistics, PGN.GNSS_RAIM_Output, PGN.GNSSPseudorangeErrorStatistics,
                   PGN.DGNSSCorrections, PGN.GNSSDifferentialCorrectionReceiverSignal, PGN.GLONASSAlmanacData,
                   PGN.AIS_DGNSS_Broadcast_Binary_Message, PGN.AIS_UTC_And_Date_Report, PGN.AISClassAStaticData,
                   PGN.AISAddressedBinaryMessage, PGN.AISAcknowledge, PGN.AISBinaryBroadcastMessage,
                   PGN.AIS_SAR_Aircraft_Position_Report, PGN.RadioFrequencyModePower, PGN.AIS_UTC_Date_Inquiry,
                   PGN.AISAddressedSafetyRelatedMessage, PGN.AISSafetyRelatedBroadcastMessage, PGN.AISInterrogationPGN,
                   PGN.AISAssignmentModeCommand, PGN.AISDataLinkManagementMessage, PGN.AISChannelManagement,
                   PGN.AISGroupAssignment, PGN.DSCCallInformation, PGN.AISClassBStaticDataPartA,
                   PGN.AISClassBStaticDataPartB, PGN.AISSingleSlotBinaryMessage, PGN.AISMultiSlotBinaryMessage,
                   PGN.AISLongRangeBroadcastMessage, PGN.LoranCTDData, PGN.LoranCRangeData, PGN.LoranCSignalData,
                   PGN.Label, PGN.ChannelSourceConfiguration, PGN.RouteAndWaypointServiceDatabaseList,
                   PGN.RouteAndWaypointServiceRouteList, PGN.RouteAndWaypointServiceRouteWPListAttributes,
                   PGN.RouteAndWaypointServiceRouteWPNameAndPosition, PGN.RouteAndWaypointServiceRouteWPName,
                   PGN.RouteAndWaypointServiceXTELimitAndNavigationMethod, PGN.RouteAndWaypointServiceWPComment,
                   PGN.RouteAndWaypointServiceRouteComment, PGN.RouteAndWaypointServiceDatabaseComment,
                   PGN.RouteAndWaypointServiceRadiusOfTurn, PGN.RouteAndWaypointServiceWPListWPNameAndPosition,
                   PGN.TideStationData, PGN.SalinityStationData, PGN.CurrentStationData, PGN.MeteorologicalStationData,
                   PGN.MooredBuoyStationData, PGN.WatermakerInputSettingAndStatus, PGN.DirectionDataPGN,
                   PGN.VesselSpeedComponents]


def is_proprietary_fast_packet_message(pgn: int) -> bool:
    return pgn == 126720 or 130816 <= pgn <= 131071


def is_proprietary_message(pgn: int) -> bool:
    """
    Test if a message is part of the NMEA2000 specifications or proprietary
    
    :param pgn: PGN to be tested
    :return: Whether the message is part of the NMEA2000 spec
    """
    return is_proprietary_fast_packet_message(pgn) or pgn == 61184 or 65280 <= pgn <= 65535


