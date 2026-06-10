from module import BaseCom
import logging

class FakeCom(BaseCom):
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        super().__init__(logger)
