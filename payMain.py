#!/usr/bin/python3

import multiprocessing as mp
import serial
from time import sleep
import time
from jsonrpcserver import method,serve
import os
import sys
import random
import subprocess
import shutil
from alexloger import *
from paypayorder import PayPayOrder
from PayPayCupOrder import PayPayCupOrder,pay_pay_cup_order_from_dict
import json
from AllConfig import J2,J3,J17,J33,J34,Track
from pca9675 import PCA9675I2C

pcaW11=PCA9675I2C(address=0x11,busnum=1)
pcaW11_Data = 0xFFFF
pcaW15=PCA9675I2C(address=0x15,busnum=1)
pcaW15_Data = 0xFFFF
pcaW18=PCA9675I2C(address=0x18,busnum=1)
pcaW18_Data = 0xFFFF
pcaW1c=PCA9675I2C(address=0x1c,busnum=1)
pcaW1c_Data = 0xFFFF
pcaW28=PCA9675I2C(address=0x28,busnum=1)
pcaW28_Data = 0xFFFF
pcaW2a=PCA9675I2C(address=0x2a,busnum=1)
pcaW2a_Data = 0xFFFF
pcaW2c=PCA9675I2C(address=0x2c,busnum=1)
pcaW2c_Data = 0xFFFF
pcaR27=PCA9675I2C(address=0x27,busnum=1)
pcaR26=PCA9675I2C(address=0x26,busnum=1)

pcaW18_Data=pcaW18.output(J34.pin2,0,pcaW18_Data)  ### 出杯轉盤方向    ###
pcaW18_Data=pcaW18.output(J34.pin4,0,pcaW18_Data)  ### 出杯轉盤關閉    ###

usbpath =''
with open("/home/pi/paypaymachine/TrackUsb.json", 'r') as obj1:
        usbpath = json.load(obj1)
with open("/home/pi/paypaymachine/PrinterUsb.json", "r") as obj1:
        Printer = json.load(obj1)
TrainA = usbpath[Track.ATrainID]
serA=serial.Serial(TrainA,57600)
TrainB = usbpath[Track.BTrainID]
serB=serial.Serial(TrainB,57600)
TrackY = usbpath[Track.YTrackID]
serY=serial.Serial(TrackY,57600)
TrackZ = usbpath[Track.ZTrackID]
serZ=serial.Serial(TrackZ,57600)
serP=serial.Serial(Printer,57600)
serP.bytesize=serial.EIGHTBITS

TrackAState='NoRun'
TrackBState='NoRun'
iocontrolsleep = 0.5

def CheckTrainA_Cup():
    if pcaR27.input(J3.pin2) != 0 : ### A道第一管有杯子###
        return True
    if pcaR27.input(J3.pin5) != 0 : ### A道第二管有杯子###
        return True
    return False
def CheckTrainB_Cup():
    if pcaR27.input(J2.pin2) != 0 : ### B道第一管有杯子###
        return True
    if pcaR27.input(J2.pin5) != 0 : ### B道第二管有杯子###
        return True
    return False

