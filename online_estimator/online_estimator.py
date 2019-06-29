from tkinter import *
from tkinter import ttk
import tkinter as tk
from random import randint
import socket
import numpy as np
from threading import Thread
from collections import deque
import os
import time
import pyqrcode                             # pip install PyQRCode
import png                                  # pip install pypng
from libs.device import Device
from libs.managger import DevicesManagger
from libs.scope import Scope
from libs.estimator import online_estimator

import joblib
from sklearn.svm import SVC

# initialize root Window and canvas
root = Tk()
root.resizable(False,False)
canvas_scope = Canvas(root, width = 800, height = 400)
canvas_scope.pack(side=LEFT)

# UDP Conection
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Internet, UDP
sock.connect(("8.8.8.8", 80))
UDP_IP = sock.getsockname()[0]
UDP_PORT = 6565
sock.close()
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
root.title(f"Tagger - Crane Project\t{UDP_IP} : {UDP_PORT}")

# Contenedor
frame = Frame(root)

# QR Image
img_path =  os.path.join(os.path.dirname(os.path.realpath(__file__)),"images","ulr.png")  
url = pyqrcode.create(f'{UDP_IP}:{UDP_PORT}')
url.png(img_path, scale=5)
canvasQR = Canvas(frame, width = 200, height = 300)
img = PhotoImage(file=img_path) 
canvasQR.create_image(20,20, anchor=NW, image=img)  
canvasQR.pack()


frame.pack()

# DevicesManagger
managger = DevicesManagger()
estimator_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"bin","estimator.pkl")  
estimator = joblib.load(filename=estimator_path)
managger.set_online_estimator(estimator)
# Key Listener


# Scope
scope_ploter = Scope(canvas_scope, managger)
scope_ploter.plot_sensors()

def UDP_collector():  
    try:
        while True:     
            data, _ = sock.recvfrom(1024)
            data = data.decode("utf-8")
            managger.update(data)  
    except:
        print("Finalizacion del hilo UDP")

thread_UDP = Thread(target=UDP_collector)
thread_UDP.start()
root.mainloop()
sock.close()
thread_UDP.join()