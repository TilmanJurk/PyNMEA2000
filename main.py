from math import radians

import can
import time
import n2k
import logging

bus = can.Bus('can0', interface='socketcan')
notifier = can.Notifier(bus, [])
device_information = n2k.DeviceInformation()
device_information.unique_number = 1
device_information.device_function = 130
device_information.device_class = 25
device_information.manufacturer_code = 2046
device_information.industry_group = 4
n2k_node = n2k.Node(bus, device_information)
n2k_node.set_product_information("Test", "0.0.1", "Dev", "00000000001", 2)
n2k_node.set_configuration_information()

# n2k.set_log_level(logging.DEBUG)

# notifier.add_listener(print)
notifier.add_listener(n2k_node)

while True:
    time.sleep(0.2)
    msg = n2k.messages.set_n2k_wind_speed(0, 10, radians(340), n2k.types.N2kWindReference.TrueNorth)
    n2k_node.send_msg(msg)