def StationA_S0(track,opentime):
    global pcaW18_Data
    print('S0 Start')
    if track == "A":
        print('S0A')
        TrackAState = 's0'
        if pcaR27.input(J3.pin2) != 0 :       ### A道第一管有杯子先用第一管 ###
            serA.write(bytes(Track.PositionStart + "\r\n" , "utf-8"))
            time.sleep(0.1) 
            serA.write(bytes(Track.Move + "\r\n" , "utf-8"))
            while True: ## 等待A軌道到位信號 ##
                serA.flushInput() 
                serA.write(bytes(Track.CheckSign + "\r\n" , "utf-8"))
                time.sleep(0.1)
                address=serA.read(13).decode("utf-8")
                # print(address)
                na=address[11:13]
                # print(na)
                bc = " ".join(format(ord(c), "b") for c in na)
                # print(bc,type(bc))
                if len(bc) == 15:
                    bin=bc[13]
                    # print(bin,type(bin))
                    if  bin == "1":
                        break
            if pcaR27.input(J3.pin8) == 0 : ## A道杯架沒有杯子 ##
                pcaW18_Data=pcaW18.output(J17.pin2,0,pcaW18_Data) ### A道第一管落杯器動作 ###
                time.sleep(0.1)
                pcaW18_Data=pcaW18.output(J33.pin2,1,pcaW18_Data) ### 冰塊推桿到A ###
                while True: ## 等待杯子落下
                    if pcaR27.input(J3.pin8) != 0 :
                        pcaW18_Data=pcaW18.output(J17.pin2,1,pcaW18_Data)  ### A道第一管落杯器關閉  ###
                        break
        elif pcaR27.input(J3.pin5) != 0 : ### A道第二管有杯子 ###
            serA.write(bytes(Track.PositionCup2 + "\r\n" , "utf-8"))
            time.sleep(0.1) 
            serA.write(bytes(Track.Move + "\r\n" , "utf-8"))
            while True: ## 等待A軌道到位信號 ##
                serA.flushInput() 
                serA.write(bytes(Track.CheckSign + "\r\n" , "utf-8"))
                time.sleep(0.1)
                address=serA.read(13).decode("utf-8")
                # print(address)
                na=address[11:13]
                # print(na)
                bc = " ".join(format(ord(c), "b") for c in na)
                # print(bc,type(bc))
                if len(bc) == 15:
                    bin=bc[13]
                    # print(bin,type(bin))
                    if  bin == "1":
                        break
            if pcaR27.input(J3.pin8) == 0 : ## A道杯架沒有杯子 ##
                pcaW18_Data=pcaW18.output(J17.pin4,0,pcaW18_Data) ### A道第二管落杯器動作 ###
                time.sleep(0.1)
                pcaW18_Data=pcaW18.output(J33.pin2,1,pcaW18_Data) ### 冰塊推桿到A ###
                while True: ## 等待杯子落下
                    if pcaR27.input(J3.pin8) != 0 :
                        pcaW18_Data=pcaW18.output(J17.pin4,1,pcaW18_Data)  ### A道第二管落杯器關閉  ###
                        break
        time.sleep(1)
        serA.write(bytes(Track.PositionIce + "\r\n" , "utf-8")) ## 移動到A道落冰處 ##
        time.sleep(0.1) 
        serA.write(bytes(Track.Move + "\r\n" , "utf-8"))
        while True: ## 等待A軌道到位信號 ##
            serA.flushInput() 
            serA.write(bytes(Track.CheckSign + "\r\n" , "utf-8"))
            time.sleep(0.1)
            address=serA.read(13).decode("utf-8")
            # print(address)
            na=address[11:13]
            # print(na)
            bc = " ".join(format(ord(c), "b") for c in na)
            # print(bc,type(bc))
            if len(bc) == 15:
                bin=bc[13]
                # print(bin,type(bin))
                if  bin == "1":
                    break
        time.sleep(1)
        for i in range(opentime*2): #Evan 點放出冰
            time.sleep(0.3)
            pcaW18_Data=pcaW18.output(J33.pin4,0,pcaW18_Data) ###給冰電磁閥開啟###
            time.sleep(0.3)
            pcaW18_Data=pcaW18.output(J33.pin4,1,pcaW18_Data) ###給冰電磁閥關閉###
        time.sleep(2)
        print("S0A道做完囉")
        TrackAState = 'NoRun'
    elif track == "B":
        print('S0B')
        TrackBState = 's0'
        if pcaR27.input(J2.pin2) != 0 :       ### B道第一管有杯子先用第一管 ###
            serB.write(bytes(Track.PositionStart + "\r\n" , "utf-8"))
            time.sleep(0.1) 
            serB.write(bytes(Track.Move + "\r\n" , "utf-8"))
            while True: ## 等待B軌道到位信號 ##
                serB.flushInput() 
                serB.write(bytes(Track.CheckSign + "\r\n" , "utf-8"))
                time.sleep(0.1)
                address=serB.read(13).decode("utf-8")
                # print(address)
                na=address[11:13]
                # print(na)
                bc = " ".join(format(ord(c), "b") for c in na)
                # print(bc,type(bc))
                if len(bc) == 15:
                    bin=bc[13]
                    # print(bin,type(bin))
                    if  bin == "1":
                        break
            if pcaR27.input(J2.pin8) == 0 : ## B道杯架沒有杯子 ##
                pcaW18_Data=pcaW18.output(J17.pin6,0,pcaW18_Data) ### B道第一管落杯器動作 ###
                time.sleep(0.1)
                pcaW18_Data=pcaW18.output(J33.pin2,0,pcaW18_Data) ### 冰塊推桿到B ###
                while True: ## 等待杯子落下
                    if pcaR27.input(J2.pin8) != 0 :
                        pcaW18_Data=pcaW18.output(J17.pin6,1,pcaW18_Data)  ### B道第一管落杯器關閉  ###
                        break
        elif pcaR27.input(J2.pin5) != 0 : ### B道第二管有杯子 ###
            serB.write(bytes(Track.PositionCup2 + "\r\n" , "utf-8"))
            time.sleep(0.1) 
            serB.write(bytes(Track.Move + "\r\n" , "utf-8"))
            while True: ## 等待A軌道到位信號 ##
                serB.flushInput() 
                serB.write(bytes(Track.CheckSign + "\r\n" , "utf-8"))
                time.sleep(0.1)
                address=serB.read(13).decode("utf-8")
                # print(address)
                na=address[11:13]
                # print(na)
                bc = " ".join(format(ord(c), "b") for c in na)
                # print(bc,type(bc))
                if len(bc) == 15:
                    bin=bc[13]
                    # print(bin,type(bin))
                    if  bin == "1":
                        break
            if pcaR27.input(J2.pin8) == 0 : ## B道杯架沒有杯子 ##
                pcaW18_Data=pcaW18.output(J17.pin8,0,pcaW18_Data) ### B道第二管落杯器動作 ###
                time.sleep(0.1)
                pcaW18_Data=pcaW18.output(J33.pin2,0,pcaW18_Data) ### 冰塊推桿到B ###
                while True: ## 等待杯子落下
                    if pcaR27.input(J3.pin8) != 0 :
                        pcaW18_Data=pcaW18.output(J17.pin8,1,pcaW18_Data)  ### B道第二管落杯器關閉  ###
                        break
        time.sleep(1)
        serB.write(bytes(Track.PositionIce + "\r\n" , "utf-8")) ## 移動到B道落冰處 ##
        time.sleep(0.1) 
        serB.write(bytes(Track.Move + "\r\n" , "utf-8"))
        while True: ## 等待B軌道到位信號 ##
            serB.flushInput() 
            serB.write(bytes(Track.CheckSign + "\r\n" , "utf-8"))
            time.sleep(0.1)
            address=serB.read(13).decode("utf-8")
            # print(address)
            na=address[11:13]
            # print(na)
            bc = " ".join(format(ord(c), "b") for c in na)
            # print(bc,type(bc))
            if len(bc) == 15:
                bin=bc[13]
                # print(bin,type(bin))
                if  bin == "1":
                    break
        time.sleep(1)
        for i in range(opentime*2): #Evan 點放出冰
            time.sleep(0.3)
            pcaW18_Data=pcaW18.output(J33.pin4,0,pcaW18_Data) ###給冰電磁閥開啟###
            time.sleep(0.3)
            pcaW18_Data=pcaW18.output(J33.pin4,1,pcaW18_Data) ###給冰電磁閥關閉###
        time.sleep(2)
        print("S0B道做完囉")
        TrackBState = 'NoRun'
    print('S0 END')       

