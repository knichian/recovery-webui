# import time

from module import BaseCom
import logging

class FakeCom(BaseCom):
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        self.is_open = False
        self.port: ( str | None ) = "fake-1"
        self.baudrate: int = 115200
        self.timeout: float = 1.0
        self.fake_lines: list[str] = [
                "#261,9339,0,-0.73,28.56,83.64,964.90,0.01,-0.03,0.01,0.34,-0.20,8.84,02:25:55,2025/11/05,440.30,-21.81603333,-49.23074617,7,nan,-49",
                "#261,11589,4,-0.88,28.62,83.57,964.92,0.01,-0.03,0.02,0.31,-0.22,8.79,02:25:58,2025/11/05,443.20,-21.81602000,-49.23074250,8,nan,-50",
                "#261,12098,5,-0.79,28.62,83.54,964.91,0.01,-0.03,0.01,0.37,-0.26,8.92,02:25:59,2025/11/05,443.20,-21.81602400,-49.23074100,8,nan,-49",
                "#261,12603,6,-0.68,28.62,83.58,964.89,0.01,-0.02,0.01,0.29,-0.25,8.81,02:25:59,2025/11/05,444.50,-21.81602400,-49.23074100,8,nan,-50",
                "#261,13114,7,-0.64,28.63,83.55,964.89,0.01,-0.02,0.01,0.37,-0.22,8.87,02:26:00,2025/11/05,444.50,-21.81603650,-49.23074317,8,nan,-49",
                "#261,13629,8,-0.95,28.64,83.60,964.92,0.01,-0.03,0.02,0.35,-0.26,8.87,02:26:00,2025/11/05,445.40,-21.81603650,-49.23074317,9,nan,-49",
                "#261,14143,9,-0.93,28.63,83.62,964.92,0.01,-0.02,0.02,0.36,-0.23,8.91,02:26:01,2025/11/05,445.40,-21.81604567,-49.23074850,9,nan,-49",
                "#261,15309,11,-0.79,28.64,83.66,964.91,0.01,-0.03,0.02,0.34,-0.24,8.83,02:26:02,2025/11/05,446.10,-21.81604517,-49.23074950,7,nan,-49",
                "#261,15824,12,-0.84,28.65,83.70,964.91,0.01,-0.03,0.01,0.28,-0.20,8.88,02:26:02,2025/11/05,446.10,-21.81604517,-49.23074950,7,nan,-49",
                "#261,17363,15,-0.69,28.66,83.67,964.90,0.01,-0.03,0.01,0.30,-0.23,8.87,02:26:04,2025/11/05,445.40,-21.81604500,-49.23074567,6,nan,-50"
                ]
        self.fake_lines_index = 0
        super().__init__(logger)
        self.logger.debug("antena sintetica criada")

    def send_command(self, command: bytes):
        return super().send_command(command)
    
    def read_response(self):
        # return super().read_response()
        if self.is_open:
            # return "NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n"
            # return "TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi"

            res: str = self.fake_lines[self.fake_lines_index]
            self.fake_lines_index+=1

            if self.fake_lines_index >= len(self.fake_lines): 
                self.fake_lines_index = 0

            return res

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
