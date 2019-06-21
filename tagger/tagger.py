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

# initialize root Window and canvas
root = Tk()
root.resizable(False,False)
canvas_scope = Canvas(root, width = 800, height = 600)
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

# Buttons
def start():
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"files")
        if file_name.get() != "":
                file_path = os.path.join(file_path,str(file_name.get()) +".csv")
                if os.path.isfile(file_path):
                        print("El archivo ya existe y no esta permitido sobrescribir")
                        return
                ed_file_name.config(state="disabled")
                start.config(state="disabled")
                pause.config(state="normal")
                resume.config(state="disabled")
                save.config(state="normal")
                
                managger.set_path(file_path)
                managger.start_writing()

def pause():
        managger.stop_writing()
        pause.config(state="disabled")
        start.config(state="disabled")
        resume.config(state="normal")
        save.config(state="normal")

def resume():
        managger.start_writing()
        resume.config(state="disabled")
        start.config(state="disabled")
        pause.config(state="normal")
        save.config(state="normal")

def save():
        file_name.set("")
        ed_file_name.config(state="normal")
        start.config(state="normal")
        pause.config(state="disabled")
        save.config(state="disabled")
        resume.config(state="disabled")
        managger.stop_writing()
        managger.close()

file_name = StringVar()
file_path = ""
tk.Label(frame, text="File Name, eg: user-trial").pack()
tk.Label(frame, text="*without .csv").pack()
ed_file_name = tk.Entry(frame, textvariable = file_name)
start = tk.Button(frame, text="START", command=start, width = 20)
pause = tk.Button(frame, text="PAUSE", command=pause, width = 20)
resume = tk.Button(frame, text="RESUME", command=resume, width = 20)
save = tk.Button(frame,  text="STOP & SAVE", command=save,  width = 20)
ed_file_name.pack()
tk.Label(frame, text="").pack()
tk.Label(frame, text="").pack()
start.pack()
pause.pack()
resume.pack()
save.pack()
pause.config(state="disabled")
save.config(state="disabled")
resume.config(state="disabled")
frame.pack()

# DevicesManagger
managger = DevicesManagger()

# Key Listener
def key(event):
    managger.set_label_cursor(event.char)
root.bind("<Key>", key)

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
managger.close()