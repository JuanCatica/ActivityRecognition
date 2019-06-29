from libs.device import Device
import os
import time
from collections import deque

class DevicesManagger():
    def __init__(self, buff_size = 700, D0 = True, D1 = False, D2 = False, D3 = False):
        # Devices an chanels
        self._DEVICE_LIST = []
        self._DEVICE_LIST.append(Device(0,buff_size)) if D0 else self._DEVICE_LIST.append(None)
        self._DEVICE_LIST.append(Device(1,buff_size)) if D1 else self._DEVICE_LIST.append(None)
        self._DEVICE_LIST.append(Device(2,buff_size)) if D2 else self._DEVICE_LIST.append(None)
        self._DEVICE_LIST.append(Device(3,buff_size)) if D3 else self._DEVICE_LIST.append(None)
        self._ACTIVE_LIST = [D0, D1, D2, D3]
        self._received_list = list(map(lambda x: not x, self._ACTIVE_LIST))
        
        self.buff_size = buff_size
        self.start_time = 0
        self.last=0
        self.time = 0
        self.is_writting = False

        self.labels = deque()
        self.label_cursor = 0
        self.lines = 0

        self.online_estimator = None
        # HardCode
        self.device_list_name = ["0-R1","1-R2","2-L1","3-L2"]
        self.sensor_list_name = ["Acc","Gyr","Mag"]

    def set_online_estimator(self, estimator):
        self.online_estimator = estimator

    def get_name(self,devId,senId):
        return "{}-{}".format(self.device_list_name[devId],self.sensor_list_name[senId])

    def get_active_list(self):
        return self._ACTIVE_LIST

    def update(self, data):
        v = data.split(",")
        try:
            n_device = int(v[0])
            AX, AY, AZ = float(v[1]),float(v[2]),float(v[3])
            GX, GY, GZ = float(v[4]),float(v[5]),float(v[6])
            MX, MY, MZ = float(v[7]),float(v[8]),float(v[9])

            if not self._ACTIVE_LIST[n_device]:
                print("Dispositivo no Registrado")
                return

            if self._received_list[n_device]:
                for i, (is_active, is_received) in enumerate(zip(self._ACTIVE_LIST, self._received_list)):
                    if is_active and not is_received:
                        self._DEVICE_LIST[i].add_values(None, None, None, None, None, None, None, None, None)
                self._write_line()
                self._received_list = list(map(lambda x: not x, self._ACTIVE_LIST))
                self._received_list[n_device] = True
                self._DEVICE_LIST[n_device].add_values(AX, AY, AZ, GX, GY, GZ, MX, MY, MZ)
            else:
                self._received_list[n_device] = True
                self._DEVICE_LIST[n_device].add_values(AX, AY, AZ, GX, GY, GZ, MX, MY, MZ)
                if sum(self._received_list) == len(self._received_list):
                    self._write_line()
                    self._received_list = list(map(lambda x: not x, self._ACTIVE_LIST))
        except:
            pass

    def get_device_sensor_series(self, n_device, sensorID):
        try:
            return self._DEVICE_LIST[n_device].getSensor(sensorID)
        except:
            raise Exception('El dispositivo {} no se encuentra diponible'.format(n_device))

    def get_label_serie(self):
        return list(self.labels)

    def _write_line(self):
        if self.online_estimator:
            line = []
            for is_active, dev in zip(self._ACTIVE_LIST,self._DEVICE_LIST):
                if is_active:
                    line += dev.get_last_values()
            
            self.online_estimator.add_register(line[:6])
            self.labels.append(self.online_estimator.get_label())
        else:
            self.labels.append(0)
        if len(self.labels) >= self.buff_size:
            self.labels.popleft()