def StationB_S1_Atrain(time1,time2,time3,time4,time5):
    pump = pcaW15
    doorA = pcaW1c
        if time1 !=0 :
            # print("1")
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J17.pin2,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin2,0,pcaW15_Data)
            time.sleep(time1)
            pcaW15_Data=pump.output(J17.pin2,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J17.pin2,1,pcaW1c_Data)
        if time2 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J17.pin4,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin4,0,pcaW15_Data)
            time.sleep(time2)
            pcaW15_Data=pump.output(J17.pin4,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J17.pin4,1,pcaW1c_Data)
        if time3 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J17.pin6,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin6,0,pcaW15_Data)
            time.sleep(time3)
            pcaW15_Data=pump.output(J17.pin6,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J17.pin6,1,pcaW1c_Data)
        if time4 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J17.pin8,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin8,0,pcaW15_Data)
            time.sleep(time4)
            pcaW15_Data=pump.output(J17.pin8,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J17.pin8,1,pcaW1c_Data)
        if time5 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J33.pin2,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin2,0,pcaW15_Data)
            time.sleep(time5)
            pcaW15_Data=pump.output(J33.pin2,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J33.pin2,1,pcaW1c_Data)

def StationB_S1_Btrain(time1,time2,time3,time4,time5):
    pump = pcaW15
    doorB = pcaW11
        if time1 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J17.pin2,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin2,0,pcaW15_Data)
            time.sleep(time1)
            pcaW11_Data=doorB.output(J17.pin2,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin2,1,pcaW15_Data)
        if time2 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J17.pin4,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin4,0,pcaW15_Data)
            time.sleep(time2)
            pcaW11_Data=doorB.output(J17.pin4,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin4,1,pcaW15_Data)
        if time3 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J17.pin6,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin6,0,pcaW15_Data)
            time.sleep(time3)
            pcaW11_Data=doorB.output(J17.pin6,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin6,1,pcaW15_Data)
        if time4 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J17.pin8,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin8,0,pcaW15_Data)
            time.sleep(time4)
            pcaW11_Data=doorB.output(J17.pin8,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J17.pin8,1,pcaW15_Data)
        if time5 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J33.pin2,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin2,0,pcaW15_Data)
            time.sleep(time5)
            pcaW11_Data=doorB.output(J33.pin2,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin2,1,pcaW15_Data)

