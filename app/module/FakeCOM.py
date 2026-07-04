# import time

from module import BaseCom
import logging

class FakeCom(BaseCom):
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        self.is_open = False
        self.port: ( str | None ) = None
        self.baudrate: int = 115200
        self.timeout: float = 1.0
        super().__init__(logger)
        self.logger.debug("antena sintetica criada")

    def send_command(self, command: bytes):
        return super().send_command(command)
    
    def read_response(self):
        # return super().read_response()
        if self.is_open:
            # return "NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n"
            return "TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi"
        else:
            self.logger.error("conexão serial fechada")
            return None

    def check_connected(self):
        return self.is_open

    def open(self):
        self.is_open = True
        return None

    def close(self):
        self.is_open = False
        return None

    def get_port_options(self):
        return [ "fake-1", "fake-2", "fake-3" ]
        # return super().get_port_options()

    def get_baudrate_options(self) -> list:
        return super().get_baudrate_options()

    def get_timeout_options(self) -> list:
        return super().get_timeout_options()

    def get_port(self) -> (str | None):
        return self.port
        # return super().get_port()

    def get_baudrate(self) -> int:
        return self.baudrate
        # return super().get_baudrate()

    def get_timeout(self) -> (float | None):
        return self.timeout
        # return super().get_timeout()

    def set_port(self, port) -> None:
        self.logger.info(f"definindo porta como {port}")
        self.port = port
        self.logger.info(f"porta definida como {port}")
        return None

    def set_baudrate(self, baudrate) -> None:
        self.logger.info(f"definindo baudrate como {baudrate}")
        self.baudrate = baudrate
        self.logger.info(f"baudrate definido como {baudrate}")
        return None

    def set_timeout(self, timeout) -> None:
        self.logger.info(f"definindo timeout como {timeout}")
        self.timeout = timeout
        self.logger.info(f"timeout definido como {timeout}")
        return None

    # TODO: adapt every method under this comment...
    def list_ports(self) -> list:
        return super().list_ports()
