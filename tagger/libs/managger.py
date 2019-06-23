from libs.device import Device
import os
import time
from collections import deque

class DevicesManagger():
    def __init__(self, buff_size = 700, D0 = True, D1 = True, D2 = False, D3 = False):
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
        self.writting_lists = deque()
        self.label_cursor = 0
        self.lines = 0
        self._file = None

        # HardCode
        self.device_list_name = ["0-R1","1-R2","2-L1","3-L2"]
        self.sensor_list_name = ["Acc","Gyr","Mag"]
    
    def get_name(self,devId,senId):
        return "{}-{}".format(self.device_list_name[devId],self.sensor_list_name[senId])

    def set_path(self,path):
        self.path = path
        self._file = open(path,"w")
        line = "timestamp,delta"
        for i in self._DEVICE_LIST:
            if i:
                line += ",{}-x,{}-y,{}-z,{}-x,{}-y,{}-z,{}-x,{}-y,{}-z".format(
                    self.get_name(i.ID,0),self.get_name(i.ID,0),self.get_name(i.ID,0),
                    self.get_name(i.ID,1),self.get_name(i.ID,1),self.get_name(i.ID,1),
                    self.get_name(i.ID,2),self.get_name(i.ID,2),self.get_name(i.ID,2)
                    )
        line+= ",label"
        self._file.write(line + "\r\n")
        self._file.flush()
        self.is_writting = False
        self.lines = 0

    def set_label_cursor(self, l_cursor):
        label = 0
        if not self.is_writting:
            return
        try:
            label = int(l_cursor)
            if label < 0 or label > 9:
                label = 0
        except:
            pass
        self.label_cursor = label

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

    def get_writting_serie(self):
        return list(self.writting_lists)

    def start_writing(self):
        self.is_writting = True
        self.start_time = time.time()
        self.last = self.start_time

    def stop_writing(self):
        self.label_cursor = 0
        self.is_writting = False

    def _write_line(self):
        if self.is_writting:
            actual = time.time()
            line = "{},{}".format(actual - self.start_time, actual- self.last)
            self.last = actual
            for is_active, dev in zip(self._ACTIVE_LIST,self._DEVICE_LIST):
                if is_active:
                    line += dev.get_line()
            line += ",{}".format(self.label_cursor)
            self._file.write(line + "\r\n")
            self._file.flush()
            self.lines += 1
            self.labels.append(self.label_cursor)
            self.writting_lists.append(True)
        else:
            self.labels.append(0)
            self.writting_lists.append(False)
        if len(self.labels) >= self.buff_size:
                self.labels.popleft()
                self.writting_lists.popleft()

    def close(self):
        self.is_writting = False
        self.lines = 0
        if self._file:
            self._file.close()