from tkinter import *
from random import randint
import socket
import numpy as np
from threading import Thread
from collections import deque
import os
import time
import pyqrcode     # pip install PyQRCode
import png          # pip install pypng

class Device:
    def __init__(self, ID, buff_size):
        self.ID = ID
        self.buff_size = buff_size
        self.AX = deque()
        self.AY = deque()
        self.AZ = deque()
        self.GX = deque()
        self.GY = deque()
        self.GZ = deque()
        self.MX = deque()
        self.MY = deque()
        self.MZ = deque()

    def add_values(self, ax, ay, az, gx, gy, gz, mx, my, mz):
        self.AX.append(ax)
        self.AY.append(ay)
        self.AZ.append(az)
        self.GX.append(gx)
        self.GY.append(gy)
        self.GZ.append(gz)
        self.MX.append(mx)
        self.MY.append(my)
        self.MZ.append(mz)
        
        if len(self.AX) >= self.buff_size:
            self.AX.popleft()
            self.AY.popleft()
            self.AZ.popleft()
            self.GX.popleft()
            self.GY.popleft()
            self.GZ.popleft()
            self.MX.popleft()
            self.MY.popleft()
            self.MZ.popleft()
        
    def getSensor(self, sensorID):
        if sensorID == 0:
            return list(self.AX),list(self.AY),list(self.AZ)
        if sensorID == 1:
            return list(self.GX),list(self.GY),list(self.GZ)
        if sensorID == 2:
            return list(self.MX),list(self.MY),list(self.MZ)

    def get_line(self):
        line = ",{},{},{},{},{},{},{},{},{}".format(
            self.AX[-1],self.AY[-1],self.AY[-1],
            self.GX[-1],self.GY[-1],self.GY[-1],
            self.MX[-1],self.MY[-1],self.MY[-1]
        )
        return line

class DevicesManagger():
    def __init__(self, path, buff_size = 600, D0 = True, D1 = True, D2 = True, D3 = True):
        # Devices an chanels
        self._DEVICE_LIST = []
        self._DEVICE_LIST.append(Device(0,buff_size)) if D0 else self._DEVICE_LIST.append(None)
        self._DEVICE_LIST.append(Device(1,buff_size)) if D1 else self._DEVICE_LIST.append(None)
        self._DEVICE_LIST.append(Device(2,buff_size)) if D2 else self._DEVICE_LIST.append(None)
        self._DEVICE_LIST.append(Device(3,buff_size)) if D3 else self._DEVICE_LIST.append(None)
        
        self._ACTIVE_LIST = [D0, D1, D2, D3]
        self._received_list = list(map(lambda x: not x, self._ACTIVE_LIST))

        self.path = path
        if os.path.isfile(path):
            print("El archivo ya existe, creando nuevo ......")

        self._file = open(path,"w")
        self.start_time = -1
        self.is_writting = False

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
            raise Exception('El dispositivo {} ni se encuentra diponible'.format(n_device))

    def start_writing(self):
        self.is_writting = True
        self.start_time = time.time()

    def stop_writing(self):
        self.is_writting = False

    def _write_line(self):
        if self.is_writting:
            line = "{}".format(time.time()- self.start_time)
            for is_active, dev in zip(self._ACTIVE_LIST,self._DEVICE_LIST):
                if is_active:
                    line += dev.get_line()
            self._file.write(line + "\r\n")
            self._file.flush()
    def close(self):
        self.is_writting = False
        self._file.close()

class Scope:
    def __init__(self, Canvas, DevicesManagger, buff_size = 600): 
        self.canvas = Canvas
        self.buff_size = buff_size
        self.deviceManagger = DevicesManagger

    def set_devices_sensors(self, DEVICE_LIST, SENSOR_LIST = None):  ## Maximo 4 lineas 
        self.DEVICE_LIST = DEVICE_LIST
        self.SENSOR_LIST = SENSOR_LIST
        if self.SENSOR_LIST == None:
            self.SENSOR_LIST = [0]*len(self.DEVICE_LIST)

    def _plot_series(self, X, Y, Z , canal):
        canal += 1
        _x = _y = _z = 0
        i = 0
        for x,y,z in zip(X, Y, Z):
            if x != None and _x != None:
                self.canvas.create_line(i, _x + (80*canal), i+1, x + (80*canal),fill="blue")
                self.canvas.create_line(i, _y + (80*canal), i+1, y + (80*canal),fill="red")
                self.canvas.create_line(i, _z + (80*canal), i+1, z + (80*canal),fill="green")
            _x = x
            _y = y
            _z = z
            i += 1

    def plot_sensors(self):
        self.canvas.delete("all")
        for i,(dev,sen) in enumerate(zip(self.DEVICE_LIST, self.SENSOR_LIST)):
            sensor_queues = self.deviceManagger.get_device_sensor_series(dev,sen)
            self._plot_series(sensor_queues[0],sensor_queues[1],sensor_queues[2],i)
        self.canvas.after(50, self.plot_sensors)


# initialize root Window and canvas
root = Tk()
root.resizable(False,False)
canvas = Canvas(root, width = 1000, height = 600)
canvas.pack(side=LEFT)

# UDP Conection
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Internet, UDP
sock.connect(("8.8.8.8", 80))
UDP_IP = sock.getsockname()[0]
UDP_PORT = 6565
sock.close()
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
root.title(f"Tagger - Crane Proyect\t{UDP_IP} : {UDP_PORT}")

# QR Image
img_path = os.path.dirname(os.path.realpath(__file__)) + "/images/ulr.png"
print(img_path)
url = pyqrcode.create(f'{UDP_IP}:{UDP_PORT}')
url.png(img_path, scale=5)
canvas2 = Canvas(root, width = 300, height = 300)
img = PhotoImage(file=img_path) 
canvas2.create_image(20,20, anchor=NW, image=img)  
canvas2.pack(side=LEFT)

# DevicesManagger
path = "/Users/juancamilo/Desktop/file.csv"
managger = DevicesManagger(path)

# Scope
scope_ploter = Scope(canvas, managger)
scope_ploter.set_devices_sensors([0,0,1,1],[0,1,0,1])
managger.start_writing()

def UDP_collector():  
    try:
        while True:     
            data, _ = sock.recvfrom(1024)
            data = data.decode("utf-8")
            managger.update(data)    
    except:
        print("Finalizacion del hilo")
scope_ploter.plot_sensors()


thread_UDP = Thread(target=UDP_collector)
thread_UDP.start()
root.mainloop()
sock.close()
thread_UDP.join()
managger.close()