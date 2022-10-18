import can
import time
import n2k

bus = can.Bus('can0', interface='socketcan')
notifier = can.Notifier(bus, [])
n2k_node = n2k.Node(bus)
notifier.add_listener(n2k_node)

while True:
    time.sleep(0.5)
