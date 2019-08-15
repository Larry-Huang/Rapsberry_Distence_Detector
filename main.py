#! /usr/bin/env python3
# coding:utf-8
import tkinter as tk
import threading
import os   
import backend

class detectWindow():
    def detect_working(self):
        while True:
            wo_id =self.e2.get()
            ma_id = self.e1.get()
            lm_user = self.e3.get()
            op =  self.e4.get()
            count =self.e5.get()
            backend.detect_working(wo_id,ma_id,lm_user,op,count)
    def keyboard(self):
        os.system('florence')
    def add_command(self):
        self.list1.insert(tk.END,(self.e1.get()))
    def callKeyboard(self):
    #global lock
    #lock.acquire()
        added_thread = threading.Thread(target=self.keyboard)
        added_thread.start()
        #lock.release()
    def window_initial(self):
        window = tk.Tk()
        window.wm_title('my window')
        #window.geometry('2000x3000')
        l1=tk.Label(window,text="機台:",font=("Courier", 45))
        l1.grid(row=0,column=0)

        l2=tk.Label(window,text="工單:",font=("Courier", 45))
        l2.grid(row=0,column=2)

        l3=tk.Label(window,text="工號:",font=("Courier", 45))
        l3.grid(row=1,column=0)

        l4=tk.Label(window,text="製程:",font=("Courier", 45))
        l4.grid(row=1,column=2)

        l4=tk.Label(window,text="穴數:",font=("Courier", 45))
        l4.grid(row=2,column=0)
        
        machine_id=tk.StringVar()
        self.e1=tk.Entry(window,textvariable=machine_id,font=("Courier", 24))
        self.e1.grid(row=0,column=1)

        wo_id=tk.StringVar()
        self.e2=tk.Entry(window,textvariable=wo_id,font=("Courier", 24))
        self.e2.grid(row=0,column=3)

        wo_num=tk.StringVar()
        self.e3=tk.Entry(window,textvariable=wo_num,font=("Courier", 24))
        self.e3.grid(row=1,column=1)

        op=tk.StringVar()
        self.e4=tk.Entry(window,textvariable=op,font=("Courier", 24))
        self.e4.grid(row=1,column=3)
        
        count=tk.StringVar()
        self.e5=tk.Entry(window,textvariable=count,font=("Courier", 24))
        self.e5.grid(row=2,column=1)

        self.b1=tk.Button(window,text="開始", width=20,font=("Courier", 16),command=self.add_command)
        self.b1.grid(row=0,column=6)

        self.b2= tk.Button(window,text="結束", width=20,font=("Courier", 16),command=self.detect_working)
        self.b2.grid(row=1,column=6)

        self.list1 = tk.Listbox(window, height=20,width=60)
        self.list1.grid(row=3,column=0,rowspan=6,columnspan=2)
        self.sb1= tk.Scrollbar(window)
        self.sb1.grid(row=3,column=2,rowspan=10)

        self.list1.configure(yscrollcommand= self.sb1.set)
        self.sb1.configure(command= self.list1.yview)

        self.b3 = tk.Button(window,text="鍵盤",width=20,font=("Courier", 16),command=self.callKeyboard)
        self.b3.grid(column=6,row=3)
        window.mainloop()
        
    def __init__(self):
        print('tttt')

a= detectWindow()
a.window_initial()
