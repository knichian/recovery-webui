from module import BaseCom
import logging

class FakeCom(BaseCom):
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        super().__init__(logger)

    def read_response(self):
        # return super().read_response()
        return "NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n"

