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
            #painel
            {"can_id": 321, "can_mask": 0x7FF, "extended": False},
            {"can_id": 839, "can_mask": 0x7FF, "extended": False},
            {"can_id": 1355, "can_mask": 0x7FF, "extended": False},

            #RES
            {"can_id": 393, "can_mask": 0x7FF, "extended": False},
            {"can_id": 137, "can_mask": 0x7FF, "extended": False},

            #DataLogger
            {"can_id": 1185, "can_mask": 0x7FF, "extended": False},
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
            raise RuntimeError(e) from e

        values = {
            #ECU
            'ControlWord': None,
            'InverterStatus': None,
            'TMSErrorCode': None,
            'CurrentState': None,
            'ECUErrorCode': None,
            'InverterErrorCode': None,

            'MaxTemperature': None,
            'BrakeSwitch': None,
            'BrakePedal': None,
            'AcceleratorPedal': None,
            'StateOfCharge': None,
            'MaxCellVoltage': None,
            'AvgCellVoltage': None,
            'MinCellVoltage': None,

            'InverterCurrent': None,
            'BatteryCurrent': None,

            'InverterVoltage': None,
            'BatteryVoltage': None,

            'MotorRPM': None,
            'MotorTemperature': None,
            'MotorTorque': None,
            'InverterTemperature': None,

            #RES
            'ASStatus': None,
            'GOSignal': None,

            'ASEmergency': None,

            #DataLogger
            'SteeringAngle': None,
            'LimitSwitchLeft': None,
            'LimitSwitchRight': None,

            'EncoderFrontRight': None,
            'EncoderFrontLeft': None,

            'EncoderRearLeft': None,
            'EncoderRearRight': None,

            'AccelX': None,
            'AccelY': None,
            'AccelZ': None,

            #Painel
            'ReadyToDrive': None,
            'AutonomousMode': None,
            'PageID' : None,
        }

        try:
            match message.arbitration_id:
                #Painel
                case 321:
                    for key in ['ReadyToDrive']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 839:
                    for key in ['AutonomousMode']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1355:
                    for key in ['PageID']:
                        if key in can_message:
                            values[key] = can_message[key]
                #RES
                case 393:
                    for key in ['GOSignal', 'ASStatus']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 137:
                    for key in ['ASEmergency']:
                        if key in can_message:
                            values[key] = can_message[key]
                #DataLogger
                case 1185:
                    for key in ['SteeringAngle', 'LimitSwitchLeft', 'LimitSwitchRight']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1186:
                    for key in ['AccelX', 'AccelY', 'AccelZ']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1187:
                    for key in ['EncoderRearLeft', 'EncoderRearRight']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1188:
                    for key in ['EncoderFrontLeft', 'EncoderFrontRight']:
                        if key in can_message:
                            values[key] = can_message[key]
                #ECU
                case 288:
                    for key in ['ControlWord', 'InverterStatus', 'TMSErrorCode', 'CurrentState', 'ECUErrorCode', 'InverterErrorCode']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 544:
                    for key in ['InverterCurrent', 'BatteryCurrent']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1056:
                    for key in ['MotorRPM', 'MotorTemperature', 'MotorTorque', 'InverterTemperature']:
                        if key in can_message:
                            values[key] = can_message[key]

                case 1057:
                    for key in ['InverterVoltage', 'BatteryVoltage']:
                        if key in can_message:
                            values[key] = can_message[key]
                case 289:
                    for key in ['MaxTemperature', 'BrakeSwitch', 'BrakePedal', 'AcceleratorPedal', 'StateOfCharge', 'MaxCellVoltage', 'AvgCellVoltage', 'MinCellVoltage']:
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