#! /usr/bin/env python3
# coding:utf-8
import time
import RPi.GPIO as GPIO
import pymssql
import datetime
import requests
import threading
import os
import logging
import numpy as np
from enum import Enum


class en_machine_status(Enum):
    stop =1
    moving_down =2
    modeling =3
    moving_up =4
    finished =5
    system_error = 6

class Distancer:
    def __init__(self,moinitor_pin,trigger_pin,echo_pin):
        #set window
        #set RaspberryyPi
        self.moinitor_pin = moinitor_pin
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Define GPIO to use on Pi
        GPIO.setup(self.moinitor_pin, GPIO.OUT)
        GPIO.setup(self.trigger_pin,GPIO.OUT)  # Trigger
        GPIO.setup(self.echo_pin,GPIO.IN)      # Echo
        self.v=343 #331+0.6T, T=Celsius
        self.machine_flag = en_machine_status.stop
        self.start_time =0
        self.end_time =0
        self.stop_flag = False
        self.conn = pymssql.connect(host='192.168.0.56',
                        user='sa',
                        password='1234',
                        database='Raspberry_pi')
        self.cur=self.conn.cursor()
    def insert(self,wo_id="",ma_id="",lm_user="",op="",count="",start_time="",end_time="",lm_time=""):
        sql = "INSERT INTO [Raspberry_pi].[dbo].[distance] (wo_id,lm_user,op,count,start_time,end_time,lm_time,ma_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        params = (wo_id,lm_user,op,count,start_time,end_time,lm_time,ma_id)
        self.cur.execute(sql,params)
        self.conn.commit()
    def loggingwarning(self,message):
        logging.basicConfig(filename='logtest.txt',  filemode='a',format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
        logging.warning(message)
    def stop_work(self):
        self.stop_flag = True
    def start_work(self):
        self.stop_flag = False
    #send_trigger_pulse must wait until the echo pin goes high and then times how long the echo pin stays high.
    def send_trigger_pulse(self):
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.0001)
        GPIO.output(self.trigger_pin, False)
    #value waits until the echo pin either goes high or low
    #timeout argument is used to provide a timeout so that if for anyreason
    def wait_for_echo(self,value, timeout):
        count = timeout
        while GPIO.input(self.echo_pin) != value and count > 0:
            count = count - 1
        #if timeout --> system_error
        if(count == 0):
            self.machine_flag == en_machine_status.stop
        return count
    def get_distance(self):
        self.send_trigger_pulse()
        self.wait_for_echo(True, 5000)
        #print("start wait_for_echo %s" % wait_for_echo(True, 5000))
        start = time.time()
        self.wait_for_echo(False, 5000)
        #print("finish wait_for_echo %s" % wait_for_echo(False, 5000))
        finish = time.time()
        pulse_len = finish - start
        #distance pulse travelled in that time is pulse_len
        #multiplied by the speed of sound (cm/s) v=3s43 #331+0.6T, T=Celsius
        #That was the distance there and back so halve the value
        distance_cm = ((pulse_len * self.v)/2 )*100
        return int(distance_cm)

    def detection_most_frequent_destence(self):
        List = []
        for i in range(0,3,1):
            List.append(self.get_distance())
            time.sleep(0.02)
        return max(set(List), key = List.count)
        #return self.get_distance()

    def get_time_strformat(self):
        x= datetime.datetime.now()
        return x.strftime("%Y-%m-%d %H:%M:%S")
    def get_datetime_strptime(self,value):
        return datetime.datetime.strptime(value, '%m/%d/%y %H:%M:%S')
    def sorted_reversed(self,value):
        if sorted(value) == list(value):
            return "up"
        elif list(reversed(sorted(value))) == list(value):
            return "down"
        else:
            return "none"

    def detect_working(self,data,queue): 
        while True and not self.stop_flag:
            t_detect_1 = self.detection_most_frequent_destence()
            time.sleep(1)
            t_detect_2 =  self.detection_most_frequent_destence()
            time.sleep(1)
            t_detect_3 =  self.detection_most_frequent_destence()
            print("de1: is %dcm. de2: %dcm. de3: %dcm." %  (t_detect_1,t_detect_2,t_detect_3))
            # deal some unnormal issuses
            if(np.std([t_detect_1,t_detect_2,t_detect_3]) > 10 or np.std([t_detect_1,t_detect_3]) ==0 
            or np.std([t_detect_1,t_detect_2]) ==0 or np.std([t_detect_2,t_detect_3]) ==0):
                self.machine_flag= en_machine_status.stop
            if(np.std([t_detect_1,t_detect_2,t_detect_3]) <= 1 and self.machine_flag == en_machine_status.stop):
                self.start_time = self.get_time_strformat()
                print("Machine  %s" % en_machine_status(self.machine_flag))
                print("start working and the starttime is %s" % self.start_time)
            elif( self.sorted_reversed([t_detect_1,t_detect_2,t_detect_3]) == "down" and np.std([t_detect_1,t_detect_2,t_detect_3]) > 2):
                self.machine_flag= en_machine_status.moving_down
                print("Machine  %s" % en_machine_status(self.machine_flag))
            elif( self.sorted_reversed([t_detect_1,t_detect_2,t_detect_3]) == "up" and self.machine_flag == en_machine_status.moving_down
            and np.std([t_detect_1,t_detect_2,t_detect_3]) > 2):
                self.machine_flag= en_machine_status.moving_up
                print("Machine  %s" % en_machine_status(self.machine_flag))
            elif(np.std([t_detect_1,t_detect_2,t_detect_3]) <= 1 and self.machine_flag == en_machine_status.moving_up):
                self.end_time = self.get_time_strformat()
                print("finish work and the starttime is %s" % self.start_time)
                print("finish work and the endtime is %s" % self.end_time)
                if self.start_time !=0:
                    if (self.get_datetime_strptime(self.end_time) - self.get_datetime_strptime(self.start_time)).seconds() > 8:
                        message = "starttime:{0} - endtime:{1}".format(self.start_time,self.end_time)
                        #loggingwarning(message)
                        self.insert(wo_id= data[0],ma_id=data[1],lm_user=data[2],op=data[3],count=data[4],start_time= self.start_time,end_time=self.end_time,lm_time=self.end_time)
                        queue.put(message)
                        #print("transation commit")   
                self.machine_flag= en_machine_status.stop
                self.start_time = 0
                self.end_time = 0
    def __del__(self):
        self.conn.close()
        GPIO.cleanup()