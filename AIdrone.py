import serial
import threading
import sys
import glob
import serial.tools.list_ports
import cv2
import imutils
import numpy as np
from PIL import Image
from PIL import ImageTk
from generate_results import GenerateFinalDetections
from tkinter import Tk, Label, Menu, Listbox, Frame, BOTH, SINGLE, N, W, E, Entry



class Loctus(Frame):
    ports = []
    arduino_serial = serial.Serial()

    def __init__(self, master):
        Frame.__init__(self, master)

        self.finalDetector = GenerateFinalDetections()
        self.master = master
        self.frame = None
        self.thread = None
        self.stopEvent = None
        self.panel = None
        self.init_window()
        

    def init_window(self):
        # set up the main frame

        self.master.title("Bluetooth")

        self.pack(fill=BOTH, expand=1)


        # ----------------- GUI stuff ---------------------

        list_of_ports = Listbox(self, selectmode=SINGLE)
        list_of_ports.grid(row=3, column=0, sticky=N)
        Label(self, text="Port: ").grid(row=2, column=0, sticky=W)
        self.serial_ports(list_of_ports)
        Label(self,text="Baudrate:").grid(row=0,column=0,sticky=W)
        Label(self,text="Direction:").grid(row=0,column=1,sticky=W, padx=10)
        self.dir_txt = Label(self,text="None").grid(row=1,column=1,sticky=W, padx=10)
        
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
        
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

    def client_exit(self):
        exit(1)

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

    def receive(self):
        while(True):
            temp = self.arduino_serial.readline()
            print(temp)
    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():
                self.frame = cv2.imread("test.jpg")
                self.frame, dir_txt = self.finalDetector.predict(self.frame)
                self.frame = imutils.resize(self.frame, width=700)
                
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                self.dir_txt.configure(text=dir_txt)
                
                if self.panel is None:
                    self.panel.image = image
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
        except RuntimeError:
            print("[INFO] caught a RuntimeError")
root = Tk()
root.geometry("1280x720")
app = Loctus(root)

root.mainloop()