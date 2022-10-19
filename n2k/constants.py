# General (Node)
#: :obj:`int`
MAX_N2K_MODEL_ID_LEN: int = 32
#: :obj:`int`
MAX_N2K_SW_CODE_LEN: int = 32
#: :obj:`int`
MAX_N2K_MODEL_VERSION_LEN: int = 32
#: :obj:`int`
MAX_N2K_MODEL_SERIAL_CODE_LEN: int = 32
#: :obj:`int`
MAX_N2K_PRODUCT_INFO_STR_LEN: int = 32

#: :obj:`int`
Max_N2K_CONFIGURATION_INFO_FIELD_LEN: int = 70


N2K_MESSAGE_GROUPS: int = 2
N2K_MAX_CAN_BUS_ADDRESS: int = 251
N2K_NULL_CAN_BUS_ADDRESS: int = 254
N2K_BROADCAST_CAN_BUS_ADDRESS: int = 255

N2K_ADDRESS_CLAIM_TIMEOUT = 250
MAX_HEARTBEAT_INTERVAL = 655320

TP_MAX_FRAMES = 5  # Maximum amount of Frames that can be received at a single time # TODO: why?
TP_CM_BAM = 32
TP_CM_RTS = 16
TP_CM_CTS = 17
TP_CM_ACK = 19
TP_CM_Abort = 255

TP_CM_AbortBusy = 1
TP_CM_AbortNoResources = 2
TP_CM_AbortTimeout = 3


# Messages
N2K_DOUBLE_NAN = -1e9
N2K_FLOAT_NAN  = -1e9
N2K_UINT8_NA   = 0xff
N2K_INT8_NA    = 0x7f
N2K_UINT16_NA  = 0xffff
N2K_INT16_NA   = 0x7fff
N2K_UINT32_NA  = 0xffffffff
N2K_INT32_NA   = 0x7fffffff
N2K_UINT64_NA  = 0xffffffffffffffff
N2K_INT64_NA   = 0x7fffffffffffffff


# Device List

N2K_MAX_BUS_DEVICES = 254

N2K_DL_TIME_FOR_FIRST_REQUEST = 1000  # Time in ms for first request after device has been noticed on the bus
N2K_DL_TIME_BETWEEN_PI_REQUEST = 1000  # Time in ms between product information requests
N2K_DL_TIME_BETWEEN_CI_REQUEST = 1000  # Time in ms between configuration information requests


# Can Message Buffer

MAX_N2K_MSG_BUF_TIME: int = 100