def StationB_S1(track,timedata):
    time1=int(timedata[2:4])
    time2=int(timedata[6:8])
    time3=int(timedata[10:12])
    time4=int(timedata[14:16])
    time5=int(timedata[18:20])
    if time1 == 0 and time2 == 0 and time3 == 0 and time4 == 0 and time5 == 0:
        return True
    if track == "A":
        TrackAState = s1
        serA.write(bytes(TrainA.PositionS1 + "\r\n" , "utf-8"))
        time.sleep(0.1) 
        serA.write(bytes(TrainA.Move + "\r\n" , "utf-8"))
        while True: ## 等待A軌道到位信號 ##
            serA.flushInput() 
            serA.write(bytes(TrainA.CheckSign + "\r\n" , "utf-8"))
            time.sleep(0.1)
            address=serA.read(13).decode("utf-8")
            # print(address)
            na=address[11:13]
            # print(na)
            bc = " ".join(format(ord(c), "b") for c in na)
            # print(bc,type(bc))
            if len(bc) == 15:
                bin=bc[13]
                # print(bin,type(bin))
                if  bin == "1":
                    break
        StationB_S1_Atrain(time1,time2,time3,time4,time5)
        time.sleep(2)
        TrackAState = NoRun
    elif track == "B":
        TrackBState = s1
        serB.write(bytes(TrainB.PositionS1 + "\r\n" , "utf-8"))
        time.sleep(0.1) 
        serB.write(bytes(TrainB.Move + "\r\n" , "utf-8"))
        while True: ## 等待B軌道到位信號 ##
            serB.flushInput() 
            serB.write(bytes(TrainB.CheckSign + "\r\n" , "utf-8"))
            time.sleep(0.1)
            address=serB.read(13).decode("utf-8")
            # print(address)
            na=address[11:13]
            # print(na)
            bc = " ".join(format(ord(c), "b") for c in na)
            # print(bc,type(bc))
            if len(bc) == 15:
                bin=bc[13]
                # print(bin,type(bin))
                if  bin == "1":
                    break
        StationB_S1_Btrain(time1,time2,time3,time4,time5)
        time.sleep(2)
        TrackBState = NoRun
