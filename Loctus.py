import serial
import threading
import sys
import glob
import serial.tools.list_ports
from tkinter import *



class Loctus(Frame):
    ports = []
    arduino_serial = serial.Serial()

    def __init__(self, master):
        Frame.__init__(self, master)



        self.master = master

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

        baudrate_entry = Entry(self)
        baudrate_entry.grid(row=1, column=0, sticky=E)
        baudrate_entry.insert(0,"115200")

        menu = Menu(self.master)
        self.master.config(menu=menu)

        menu.add_command(label='Exit', command=self.client_exit)
        menu.add_command(label='Refresh', command=lambda: self.serial_ports(list_of_ports))
        menu.add_command(label='Connect', command=lambda: self.connect(list_of_ports, baudrate_entry))
        menu.add_command(label='Disconnect', command=self.disconnect)

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


root = Tk()
root.geometry("400x300")
app = Loctus(root)

root.mainloop()