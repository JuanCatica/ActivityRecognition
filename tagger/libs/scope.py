class Scope:
    def __init__(self, Canvas, DevicesManagger, buff_size = 700): 
        self.canvas = Canvas
        self.buff_size = buff_size
        self.deviceManagger = DevicesManagger
        self.width = int(Canvas['width'])
        self.height = int(Canvas['height'])
        self.colors = [
            "gray",
            "gold",
            "blue",
            "red",
            "green",
            "salmon",
            "purple",
            "cyan",
            "DarkOrange1",
            "VioletRed1"
        ]
        # Hardcoded
        self.DEVICE_LIST = [0,0,0,1,1,1]
        self.SENSOR_LIST = [0,1,2,0,1,2]

    @DeprecationWarning
    def set_devices_sensors(self, DEVICE_LIST, SENSOR_LIST = None):  ## Maximo 6 canales
        self.DEVICE_LIST = DEVICE_LIST[:6]
        self.SENSOR_LIST = SENSOR_LIST[:6]
        if self.SENSOR_LIST == None:
            self.SENSOR_LIST = [0]*len(self.DEVICE_LIST)

    def _plot_series(self, X, Y, Z , canal, name):
        canal += 1
        _x = _y = _z = 0
        i = 0
        self.canvas.create_text(self.buff_size+50,(80*(canal)),fill="red",font="Arial",text="{}".format(name))
        self.canvas.create_line(1, (80*canal), self.buff_size-2, (80*canal),fill="black")
        for x,y,z in zip(X, Y, Z):
            if x != None and _x != None:
                self.canvas.create_line(i, (80*canal) - _x, i+1, (80*canal) - x,fill="blue")
                self.canvas.create_line(i, (80*canal) - _y, i+1, (80*canal) - y,fill="red")
                self.canvas.create_line(i, (80*canal) - _z, i+1, (80*canal) - z,fill="green")
            _x = x
            _y = y
            _z = z
            i += 1

    def plot_sensors(self):
        self.canvas.delete("all")
        self.canvas.create_text(10,10,fill="blue",font="Arial",text="-X")
        self.canvas.create_text(30,10,fill="red",font="Arial",text="-Y")
        self.canvas.create_text(50,10,fill="green",font="Arial",text="-Z")
        for i,(devId,senId) in enumerate(zip(self.DEVICE_LIST, self.SENSOR_LIST)):
            sensor_queues = self.deviceManagger.get_device_sensor_series(devId,senId)
            self._plot_series(sensor_queues[0],sensor_queues[1],sensor_queues[2],i,self.deviceManagger.get_name(devId,senId))

        for i,(label,is_writting) in enumerate(zip(self.deviceManagger.get_label_serie(),self.deviceManagger.get_writting_serie())):
            color = "green" if is_writting else "black"
            self.canvas.create_line(i, self.height-26, i, self.height-32,fill=color)
            if is_writting:
                self.canvas.create_line(i, self.height, i, self.height-25,fill=self.colors[label]) 
        self.canvas.create_text(self.buff_size+50,self.height-30,fill="darkblue",font="Arial",text=f"{self.deviceManagger.lines}")
        self.canvas.create_text(self.buff_size+50,self.height-15,fill="darkblue",font="Arial",text="Labels")
        self.canvas.create_line(self.buff_size - 300,10,self.buff_size - 300,self.height-35,fill="black") ####### 6s : 300 pixeles
        self.canvas.after(50, self.plot_sensors)