def StationC_S2_Atrain(time1,time2,time3,time4,time5):
    pump = pcaW15
    doorA = pcaW1c 
        if time1 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J33.pin4,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin4,0,pcaW15_Data)
            time.sleep(time1)
           pcaW15_Data=pump.output(J33.pin4,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J33.pin4,1,pcaW1c_Data)
        if time2 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J33.pin6,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin6,0,pcaW15_Data)
            time.sleep(time2)
            pcaW15_Data=pump.output(J33.pin6,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J33.pin6,1,pcaW1c_Data)
        if time3 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J33.pin8,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin8,0,pcaW15_Data)
            time.sleep(time3)
            pcaW15_Data=pump.output(J33.pin8,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J33.pin8,1,pcaW1c_Data)
        if time4 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J34.pin2,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J34.pin2,0,pcaW15_Data)
            time.sleep(time4)
            pcaW15_Data=pump.output(J34.pin2,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J34.pin2,1,pcaW1c_Data)
        if time5 !=0 :
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J34.pin4,0,pcaW1c_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J34.pin4,0,pcaW15_Data)
            time.sleep(time5)
            pcaW15_Data=pump.output(J34.pin4,1,pcaW15_Data)
            time.sleep(iocontrolsleep)
            pcaW1c_Data=doorA.output(J34.pin4,1,pcaW1c_Data)

def StationC_S2_Btrain(time1,time2,time3,time4,time5):
    pump = pcaW15
    doorB = pcaW11
        if time1 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J33.pin4,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin4,0,pcaW15_Data)
            time.sleep(time1)
            pcaW11_Data=doorB.output(J33.pin4,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin4,1,pcaW15_Data)
        if time2 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J33.pin6,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin6,0,pcaW15_Data)
            time.sleep(time2)
            pcaW11_Data=doorB.output(J33.pin6,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin6,1,pcaW15_Data)
        if time3 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J33.pin8,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin8,0,pcaW15_Data)
            time.sleep(time3)
            pcaW11_Data=doorB.output(J33.pin8,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J33.pin8,1,pcaW15_Data)
        if time4 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J34.pin2,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J34.pin2,0,pcaW15_Data)
            time.sleep(time4)
            pcaW11_Data=doorB.output(J34.pin2,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J34.pin2,1,pcaW15_Data)
        if time5 !=0 :
            time.sleep(iocontrolsleep)
            pcaW11_Data=doorB.output(J34.pin4,0,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J34.pin4,0,pcaW15_Data)
            time.sleep(time5)
            pcaW11_Data=doorB.output(J34.pin4,1,pcaW11_Data)
            time.sleep(iocontrolsleep)
            pcaW15_Data=pump.output(J34.pin4,1,pcaW15_Data)

def StationC_S2(track,timedata):
    time1=int(timedata[2:4])
    time2=int(timedata[6:8])
    time3=int(timedata[10:12])
    time4=int(timedata[14:16])
    time5=int(timedata[18:20])
    if time1 == 0 and time2 == 0 and time3 == 0 and time4 == 0 and time5 == 0:
        return True
    if track == "A":
        TrackAState = s2
        serA.write(bytes(TrainA.PositionS2 + "\r\n" , "utf-8"))
        time.sleep(0.1) 
        serA.write(bytes(TrainA.Move + "\r\n" , "utf-8"))
        while True: ## 等待A軌道到位信號 ##
            serA.flushInput() 
            serA.write(bytes(TrainA.CheckSign + "\r\n" , "utf-8"))
            time.sleep(0.1)
            address=serA.read(13).decode("utf-8")
            # print(address)
            na=address[11:13]
            # print(na)
            bc = " ".join(format(ord(c), "b") for c in na)
            # print(bc,type(bc))
            if len(bc) == 15:
                bin=bc[13]
                # print(bin,type(bin))
                if  bin == "1":
                    break
        StationC_S2_Atrain(time1,time2,time3,time4,time5)
        time.sleep(2)
        TrackAState = NoRun
    elif track == "B":
        TrackBState = s2
        serB.write(bytes(TrainB.PositionS2 + "\r\n" , "utf-8"))
        time.sleep(0.1) 
        serB.write(bytes(TrainB.Move + "\r\n" , "utf-8"))
        while True: ## 等待B軌道到位信號 ##
            serB.flushInput() 
            serB.write(bytes(TrainB.CheckSign + "\r\n" , "utf-8"))
            time.sleep(0.1)
            address=serB.read(13).decode("utf-8")
            # print(address)
            na=address[11:13]
            # print(na)
            bc = " ".join(format(ord(c), "b") for c in na)
            # print(bc,type(bc))
            if len(bc) == 15:
                bin=bc[13]
                # print(bin,type(bin))
                if  bin == "1":
                    break
        StationC_S2_Btrain(time1,time2,time3,time4,time5)
        time.sleep(2)
        TrackBState = NoRun
