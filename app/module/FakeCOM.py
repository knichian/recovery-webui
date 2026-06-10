from module import BaseCom
import logging

class FakeCom(BaseCom):
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        super().__init__(logger)

    def read_response(self):
        return super().read_response()
        
        # fields = response.split(",")
        #
        # TEAM_ID = fields[1]
        # millis =  fields[2]
        # count =   fields[3]
        # altp =    fields[4]
        # temp =    fields[5]
        # umi =     fields[6]
        # p =       fields[7]
        # gp =      fields[8]
        # gr =      fields[9]
        # gy =      fields[10]
        # ap =      fields[11]
        # ar =      fields[12]
        # ay =      fields[13]
        # hora =    fields[14]
        # data =    fields[15]
        # alt =     fields[16]
        # lat =     fields[17]
        # lon =     fields[18]
        # sat =     fields[19]
        # pqd =     fields[20]
        # rssi =    fields[21]

        # TODO: finish this fake interface class for tests

        pass
