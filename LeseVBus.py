#Datenauswertung für DeltaSol BX Plus
#Schnittstelle Datenempfang vom VBus
#https://forum-raspberrypi.de/forum/thread/35528-daten-an-webserver-uebertragen/#
#Schnittstellen des Raspberry: dmesg | grep  tty

import serial
import MySQLdb
import time
import requests
import socket
import RPi.GPIO as GPIO
#Pfad: /usr/local/lib/python3.5/dist-packages/xknx-0.8.5-py3.5.egg/xknx/knx/telegram.py

import asyncio
import getopt
import sys
 
from xknx import XKNX
from xknx.knx import AddressFilter
from xknx.core import ValueReader
from xknx.knx import GroupAddress

ip   = "hauptrechner"
port = 54345

USBDeltaSol ='/dev/ttyACM0'
USBSunGo ='/dev/ttyACM1'
USBArduino='/dev/ttyS0'

Byt=180*[0]
Rohbyts = 180*[0]   #array mit 112 leeren Elementen
AnzToArduino = 240
FromArd = 180*[0] #Daten, die vomArduino kommen
ToArd = list() #Daten, die vomArduino kommen

DZa = 0
SZa = 0
AZa = 0
KNXZa = 0
AnzDelta = 0
AnzSunGo = 0
AnzArduino = 0

readUSB = 1
AktZeit = time.time()
AktPCZeit = time.time()
KNXZeit = time.time()

#Bytposition (null basierend)
BytNr = [92,94,96,98,99,101,103,104,106,110,112,114,115,116,117,118,120,122,124,126,127,129,131,133,134,135,136,137,138,140,142,144,146,147,148,149,151,152,156]

def INIT():
    global ToArd,AnzToArduino
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT) #lese KNX
    GPIO.setup(13, GPIO.OUT) #lese deltasol
    GPIO.setup(16, GPIO.OUT) #lese Sun Go
    GPIO.setup(18, GPIO.OUT) #Lese Aruino

    for i in range(0, AnzToArduino):
        ToArd.append(i)
   
###################################################################

async def LeseAdresse():
    global Byt
    """Connect and read value from KNX bus."""
    xknx = XKNX()
    await xknx.start()
    
    for GA in range(0,38):
        Adresse = '0/0/'+ str(GA)
        value_reader = ValueReader(xknx, GroupAddress(Adresse))
        telegram = await value_reader.read()
        if telegram is not None:
            Z=str(telegram)
            Teilen= Z.split('-')
            GrAdr = int(Teilen[0])
            Wert = Teilen[1].split(',')
            
            #an der richtigen Stelle im Array ablegen
            for n in range(len(Wert)):  
                Byt[BytNr[GrAdr-1]+n]= int(Wert[n])
                #print (n,BytNr[GrAdr-1]+n,int(Wert[n]))
            
    await xknx.stop()
 ################# Unterprogramme ################################
def GPIO_schalten(Nr):
          GPIO.output(11, GPIO.HIGH)
          GPIO.output(13, GPIO.HIGH)
          GPIO.output(16, GPIO.HIGH)
          GPIO.output(18, GPIO.HIGH)
          if Nr >  0:
              GPIO.output(Nr, GPIO.LOW)     
     
 ################# Unterprogramme ################################
def DateninDatenbank():
    
    Spalten= "(Temperatur1,Temperatur2,Temperatur3,Temperatur4)"
    Values = ' VALUES (%d,%d,%d,%d);' % (Wert(0),Wert(2),Wert(4),Wert(6))
     
    SQL_Befehl = "INSERT INTO messdaten " + Spalten + Values 
    curs.execute (SQL_Befehl)
    DB.commit()
###################################################################
def DatenzumPC():  #über UDP
    global AktPCZeit
    Tpc=5   #Sendepause, nur alle 20 sec zum Server senden
    if (time.time()- AktPCZeit) < Tpc: return
    AktPCZeit = time.time()
      
    outstr=', '.join(str(x) for x in Byt[:151])
    #print (outstr)
    Test =str(outstr)
    sock.sendto(Test.encode('utf-8'), (ip, port))
    
################# Unterprogramme ################################
def DatenzuHeisopo():  
    global AktZeit
    Theisopo=30   #Sendepause, nur alle 20 sec zum Server senden
    
    if (time.time()- AktZeit) < Theisopo: return
    AktZeit = time.time()
 
    outstr=', '.join(str(x) for x in Byt)
    url = "http://www.heisopo.de/Raspberry/EingangRaspberry.php"
    payload ={'Value': outstr}
    r = requests.post(url, data=payload)

    print (r.text)
    #print (r.url)
#########################################################################
def DatenzumArduino():
        Arduino.write(ToArd)
     
    
################# Unterprogramme ################################
def DatenzumServer():
    url = "http://heisopi/Heizung/DeltaSolDaten.php"
    r = requests.post(url)
    print (r)
