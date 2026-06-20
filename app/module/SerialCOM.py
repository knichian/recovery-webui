# import serial
from datetime import time

import serial.tools.list_ports
from serial import Serial, SerialException
import sys
import logging

# TODO: create method to abstract the check if the serial is configured with a decorator
class BaseCom:
    
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        self.logger: logging.Logger = logger
        self.serial = Serial(
            port = None,
            baudrate = 115200,
            timeout = None,
            xonxoff = False,
            rtscts = False,
            write_timeout = None,
            dsrdtr = False,
            inter_byte_timeout = None
        )
        self.logger.info("interface de comunicação criada")


    # Envia um comando serial
    def send_command(self, command: bytes):
        try:
            self.serial.write(command)
        except SerialException as err:
            self.logger.error(f"erro de comunicação serial -> {err}")


    # Recebe uma string serial
    def read_response(self):
        try:
            return self.serial.readline().decode('utf-8').strip()
        except SerialException as err:
            self.logger.error(f"erro de comunicação serial -> {err}")
    
    # Confere a conexão serial esta ativa
    def check_connected(self):
        return self.serial.is_open

    # Ativa a conexão serial
    def open(self):
        self.serial.open()
        
    # Desativa a conexão serial
    def close(self):
        self.serial.close()

    def set_port(self, port) -> None:
        self.serial.port = port
        return None

    def set_baudrate(self, baudrate) -> None:
        self.serial.baudrate = baudrate
        return None

    def set_timeout(self, timeout) -> None:
        self.serial.timeout = timeout
        return None



    def list_ports(self):
        if sys.platform.startswith('win'):  # For Windows
            return [port.device for port in serial.tools.list_ports.comports()]
        elif sys.platform.startswith(('linux', 'cygwin')): # For Linux and Cygwin
            return [port.device for port in serial.tools.list_ports.comports() if '/dev/ttyACM' in port.device]
        else:
            return []



# Lista as portas seriais disponíveis
def list_ports():
    if sys.platform.startswith('win'):  # For Windows
        return [port.device for port in serial.tools.list_ports.comports()]
    elif sys.platform.startswith(('linux', 'cygwin')): # For Linux and Cygwin
        return [port.device for port in serial.tools.list_ports.comports() if '/dev/ttyACM' in port.device]
    else:
        return []

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ports = list_ports()
    
    logger.info("Available COM ports:")
    for port in ports:
        logger.info(port)
    
    # Example usage
    if ports:
        antenna_serial = BaseCom()
        # antenna_serial.configure_serial("/dev/ttyACM")
        # antenna_serial.configure_port("/dev/ttyACM")
        # antenna_serial.configure_baudrate()  # broken! need to find the default value for this
        # antenna_serial.configure_timeout() # broken! need to find the default value for this
        # antenna_serial.configure_serial()
        # TODO: fix this test part
        n = 0
        while n<1000:
            # com.send_command(b'A')
            response = antenna_serial.read_response()
            print(f"Response: {response}")
            n += 1
        antenna_serial.close()
