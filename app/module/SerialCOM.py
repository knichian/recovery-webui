import serial
import serial.tools.list_ports
from serial import Serial, SerialException
import sys
import logging

class BaseCom():
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        self.serial: Serial
        self.serial_configured: bool = False
        self.logger: logging.Logger = logger
        self.logger.info("interface serial criada")

    def configure_serial(self, port: str, baudrate: int = 115200, timeout: float = 0.5):
        try:
            self.serial: Serial = Serial(
                port = port,
                baudrate = baudrate,
                timeout = timeout,
                xonxoff = False,
                rtscts = False,
                write_timeout = timeout,
                dsrdtr = False,
                inter_byte_timeout = None
            )
            self.serial_configured = True
            self.logger.info("interface serial configurada")
        except SerialException as err:
            self.logger.error(f"erro ao configurar serial -> {err}")

    # TODO: create method to abstract the check if the serial is configured with a decorator

    # Envia um comando serial
    def send_command(self, command: bytes):
        if self.serial_configured:
            try:
                self.serial.write(command)
            except SerialException as err:
                self.logger.error(f"erro de comunicação serial -> {err}")
        else:
            self.logger.error("serial não configurada")

    # Recebe uma string serial
    def read_response(self):
        if self.serial_configured:
            try:
                return self.serial.readline().decode('utf-8').strip()
            except SerialException as err:
                self.logger.error(f"erro de comunicação serial -> {err}")
        else:
            self.logger.error("serial não configurada")
    
    # Confere a conexão serial
    def check_connection(self):
        if self.serial_configured:
            try:
                return self.serial.is_open
            except SerialException as err:
                self.logger.error(f"erro de comunicação serial -> {err}")
        else:
            self.logger.error("serial não configurada")
    
    # Encerra a conexão serial
    def close(self):
        if self.serial_configured:
            try:
                self.serial.close()

            except SerialException as err:
                self.logger.error(f"erro de comunicação serial -> {err}")
        else:
            self.logger.error("serial não configurada")

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
        antenna_serial.configure_serial("/dev/ttyACM")
        n = 0
        while n<1000:
            # com.send_command(b'A')
            response = antenna_serial.read_response()
            print(f"Response: {response}")
            n += 1
        antenna_serial.close()
