import serial
import serial.tools.list_ports
import sys

class base_com():
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                xonxoff=False,
                rtscts=False,
                write_timeout=timeout,
                dsrdtr=False,
                inter_byte_timeout=None
            )
        except serial.SerialException as e:
            self.serial = None
            raise

    # Envia um comando serial
    def send_command(self, command: bytes):
        self.serial.write(command)

    # Recebe uma string serial
    def read_response(self):
        return self.serial.readline().decode('utf-8').strip()
    
    # Confere a conexão serial
    def check_connection(self):
        return self.serial.is_open
    
    # Encerra a conexão serial
    def close(self):
        self.serial.close()

# Lista as portas seriais disponíveis
def list_ports():
    if sys.platform.startswith('win'):  # For Windows
        return [port.device for port in serial.tools.list_ports.comports()]
    elif sys.platform.startswith(('linux', 'cygwin')): # For Linux and Cygwin
        return [port.device for port in serial.tools.list_ports.comports() if '/dev/ttyACM' in port.device]
    return []

if __name__ == "__main__":
    ports = list_ports()
    
    print("Available COM ports:")
    for port in ports:
        print(port)
    
    # Example usage
    if ports:
        com = base_com('/dev/ttyACM0')
        n = 0
        while n<1000:
            # com.send_command(b'A')
            response = com.read_response()
            print(f"Response: {response}")
            n += 1
        com.close()