###########################################################    
def BytsDarstellen(AnzFrames):
    for FrameNr in range(1,AnzFrames+1):
         Startbyt = FrameNr * 6 + 4
         check = 0
         #print (Startbyt+6)
         for j in range(Startbyt,Startbyt+6):
                        check = check+Rohbyts[j]
         
         if (check | 128) & 255 == 255:            #Cheksumme OK!
                #MSB setzen
                MSB = Rohbyts[Startbyt + 4]
                for j in range(0,4):
                    if (MSB & (1<<j)) > 0:
                        Rohbyts[Startbyt + j] = Rohbyts[Startbyt + j] | 128
                    Index = 4*(FrameNr-1) + j
                    if AnzFrames == 9: 	Index += 56
                    
                    Byt[Index] = Rohbyts[Startbyt + j]
                    #print(Index," ",FrameNr,Startbyt," ",j,Startbyt + j,Byt[Index] )
                  
         else: print (FrameNr,"Check nicht OK",Startbyt,check)
                 
    #for i in range(0,10):
   # print (ValuByte)

    print(time.strftime("%d.%m.%Y %H:%M:%S"),"DeltaSol:", AnzDelta,"SunGo:",AnzSunGo,"Arduino:",AnzArduino, "KNX:",KNXZa)

###########################################################    
def ArduinoBytsAuswerten(i,Ard):
      
        data = str(Ard)
        data1=data.split(",")
        del data1[0]  #erstes Element entfernen (ARD)
        del data1[len(data1)-1]  #letztes Element entfernen
        for n in range(0,len(data1)):
            FromArd[n]=int(data1[n])  
        #print (FromArd)
        
################################################################

#Verbindung zur Datenbank öffnen
#DB = MySQLdb.connect(host="localhost",db="Hausrechner",user="root", passwd="tester")
#curs = DB.cursor()
INIT()

#Serielle Schnittstellen öffnen
DeltaSol = serial.Serial(USBDeltaSol, 9600, timeout= 5) 
SunGo = serial.Serial(USBSunGo, 9600, timeout= 5) 
Arduino =serial.Serial(USBArduino, 57600, timeout= 10) 
DeltaSol.isOpen()
SunGo.isOpen()
Arduino.isOpen()

sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

Tknx=30   #Sendepause, nur alle 30 sec KNX-Gruppen lesen   
KNXZeit = time.time() - Tknx  
try:
    while True:   
###########-Lese KNX-Gruppenadresse ###########
        if (time.time()- KNXZeit) > Tknx:
            KNXZeit = time.time()
            GPIO_schalten(11)
            KNXZa += 1
            loop = asyncio.get_event_loop()
            loop.run_until_complete(LeseAdresse())
###########-Lese DeltaSol ######################  
        while readUSB == 1:
            GPIO_schalten(13)
                #print ("Lese DeltaSol")
            try:  
                DS = DeltaSol.read()
                if DS[0] == 170:
                    DZa = 0
                    #print ("Sync-Byte gefunden")
                Rohbyts[DZa]=DS[0]
                DZa += 1
                #print(DZa,DS[0])       
                
                if DZa == 112 and Rohbyts[1]==16 and Rohbyts[2] == 0:
                    if Rohbyts[8]==17:
                        AnzDelta +=1
                        BytsDarstellen(14)  #Anzahl der auszuwertenden Frames = 14
                        readUSB = 2
            except:          
                  print("keine Daten von DeltaSol")
                  readUSB = 2
                        
###########-Lese SunGo- ##############
        while readUSB == 2:
            GPIO_schalten(16)
            try:
                #print ("Lese SunGo")
                SG = SunGo.read()
                if SG[0] == 170:
                    SZa = 0
                Rohbyts[SZa]=SG[0]
                SZa +=1
                if  SZa == 70 and Rohbyts[1]==16 and Rohbyts[2] == 0:
                    if Rohbyts[8]==10:
                        BytsDarstellen(9)  
                        AnzSunGo +=1        
                        readUSB = 3
            except:          
                  print("keine Daten von SunGo")
                  readUSB = 3           
###########-Lese Arduino - ##############
        while readUSB == 3:
            GPIO_schalten(18)
            try:
                Ard = Arduino.readline()
                print ("Arduino=",len(Ard))
                if len(Ard)== 0: #Keine Daten-> Fehler erzeugen
                     raise
               
                for i in range(0,len(Ard)):
                    #Suche nach 'ARD'
                    if Ard[i]==65 and Ard[i+1]==82 and Ard[i+2]==68:
                        ArduinoBytsAuswerten(i,Ard)
                        AnzArduino +=1
                        readUSB = 1
            except:
                  print("keine Daten von Arduino")
                  readUSB = 1
                  
#######################################################       
        GPIO_schalten(0)  #Alle LED aus
        if (AnzDelta + AnzSunGo) > 1:
            DatenzuHeisopo()
            DatenzumPC()
            DatenzumArduino()
       

except KeyboardInterrupt:
        print ("Verbindung geschlossen")
        #GPIO.output(16, 0)
        GPIO.output(18, 0)
        GPIO.cleanup()
        loop.close() 
        DeltaSol.close()
        SunGo.close()

