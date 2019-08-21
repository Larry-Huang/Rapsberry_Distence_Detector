#! /usr/bin/env python3
# coding:utf-8

from tkinter import *
import threading,os,time,queue
from backend import Distancer
from tkinter import messagebox

distancer = Distancer(moinitor_pin= 26,trigger_pin= 23,echo_pin= 24)
class detectWindow():
    def __init__(self,window):
        self.stop_report_flag = False
        self.que = queue.Queue(maxsize = 100)  
        self.window = window
        self.window.wm_title("Working Window")
        l1=Label(window,text="機台:",font=("Courier", 30))
        l1.grid(row=0,column=0)
        l2=Label(window,text="工單:",font=("Courier", 30))
        l2.grid(row=0,column=2)
        l3=Label(window,text="工號:",font=("Courier", 30))
        l3.grid(row=1,column=0)
        l4=Label(window,text="製程:",font=("Courier", 30))
        l4.grid(row=1,column=2)
        l4=Label(window,text="穴數:",font=("Courier", 30))
        l4.grid(row=2,column=0)
        self.l5=Label(window,text="停止",font=("Courier", 45))
        self.l5['fg'] ="red"
        self.l5.grid(row=3,column=3)
        machine_id=StringVar()
        self.e1=Entry(window,textvariable=machine_id,font=("Courier", 24))
        self.e1.grid(row=0,column=1)
        wo_id=StringVar()
        self.e2=Entry(window,textvariable=wo_id,font=("Courier", 24))
        self.e2.grid(row=0,column=3)
        wo_num=StringVar()
        self.e3=Entry(window,textvariable=wo_num,font=("Courier", 24))
        self.e3.grid(row=1,column=1)
        op=StringVar()
        self.e4=Entry(window,textvariable=op,font=("Courier", 24))
        self.e4.grid(row=1,column=3)     
        count=StringVar()
        self.e5=Entry(window,textvariable=count,font=("Courier", 24))
        self.e5.grid(row=2,column=1)
        #POM2FA08
        #molding
        #MNG_970067
        #2
        #093173
        self.e1.insert(END, "POM2FA08")
        self.e2.insert(END, "MNG_970067")
        self.e3.insert(END, "093173")
        self.e4.insert(END, "molding")
        self.e5.insert(END, "2")
        self.list1 = Listbox(window, height=20,width=60)
        self.list1.grid(row=3,column=0,rowspan=6,columnspan=2)
        sb1= Scrollbar(window)
        sb1.grid(row=3,column=2,rowspan=10)
        sb1.configure(command= self.list1.yview)
        self.b1=Button(window,text="開始", width=20,font=("Courier", 16),command=self.detect_working)
        self.b1.grid(row=0,column=6)
        b2= Button(window,text="結束", width=20,font=("Courier", 16),command=self.end_command)
        b2.grid(row=1,column=6)
        b3 = Button(window,text="鍵盤",width=20,font=("Courier", 16),command=self.callKeyboard)
        b3.grid(column=6,row=3)
    def detect_working(self):
        wo_id = self.e2.get()
        ma_id = self.e1.get()
        lm_user = self.e3.get()
        op =  self.e4.get()
        count =self.e5.get()
        if not wo_id and not ma_id and not lm_user and not op and not count:
            messagebox.showwarning("Warning","請輸入資料!")
        else:
            self.disabledFunctions()
            data = (wo_id,ma_id,lm_user,op,count)
            distancer.start_work()
            self.stop_report_flag = False
            self.t = threading.Thread(target=distancer.detect_working, args=(data, self.que))
            self.t.start()
            self.t2 = threading.Thread(target=self.report_detect_result)
            self.t2.start()
    def disabledFunctions(self):
        self.b1['state'] = 'disabled'
        self.e1['state'] = 'disabled'
        self.e2['state'] = 'disabled'
        self.e3['state'] = 'disabled'
        self.e4['state'] = 'disabled'
        self.e5['state'] = 'disabled'
        self.l5['text'] = "執行中...."
        self.l5['fg'] ="green"
    def enabledFunctions(self):
        self.b1['state'] = 'normal'
        self.e1['state'] = 'normal'
        self.e2['state'] = 'normal'
        self.e3['state'] = 'normal'
        self.e4['state'] = 'normal'
        self.e5['state'] = 'normal'
        self.l5['text'] = "停止"
        self.l5['fg'] ="red"
    def keyboard(self):
        os.system('florence')
    def report_detect_result(self):
        ls_index = 1
        processdot = 1
        while True and not self.stop_report_flag:
            #print(self.que.qsize())
            time.sleep(1)
            self.l5['text'] = "執行中%s" %  ('.' * processdot)
            if processdot == 4:
                processdot =0
            else:
                processdot += 1
            if self.que.qsize() != 0:
                self.list1.insert(ls_index,self.que.get())
                ls_index = ls_index +1
            ls_index =1 if ls_index == 20 else False
        self.enabledFunctions()
    def end_command(self):
        distancer.stop_work()
        self.stop_report_flag = True
    def callKeyboard(self):
        added_thread = threading.Thread(target=self.keyboard)
        added_thread.start()   
window = Tk()
detectWindow(window)
window.mainloop()
