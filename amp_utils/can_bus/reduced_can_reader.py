import struct
import logging
import cantools
import can
import cantools.database
import numpy as np

from can_proxy import CanBusCommunicator

class StateCanReader():
    def __init__(self) -> None:
        DBC_FILE = "/home/ampera/ws/src/amp_utils/amp_utils/config/amp266-testeECU.dbc"
        BUSTYPE = "socketcan"
        CHANNEL = "can0"
        self.db = cantools.database.load_file(DBC_FILE)

        filters = [
            #painel
            {"can_id": 321, "can_mask": 0x7FF, "extended": False},
            {"can_id": 839, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1355, "can_mask": 0x7FF, "extended": False},

            #RES
            {"can_id": 393, "can_mask": 0x7FF, "extended": False},
            {"can_id": 137, "can_mask": 0x7FF, "extended": False},

            #DataLogger
            {"can_id": 1186, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1187, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1188, "can_mask": 0x7FF, "extended": False},

            #ECU
            {"can_id": 288, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1056, "can_mask": 0x7FF, "extended": False},
            {"can_id": 544, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1057, "can_mask": 0x7FF, "extended": False},
            {"can_id": 289, "can_mask": 0x7FF, "extended": False},
        ]

        self.logger = logging.getLogger('CAN_Reader')
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.can_listener = CanBusCommunicator(CHANNEL, BUSTYPE, filters)

        self.logger.info("CAN Reader inicializado")
        
    def can_reader(self, message):
        try:
            can_message = self.db.decode_message(message.arbitration_id, message.data)
            self.logger.debug(f"ID {message.arbitration_id}: {can_message}")
        except Exception as e:
            self.logger.error(f"Erro ao decodificar ID {message.arbitration_id} (Dados: {message.data.hex()}): {str(e)}")
            return
        
        return can_message

    def send_message(self, id, signals, extended=False):
        try:
            data = self.db.encode_message(id, signals)
            self.can_listener.bus.send(
                can.Message(arbitration_id=id, data=data, is_extended_id=extended)
            )
        except Exception as e:
            self.logger.error(f"Erro ao enviar: {e}")

    def receive_message(self):
        try:
            return self.can_listener.read_message()
        except Exception as e:
            self.logger.error(f"Erro ao ler mensagem CAN: {str(e)}")
            return None