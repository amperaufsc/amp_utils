import struct
import logging
import cantools
import can
import cantools.database
import numpy as np

from can_proxy import CanBusCommunicator

class StateCanReader():
    def __init__(self) -> None:
        DBC_FILE = "src/as_amp/can_bus/config/AS_CAN.dbc"
        BUSTYPE = "socketcan"
        CHANNEL = "can0"

        self.db = cantools.database.load_file(DBC_FILE)

        filters = [
            {"can_id": 1104, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1105, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1106, "can_mask": 0x7FF, "extended": False},
            {"can_id": 865, "can_mask": 0x7FF, "extended": False},
            {"can_id": 881, "can_mask": 0x7FF, "extended": False},
            {"can_id": 882, "can_mask": 0x7FF, "extended": False},
            {"can_id": 883, "can_mask": 0x7FF, "extended": False},
            {"can_id": 884, "can_mask": 0x7FF, "extended": False},
            {"can_id": 885, "can_mask": 0x7FF, "extended": False},
            {"can_id": 886, "can_mask": 0x7FF, "extended": False},
            {"can_id": 887, "can_mask": 0x7FF, "extended": False},
            {"can_id": 888, "can_mask": 0x7FF, "extended": False},
            {"can_id": 288, "can_mask": 0x7FF, "extended": False},
            {"can_id": 273, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1088, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1089, "can_mask": 0x7FF, "extended": False},
            {"can_id": 560, "can_mask": 0x7FF, "extended": False},

        ]

        self.logger = logging.getLogger('CAN_Reader')
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info("CAN Reader inicializado")

        self.can_listener = CanBusCommunicator(CHANNEL, BUSTYPE, filters)

    def can_reader(self, message):
        try:
            can_message = self.db.decode_message(message.arbitration_id, message.data)
            self.logger.debug(f"ID {message.arbitration_id}: {can_message}")
        except Exception as e:
            self.logger.error(f"Erro ao decodificar ID {message.arbitration_id} (Dados: {message.data.hex()}): {str(e)}")
            raise RuntimeError(e) from e

        values = {

            # Suspension
            "Susp_TE": None,
            "Susp_FD": None, 
            "Susp_FE": None,
            "Susp_TD": None,

            # Pedal / Brakes
            "Cebolinha": None,
            "Brake_Pedal": None,
            "ACC_Pedal": None,
            "Pedal_angle": None, 
            "Steering_angle": None,
            "Pressure_T": None,
            "Pressure_F": None,

            # Modes
            "Task_Mode": None,
            "Torque_Mode": None,

            # Inverter
            "Inverter_Current": None,
            "Inverter_Temperature": None,
            "Inverter_Voltage": None,

            # Motor
            "Motor_Temperature": None,
            "Motor_RPM": None,
            "Motor_Input_Power": None,
            "Motor_Output_Power": None,
            "Motor_Torque": None,
            "Car_Speed": None,

            # ACC
            "BMS_Current": None,
            "Avarage_Temperature": None,
            "Max_Temperature": None,
            "HV_Voltage": None,
            "Protection_Flags": None,

            # AS
            "RES": None,
            "Estercamento_Atuador": None,
            "Go_State": None,

            # WSM
            "Encoder_Front_Left": None,
            "Encoder_Front_Right": None,
            "Encoder_Rear_Left": None,
            "Encoder_Rear_Right": None
        }

        try:
            match message.arbitration_id:
                
                case 1104:
                    for key in ['Susp_TE', 'Susp_FD', 'Susp_FE', 'Susp_TD']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1105:
                    for key in ['Pedal_angle', 'Steering_angle']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1106:
                    for key in ['Pressure_T', 'Pressure_F']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 865:
                    for key in ['Task_Mode']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 881:
                    for key in ['Motor_Temperature', 'Motor_RPM']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 882:
                    for key in ['Inverter_Current', 'BMS_Current']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 883:
                    for key in ['Inverter_Temperature', 'Inverter_Voltage']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 884:
                    for key in ['Motor_Torque', 'ACC_Pedal', 'Brake_Pedal', 'Cebolinha']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 885:
                    for key in ['Motor_Input_Power', 'Motor_Output_Power']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 886:
                    for key in ['Torque_Mod']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 887:
                    for key in ['HV_Voltage', 'Protection_Flags']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 888:
                    for key in ['Car_Speed', 'Avarage_Temperature', 'Max_Temperature']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 288:
                    for key in ['RES']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1088:
                    for key in ['Encoder_Front_Left', 'Encoder_Front_Right']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1089:
                    for key in ['Encoder_Rear_Left', 'Encoder_Rear_Right']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 560:
                    for key in ['Estercamento_Atuador']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 273:
                    for key in ['Go_State']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 528:
                    for key in ['Ref_Estercamento_Atuador']:
                       if key in can_message:
                           values[key] = can_message[key]

                case 274:
                    for key in ['Ref_Velocidade']:
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