def StationD_S3(track,timedata):
    time1=int(timedata[2:4])
    time2=int(timedata[6:8])
    time3=int(timedata[10:12])
    time4=int(timedata[14:16])
    time5=int(timedata[18:20])
    if time1 == 0 and time2 == 0 and time3 == 0 and time4 == 0 and time5 == 0:
        return True
    if track == "A":
        TrackAState = s3

        TrackAState = NoRun
    elif track == "B":
        TrackBState = s3

        TrackBState = NoRun
def StationE_S4(track,timedata):
    time1=int(timedata[2:4])
    time2=int(timedata[6:8])
    time3=int(timedata[10:12])
    time4=int(timedata[14:16])
    time5=int(timedata[18:20])
    if time1 == 0 and time2 == 0 and time3 == 0 and time4 == 0 and time5 == 0:
        return True
    if track == "A":
        TrackAState = s4

        TrackAState = NoRun
    elif track == "B":
        TrackBState = s4

        TrackBState = NoRun
def StationF_S5(track,timedata):
    time1=int(timedata[2:4])
    time2=int(timedata[6:8])
    time3=int(timedata[10:12])
    time4=int(timedata[14:16])
    time5=int(timedata[18:20])
    if time1 == 0 and time2 == 0 and time3 == 0 and time4 == 0 and time5 == 0:
        return True
    if track == "A":
        TrackAState = s5

        TrackAState = NoRun
    elif track == "B":
        TrackBState = s5

        TrackBState = NoRun

def checkSisruning(sta):
    if TrackAState == sta:
        return True
    if TrackBState == sta:
        return True
    return False
    #filename = f'./run/{sta}.run'
    #if os.path.isfile(filename):
    #    return True
    #return False
def getS0o(orderTxt):
    print(orderTxt)
def getS1o(orderTxt):
    print(orderTxt)

    
def processA(bitArray,order):
    print(f'A: pid={pid()}')
    while True:        
        if order.empty():
            logger.info('A empty')
            time.sleep(1)
            continue
        o=order.get()
        print(o)
        print(f'{o}')
        logger.info(f'A:processA {list(bitArray)},order={o}')
        bitArray[0]=1
        logger.info(f'A:aprocessA-1 {list(bitArray)},order={o}')   
        recp_dic = {"stationa":o.stationa,"stationb":o.stationb,"stationc":o.stationc,"stationd":o.stationd,"statione":o.statione,"stationf":o.stationf,"endpoint":o.cupnum}
        station_dic = {"s0":"stationa","s1":"stationb","s2":"stationc","s3":"stationd","s4":"statione","s5":"stationf","s6":"endpoint"}
        station = ["s0","s1","s2","s3","s4","s5","s6"]
        for sta in station:
            while checkSisruning(sta) is True:
                logger.info(f'A:wait 1 sec for {sta}')
                time.sleep(1)
            
            # print(f'hello-{sta}-{recp_dic[station_dic[sta]]}')
            #logger.info(f'hello-{sta}-{recp_dic[station_dic[sta]]}')   
            sec = random.randint(5,10) 
            logger.info(f'A:do {sta} A {sec} sec')
            if os.uname()[0] == 'Linux' :
                print(f'send cmd python3 {sta}.py A {recp_dic[station_dic[sta]]}')
                logger.info(f'send cmd python3 {sta}.py A {recp_dic[station_dic[sta]]}')
                p = subprocess.run(['python3',f'{sta}.py',f'A',f'{recp_dic[station_dic[sta]]}'])
            else:
                print(f'send cmd python3 {sta}.py A {recp_dic[station_dic[sta]]}')
                logger.info(f'send cmd python3 {sta}.py A {recp_dic[station_dic[sta]]}')
                p = subprocess.run(['python3',f'{sta}ta.py',f'A',f'{recp_dic[station_dic[sta]]}',f'{sec}'])
            # p = subprocess.run(['python3','s1.py',f'A',f'{sta}',f'{sec}'])
        time.sleep(2)
        bitArray[0]=0
        logger.info(f'A:processA-E {list(bitArray)},order={o}')
