import struct
import logging
import cantools
import can
import cantools.database
import numpy as np

from can_bus.can_proxy import CanBusCommunicator

class StateCanReader():
    def __init__(self) -> None:
        DBC_FILE = "src/amp_utils/config/can_AMP-226.dbc"
        BUSTYPE = "socketcan"
        CHANNEL = "can1"

        self.db = cantools.database.load_file(DBC_FILE)

        filters = [
            {"can_id": 321, "can_mask": 0x7FF, "extended": False},
            {"can_id": 839, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1355, "can_mask": 0x7FF, "extended": False},
            {"can_id": 393, "can_mask": 0x7FF, "extended": False},
            #{"can_id": 1185, "can_mask": 0x7FF, "extended": False},
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
            raise RuntimeError(e) from e

        values = {

            #RES
            'AS_status': None,
            'go_signal': None,

            #DataLogger
            'steering_angle': None,

            #Painel
            'ready_to_drive': None,
            'task_mode': None,
        }

        try:
            match message.arbitration_id:
                
                case 321:
                    for key in ['ready_to_drive']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 839:
                    for key in ['task_mode']:
                        if key in can_message:
                            values[key] = can_message[key]


                case 393:
                    for key in ['go_signal', 'AS_status']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1185:
                    for key in ['steering_angle']:
                        if key in can_message:
                            values[key] = can_message[key]

                case _:
                    self.logger.debug(f"ID {message.arbitration_id} não mapeado")
                    
        except Exception as e:
            self.logger.error(f"Erro ao mapear valores da mensagem CAN ID: {str(e)}")

        return values


    def send_references_steering(self, values):
        if 'Referencia' in values:
            try:
                ref_est_data = self.db.encode_message(528, {'Ref_Estercamento_Atuador': values['Referencia']})
                self.can_listener.bus.send(
                    can.Message(arbitration_id=528, data=ref_est_data, is_extended_id=False)
                )
            except Exception as e:
                self.logger.error(f"Erro ao enviar Ref_Estercamento_Atuador: {e}")


    def send_references_throttle(self, values):
         if 'Velocidade' in values:
            try:
                speed_ref_data = self.db.encode_message(274, {'Ref_Velocidade': values['Velocidade']})
                self.can_listener.bus.send(
                    can.Message(arbitration_id=274, data=speed_ref_data, is_extended_id=False)
                )
            except Exception as e:
                self.logger.error(f"Erro ao enviar Ref_Velocidade: {e}")

    def receive_message(self):
        try:
            return self.can_listener.read_message()
        except Exception as e:
            self.logger.error(f"Erro ao ler mensagem CAN: {str(e)}")
            return None