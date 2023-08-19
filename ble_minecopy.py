import bluetooth
from ble_advertising import advertising_payload
import _thread
import math
from time import sleep

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)


class BLEUART:
    def __init__(self, ble, name="Akilli_Saksi", rxbuf=100):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        # Increase the size of the rx buffer and enable append mode.
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._connections = set()
        self._rx_buffer = bytearray()
        self._handler = None
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self._payload = advertising_payload(name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()

    def irq(self, handler):
        self._handler = handler

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(self._rx_handle)
                if self._handler:
                    self._handler()

    def any(self):
        return len(self._rx_buffer)

    def read(self, sz=None):
        if not sz:
            sz = len(self._rx_buffer)
        result = self._rx_buffer[0:sz]
        self._rx_buffer = self._rx_buffer[sz:]
        return result

    def write(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)
            
    def write_chunked(self, data): #---------------------
        for conn_handle in self._connections:
            for i in range(math.ceil(len(data)/20)):
                self._ble.gatts_notify(conn_handle, self._tx_handle, data[20 * i:20 * (i+1)])
                sleep(0.1)

    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


last_command = ""
command_sent = True

ble = bluetooth.BLE()
uart = BLEUART(ble)
def on_rx():
    global last_command
    global command_sent
    command_sent = False
    last_command = uart.read().decode().strip()
    #print("rx: ", last_command) # Print incoming messages.

uart.irq(handler = on_rx)
def send_command(command_to_send):
    print("Yeah command is out : {}".format(command_to_send))
    uart.write_chunked("{}\n".format(command_to_send)) #--------------

def get_command():
    global command_sent
    if (command_sent == False):
        command_sent = True
        return last_command
    else:
        return False
    
# def send_command():
#     ble = bluetooth.BLE()
#     uart = BLEUART(ble)
# 
#     def on_rx():
#         print("rx: ", uart.read().decode().strip()) # Print incoming messages.
# 
#     uart.irq(handler=on_rx) # Join on_rx func on incoming messages.
#     
#     from time import sleep
#     try:
#         while True:
#             with open("currentvalues.txt", "r") as f:
#                 f.seek(0, 0)
#                 line = f.read()
#                 print("It worked. Output : {}".format(line))
#                 sleep(2)
            
#        from time import sleep
#        while True:
#            uart.write("{} TaVars\n".format(i))
#            i = i + 1
#            sleep(2)
#     except KeyboardInterrupt:
#         pass
    #uart.close()
    
if __name__ == "__main__":
    send_command()