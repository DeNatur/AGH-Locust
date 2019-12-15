import serial
import threading
import serial.tools.list_ports
import cv2
import imutils
import time
import math

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# implement the default mpl key bindings
from matplotlib.figure import Figure
from pandas import DataFrame

from PIL import Image
from PIL import ImageTk
from generate_results import GenerateFinalDetections
from tkinter import Tk, Label, Menu, Listbox, Frame, BOTH, SINGLE, N, W, E, Entry
from simple_pid import PID



class Loctus(Frame):
    ports = []
    arduino_serial = serial.Serial()
    k1 = 0.5
    k2 = 0.8
    k3 = 0.3
    
    Pr = 5
    Ir = 0
    Dr = 0
    
    Py = 5
    Iy = 0
    Dy = 0
    
    control = 975
    roll_trim = 0
    pitch_trim = 0

    def __init__(self, master):
        Frame.__init__(self, master)

        self.finalDetector = GenerateFinalDetections()
        self.canvas = None
        self.master = master
        self.frame = None
        self.thread = None
        self.stopEvent = None
        self.panel = None
        self.dir_txt = None
        self.init_window()
        self.throttle = 990
        self.input2 = 1000
        self.roll =1500
        self.pid = PID(self.k1, self.k2, self.k3, setpoint=-5, sample_time=0.03)
        self.pid.output_limits = (1500, 2000)
        self.time_now = time.time()
        self.stop = True
        
        self.pidRoll = PID(self.Pr, self.Ir, self.Dr, setpoint=0, sample_time=0.03)
        self.pidRoll.output_limits = (1000, 2000)
        self.pidRoll.set_auto_mode(True,1500)
        self.pidYaw = PID(self.Py, self.Iy, self.Dy, setpoint=0, sample_time=0.03)
        self.pidYaw.output_limits = (1000, 2000)

    def init_window(self):
        # set up the main frame

        self.master.title("AI Racer")

        self.pack(fill=BOTH, expand=1)


        # ----------------- GUI stuff ---------------------

        list_of_ports = Listbox(self, selectmode=SINGLE)
        list_of_ports.grid(row=3, column=0, sticky=N)
        Label(self, text="Port: ").grid(row=2, column=0, sticky=W)
        self.serial_ports(list_of_ports)
        Label(self,text="Baudrate:").grid(row=0,column=0,sticky=W)
        Label(self,text="Direction:").grid(row=0,column=1,sticky=W, padx=10)
        self.dir_txt = Label(self,text="None")
        self.roll_trim_txt = Label(self, text=str(self.roll_trim))
        self.roll_trim_txt.grid(row=2, column=1, sticky=W, padx=10)
        self.dir_txt.grid(row=1,column=1,sticky=W, padx=10)
        self.k1_edit = Entry(self)
        self.k1_edit.insert(0, str(self.k1))
        self.k1_edit.grid(row=1, column=2, sticky=W, padx=10)
        
        self.k2_edit = Entry(self)
        self.k2_edit.insert(0, str(self.k2))
        self.k2_edit.grid(row=1, column=3, sticky=W, padx=10)
        
        self.k3_edit = Entry(self)
        self.k3_edit.insert(0, str(self.k3))
        self.k3_edit.grid(row=1, column=4, sticky=W, padx=10)
        
        self.Data1 = {'Channels':['1','2','3','4'],
                 'Values': [1500,1500,1500,1500]}
        self.df1 = DataFrame(self.Data1, columns= ['Channels', 'Values'])
        self.df1 = self.df1[['Channels', 'Values']].groupby('Channels').sum()
        
        self.f = Figure(figsize=(5,4), dpi=100)
        #self.ax1 = self.f.add_subplot(111)
        #self.canvas = FigureCanvasTkAgg(self.f, master=self.master)
        #self.canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
        #self.df1.plot(kind='bar', legend=True, ax=self.ax1)
        #self.ax1.set_title('Value')
        
        
        
        self.frame = cv2.imread("test.jpg")
        self.frame = imutils.resize(self.frame, width=700)
        image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        self.panel = Label(image=image)
        self.panel.image = image
        self.panel.pack(side="left", padx=10, pady=10)
        baudrate_entry = Entry(self)
        baudrate_entry.grid(row=1, column=0, sticky=E)
        baudrate_entry.insert(0,"115200")

        menu = Menu(self.master)
        self.master.config(menu=menu)

        menu.add_command(label='Exit', command=self.client_exit)
        menu.add_command(label='Refresh', command=lambda: self.serial_ports(list_of_ports))
        menu.add_command(label='Connect', command=lambda: self.connect(list_of_ports, baudrate_entry))
        menu.add_command(label='Disconnect', command=self.disconnect)
        menu.add_command(label='STOP/START', command=self.drone_stop)
        menu.add_command(label='Set PID', command=self.set_pid)
        menu.add_command(label='Set CONTROL', command=self.set_control)
        menu.add_command(label='+ roll', command=lambda: self.trim_roll(True))
        menu.add_command(label='- roll', command=lambda: self.trim_roll(False))
        menu.add_command(label='pitch', command=self.trim_pitch)
        #menu.add_command(label='LOL', command=self.drone_start)
        #menu.add_command(label='LOL2', command=self.drone2)
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

    def client_exit(self):
        exit(1)
    def trim_roll(self, x):
        if x:
            self.roll_trim = self.roll_trim + 10
        else:
            self.roll_trim = self.roll_trim - 10
        self.roll_trim_txt.configure(text=str(self.roll_trim))
    
    def trim_pitch(self):
        if self.pitch_trim == 100:
            self.pitch_trim = 0
        else:
            self.pitch_trim = 100
    def set_control(self):
        self.throttle = 975
        self.roll = 1500
    
    def set_pid(self):
        self.k1 = float(self.k1_edit.get())
        self.k2 = float(self.k2_edit.get())
        self.k3 = float(self.k3_edit.get())
        self.pid.tunings = (self.k1, self.k2, self.k3)
    def drone_stop(self):
        self.throttle = 975
        self.roll =1500
        if self.stop:
            self.stop = False
        else:
            self.stop = True
    def drone_start(self):
        self.input2 = 1800
        self.input1 = 1800
    def drone2(self):
        self.input2 = 1100
        self.input1 = 1100
    def serial_ports(self, list_of_ports):
        list_of_ports.delete(0, 'end')
        port_number = 1
        self.ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(self.ports):
            list_of_ports.insert(port_number, port)

    def connect(self, list_of_ports, baudrate_entry):
        self.arduino_serial.baudrate = int(baudrate_entry.get())
        self.arduino_serial.port = list_of_ports.get(list_of_ports.curselection())
        self.arduino_serial.open()
        print("Connecting to: %s" % self.arduino_serial.port)
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def disconnect(self):
        self.arduino_serial.close()
    def onClose(self):
        print("closing...")
        self.stopEvent.set()
        self.master.quit()
    def receive(self):
        while(True):
            temp = self.arduino_serial.readline()
            print("Received: " + temp)
    def sendToArduino(self, throttle, pitch, roll, yaw, input1, input2):
        command = "@" + str(throttle) + "#" + str(pitch) + "$" + str(roll) + "%" + str(yaw) + "^" + str(input1) + "&" + str(input2) + "e";    
        b = bytearray()
        b.extend(map(ord, command))
        if self.arduino_serial.is_open:
            self.arduino_serial.write(b)
    def videoLoop(self):
        par = 0.2
        cap = cv2.VideoCapture(1)
        pitch = 1500
        self.roll = 1500
        self.throttle = 990
        yaw = 1500
        input1 = 1500
        first = True
        try:
            while not self.stopEvent.is_set():
                #self.frame = cv2.imread("test.jpg")
                ret, self.frame = cap.read()

                if ret == True:
                    cv2.imwrite('data/test.jpg', self.frame)
                    self.frame, txt, txt2, odl_y, odl_x, width_up, width_down, height_left, height_right = self.finalDetector.predict(self.frame)
                    self.frame = imutils.resize(self.frame, width=400)
                    l = 0
                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)
                    self.dir_txt.configure(text=txt)
                    angle_radians = 0
                    try:
                        b = ((height_left + height_right)/2)
                        a = 0.24
                        angle_radians = math.acos(width_up/((height_left + height_right)/2))
                        if height_left < height_right:
                            angle_radians = angle_radians * -1
                        angle_radians = angle_radians * 150
                        angle_radians = int(angle_radians)
                        l = a/b
                        l = l*100000
                        l = l/3
                        odl_y = odl_y-((l - 40)*2)
                    except:
                        pass
                    if self.panel is None:
                        self.panel.image = image
                    else:
                        self.panel.configure(image=image)
                        self.panel.image = image
                    
                    #print("ODL Y: {} CONTROL: {} {} {} {} PIDROLL {}  {}".format(odl_y, self.throttle, self.k1, self.k2, self.k3,odl_x,self.roll))
                    #print("ODL Y {} DIS {}".format(odl_y, int(l)))
                    #print("ANGLE {} DIS {}".format(angle_radians, int(l)/3))
                    self.time_now = time.time()
                    #print(self.throttle)
                    if self.stop:
                        self.throttle = self.pid(odl_y)
                        pitch = self.pidRoll(odl_x)
                       # pitch = self.pidYaw(angle_radians)
                    if txt2 == "LEFT":
                        yaw = 1500 + odl_x * 1.5    
                    elif txt2 == "RIGHT": 
                        yaw = 1500 + odl_x * 1.5
                    else:
                        yaw = 1500
                        #if txt == 'UP' and first:
                         #   first = False
                          #  self.throttle = 1500
                   # pitch = 1500 + angle_radians
                    print("THROTTLE: {} ROLL: {} ANGLE {} PITCH {}".format(self.throttle, pitch, angle_radians, self.pitch_trim))
                    self.sendToArduino(pitch , self.roll - self.pitch_trim, self.throttle, yaw, input1, self.input2)
                            
            cap.release()
        except RuntimeError:
            print("[INFO] caught a RuntimeError")
root = Tk()
root.geometry("640x640")
app = Loctus(root)
#root.protocol("WM_DELETE_WINDOW", app.onClose)
root.mainloop()