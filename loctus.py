import serial
from tkinter import *


class Loctus(Frame):
    
    arduino_serial = serial.Serial('/dev/ttyUSB0')
    arduino_serial.baudrate = 115200
    arduino_serial.timeout = 1

    def __init__(self, master):
        Frame.__init__(self, master)

        self.master = master

        self.init_window()

    def init_window(self):
        # set up the main frame

        self.master.title("Bluetooth")
        self.pack(fill=BOTH, expand=1)

        # ----------------- GUI stuff ---------------------


        menu = Menu(self.master)
        self.master.config(menu=menu)

        menu.add_command(label='Exit', command=self.client_exit)
        
        
    
    def client_exit(self):
        exit(1)
    
    
        

root = Tk()
root.geometry("400x300")

app = Loctus(root)

root.mainloop()