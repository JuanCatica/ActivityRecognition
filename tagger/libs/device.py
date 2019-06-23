from collections import deque

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
            self.AX[-1],self.AY[-1],self.AZ[-1],
            self.GX[-1],self.GY[-1],self.GZ[-1],
            self.MX[-1],self.MY[-1],self.MZ[-1]
        )
        return line