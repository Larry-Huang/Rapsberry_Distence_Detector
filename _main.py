#! /usr/bin/env python3
# coding:utf-8
#Project: Rapsberry_Distence_Detector
#RaspberryyPi 3 Model B+
#Hardware: 
#IC: HC-SR04 Ultrasonic Ranging and report Machine efficent data.
#Editor: Jerry

#import tkinter as tk
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

#set Enum
class Machine_Status(Enum):
    stop =1
    moving_down =2
    modeling =3
    moving_up =4
    finished =5
    system_error = 6

logging.basicConfig(
    filename='logtest.txt',  filemode='a',
    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')                  

#set window
#set RaspberryyPi
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Define GPIO to use on Pi
moinitor_pin = 26
trigger_pin = 23
echo_pin = 24
GPIO.setup(moinitor_pin, GPIO.OUT)
GPIO.setup(trigger_pin,GPIO.OUT)  # Trigger
GPIO.setup(echo_pin,GPIO.IN)      # Echo
v=343 #331+0.6T, T=Celsius
#set machine_flag  to stop 
machine_flag = Machine_Status.stop
start_time =0
end_time =0


#send_trigger_pulse must wait until the echo pin goes high and then times how long the echo pin stays high.
def send_trigger_pulse():
    GPIO.output(trigger_pin, True)
    time.sleep(0.0001)
    GPIO.output(trigger_pin, False)

#value waits until the echo pin either goes high or low
#timeout argument is used to provide a timeout so that if for anyreason
def wait_for_echo(value, timeout):
    count = timeout
    while GPIO.input(echo_pin) != value and count > 0:
        count = count - 1
    #if timeout --> system_error
    if(count == 0):
        global sys_flag
        sys_flag = Machine_Status.system_error
    return count

def get_distance():
    send_trigger_pulse()
    wait_for_echo(True, 5000)
    #print("start wait_for_echo %s" % wait_for_echo(True, 5000))
    start = time.time()
    wait_for_echo(False, 5000)
    #print("finish wait_for_echo %s" % wait_for_echo(False, 5000))
    finish = time.time()
    pulse_len = finish - start
    #distance pulse travelled in that time is pulse_len
    #multiplied by the speed of sound (cm/s) v=3s43 #331+0.6T, T=Celsius
    #That was the distance there and back so halve the value
    distance_cm = ((pulse_len *v)/2 )*100
    return int(distance_cm)

def detection_most_frequent_destence():
    List = []
    for i in range(0,5,1):
        List.append(get_distance())
        time.sleep(0.01)
    return max(set(List), key = List.count)

def get_time_strformat():
    x= datetime.datetime.now()
    return x.strftime("%Y-%m-%d %H:%M:%S")

def sorted_reversed(value):
    if sorted(value) == list(value):
        return "up"
    elif list(reversed(sorted(value))) == list(value):
        return "down"
    else:
        return "none"

def detect_working():
    global machine_flag
    #suspend_time = 0
    global start_time, end_time
    while True:
        t_detect_1 = detection_most_frequent_destence()
        print("The t_detect_1 is %dcm." % t_detect_1)
        time.sleep(1)
        t_detect_2 =  detection_most_frequent_destence()
        print("The t_detect_2 is %dcm." % t_detect_2)
        time.sleep(1)
        t_detect_3 =  detection_most_frequent_destence()
        print("The t_detect_3 is %dcm." % t_detect_3)
        # deal some unnormal issuses
        if(np.std([t_detect_1,t_detect_2,t_detect_3]) > 10):
            machine_flag= Machine_Status.stop
        if(np.std([t_detect_1,t_detect_2,t_detect_3]) <= 1 and machine_flag == Machine_Status.stop):
            start_time = get_time_strformat()
            print("Machine  %s" % Machine_Status(machine_flag))
            print("start working and the starttime is %s" %start_time)
        elif( sorted_reversed([t_detect_1,t_detect_2,t_detect_3]) == "down" and 3 < np.std([t_detect_1,t_detect_2,t_detect_3]) < 7.5):
            machine_flag= Machine_Status.moving_down
            print("Machine  %s" % Machine_Status(machine_flag))
        elif( sorted_reversed([t_detect_1,t_detect_2,t_detect_3]) == "up" and machine_flag == Machine_Status.moving_down
        and 3 < np.std([t_detect_1,t_detect_2,t_detect_3]) < 7.5):
            machine_flag= Machine_Status.moving_up
            print("Machine  %s" % Machine_Status(machine_flag))
        elif(np.std([t_detect_1,t_detect_2,t_detect_3]) <= 1 and machine_flag == Machine_Status.moving_up):
            end_time = get_time_strformat()
            print("finish work and the starttime is %s" %start_time)
            print("finish work and the endtime is %s" %end_time)
           
            if(start_time !=0):
                message = "starttime:{0} - endtime:{1}".format(start_time,end_time)
                logging.warning(message)
                print("transation commit")
                
            machine_flag= Machine_Status.stop
            start_time=0
            end_time = 0
          
try: 
    #while True:
    detect_working()
        #print("The distence is %scm." % detection_most_frequent_destence())
        #detection_most_frequent_destence()
       

except KeyboardInterrupt:
    print ("Exception: KeyboardInterrupt\n")

finally:
    GPIO.cleanup()
    

