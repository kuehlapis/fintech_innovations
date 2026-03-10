
import logging


logger = logging.getLogger(__name__)

class ClientDB:
    def __init__(self, db):
        self.db = db