def processB(bitArray,order):
    print(f'B: pid={pid()}')
    while True:
        time.sleep(2)
        if order.empty():
            logger.info('B:B empty')
            time.sleep(1)
            continue
        o=order.get()
        
        logger.info(f'B:processB show train AB is available {list(bitArray)},order={o}')
        bitArray[1]=1
        logger.info(f'B:processB-1 set train B{list(bitArray)},order={o}')
        recp_dic = {"stationa":o.stationa,"stationb":o.stationb,"stationc":o.stationc,"stationd":o.stationd,"statione":o.statione,"stationf":o.stationf,"endpoint":o.cupnum}
        station_dic = {"s0":"stationa","s1":"stationb","s2":"stationc","s3":"stationd","s4":"statione","s5":"stationf","s6":"endpoint"}
        station = ["s0","s1","s2","s3","s4","s5","s6"]
        
        for sta in station:
            while checkSisruning(sta) is True:               
                logger.info(f'B:{sta} A is running , wait 1 sec for {sta} A')
                time.sleep(1)
            logger.info(f'hello-{sta}-{recp_dic[station_dic[sta]]}')
            print(f'hello-{sta}-{recp_dic[station_dic[sta]]}')
          #  logger.info(f'hello-{sta}-{recp_dic[station_dic[sta]]}')   
            sec = random.randint(5,10)
            
            logger.info(f'B:{sta} free do {sta} on B {sec} sec')
            
            if os.uname()[0] == 'Linux' :
                p = subprocess.run(['python3',f'{sta}.py',f'B',f'{recp_dic[station_dic[sta]]}'])
                print(f'send cmd python3 {sta}.py B {recp_dic[station_dic[sta]]}')
                logger.info(f'send cmd python3 {sta}.py B {recp_dic[station_dic[sta]]}')   
                
            else:
                p = subprocess.run(['python3',f'{sta}ta.py',f'B',f'{recp_dic[station_dic[sta]]}',f'{sec}'])
                print(f'send cmd python3 {sta}.py B {recp_dic[station_dic[sta]]}')
                logger.info(f'send cmd python3 {sta}.py B {recp_dic[station_dic[sta]]}')   
                
                
        time.sleep(2)
        bitArray[1]=0
        logger.info(f'B:processB-End done {list(bitArray)},order={o}')



def jsonrpcserver(q):
    @method
    def jsonrpc_addorder(order):
        print(order)
        # order='{"ordernum":"RSAP21071400002","cupcount":1,"content":[{"cupnum":"A0001","stationa":"02","stationb":"01010200030004000500","stationc":"01010200030004000500","stationd":"01000200030004000503","statione":"01010200030004000500","stationf":"01010200030004000500"}]}'
        # orderjson = json.loads(order)
        # print(orderjson)
        orderobj=PayPayOrder.from_json(order)
        # orderinfo=pay_pay_order_from_dict(order)
        print(orderobj.content)
        for cup in orderobj.content:
            ss = cup.to_dict()
            # ss=json.dumps(cup)
            cupOrder=pay_pay_cup_order_from_dict(ss)
            print('put')
            q.put(cup)
            print('put ok')
            
    serve(port=9000)    
    
    
order_queue=mp.Queue()
pid = os.getpid    
if __name__ == '__main__':
    os.remove('station_logger.log')
    os.remove('first_logfile.log')
    logger.info(order_queue)
    
    train_bit=mp.Array('i', 2)
    if os.path.isdir(f"./run") == True:
        shutil.rmtree('./run')
    os.mkdir('./run')
    
    rpcservprocess = mp.Process(target=jsonrpcserver,args=(order_queue,))
    
    StationA_S0(A,1)

    aprocess=mp.Process(target=processA,args=(train_bit,order_queue))
    bprocess=mp.Process(target=processB,args=(train_bit,order_queue))
    rpcservprocess.start()
    aprocess.start()
    bprocess.start()
    logger.info('add 5 test order to queue')
    # for i in range(2):
    #      order_queue.put(i)
    
    aprocess.join()
    bprocess.join()
