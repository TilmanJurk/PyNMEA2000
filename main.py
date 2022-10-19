import can
import time
import n2k

bus = can.Bus('can0', interface='socketcan')
notifier = can.Notifier(bus, [])
n2k_node = n2k.Node(bus)
n2k_node.set_device_information(1)
n2k_node.set_product_information("Test", "0.0.1", "Dev", "00000000001", 2)
n2k_node.set_configuration_information()

notifier.add_listener(n2k_node)
notifier.add_listener(print)

while True:
    time.sleep(0.1)
