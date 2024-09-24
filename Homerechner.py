#Datenauswertung für DeltaSol BX Plus
#Schnittstelle Datenempfang vom VBus
#https://forum-raspberrypi.de/forum/thread/35528-daten-an-webserver-uebertragen/#
#Schnittstellen des Raspberry: dmesg | grep  tty



import sys
import serial
import os
#import MySQLdb

import time
#import termios
#import tty
import requests
import socket
#import subprocess
import RPi.GPIO as GPIO
#Pfad: /usr/local/lib/python3.5/dist-packages/xknx-0.8.5-py3.5.egg/xknx/knx/telegram.py
import subprocess as sp
import asyncio


#import tkinter as tk

#import sys
#import SuchePorts

from datetime import datetime
from xknx import XKNX

from xknx.core import ValueReader
from xknx.knx import GroupAddress

from pathlib import Path

#from tkinter import *

#
#root = tk.Tk()   #Ausgabefenster erzeugen
#root.title("Ausgabe des Raspberry")
#root.geometry("1000x300")
#
#Zeitlabel = tk.Label(root,fg = "light green",bg = "dark green",font = "Helvetica 16 bold italic")
#
#Zeitlabel.pack(side="left")
#
#
#button = tk.Button(root, text='Ende', width=25, command=root.destroy)
#button.pack()

#Zum Gas auslesen 
fileGas ="/mnt/ramdisk/Gasdaten.heis"
ErsteGasmessung = True


ip   = "192.168.178.34"  #Hauprechner zur UDP
ip1   = "192.168.178.40"  #zum ESP32 Gas
ESPStrom_IP = "192.168.178.60"
IPWohnzimmer ="192.168.178.52"
    
port = 54346
port1 = 54321

#Dachrechner_PORT = 7777

LEDPin=21
GesEnergie = 4*[0]
HeutEnergie  = 4*[0]
AktEnergie  = 4*[0]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDPin, GPIO.OUT)
LEDStatus = True
HandyImWLan = False
InternetOK = False

SerOK=[False,False,False]

Ser = ["ACM0","ACM1","S0"]
#Ser=["ACM1","ACM0","S0"]
#Ser = SuchePorts.SerielleSchnittstellen()
for n in range(0,3):
    if Ser[n] != "KEINE": SerOK[n]=True


USBDeltaSol ='/dev/tty'+ Ser[0] 
USBSunGo ='/dev/tty'+ Ser[1]
USBArduino='/dev/tty'+ Ser[2]

Byt=350*[0]         #Daten, die zu heisopo und über UDP zum PC gesendet werden
Rohbyts = 190*[0]   #array mit 180 leeren Elementen
FromArd = 330*[0]   #Daten, die vom Arduino kommen
Serverantwort =""
Serveranfrage = False   #wird auf true gesetzt, wenn eine Antwort von Heisopo eingeht
StromdateiGleich = 0


DZa = 0
SZa = 0
AZa = 0
KNXZa = 0
AnzDelta = 0
AnzSunGo = 0
AnzArduino = 0

readUSB = 1
AktZeit = time.time()
StromZeit = time.time()

KNXZeit = time.time()

#Bytposition (null basierend)
#BytNr = [92,94,96,98,99,101,103,104,106,110,112,114,115,116,117,118,120,122,124,126,127,129,131,133,134,135,136,137,138,140,142,144,146,147,148,149,151,152,156]
#Folgende Byts werden von Fliesskomma nach Integer umgewandelt
BytListe = [92,94,96,99,101,110,112,118,120,138,140,142,144]
#KNX-Adressen, die gelesen werden
Adressliste = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,25,26,27,28,29,30,31,32,33,36]  #44
#Bytposition, abhängig von Adressliste
Varpos = [92,94,96,98,99,101,103,104,106,110,112,114,115,116,117,118,120,134,135,136,137,138,140,142,144,146,151,152]

inkey_buffer = 1
###################################################################
def inkey():
    fd=sys.stdin.fileno()
    remember_attributes=termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    character=sys.stdin.read(inkey_buffer)
    termios.tcsetattr(fd,termios.TCSADRAIN, remember_attributes)
    return character


###################################################################
def INIT():
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT) #lese KNX
    GPIO.setup(13, GPIO.OUT) #lese deltasol
    GPIO.setup(16, GPIO.OUT) #lese Sun Go
    GPIO.setup(18, GPIO.OUT) #Lese Aruino

   
###################################################################
def FlieskommaInInt(BytNr):    
   #Umwandeln einer 2Byte Fliesskommazahl in einen Integerwert 
    
    HB = Byt[BytNr]
    LB = Byt[BytNr+1]
    
    Ex = (HB & 120) / 8
    MH = (HB & 7)
    
    if ((HB & 128) > 0):   #negative Zahl
        Mant = -(2**11-(MH * 256 + LB))
    else:
        Mant = MH * 256 + LB
        
    Erg = (0.1 * Mant) * (2 ** Ex)  #10-facher Wert
    
#    if (BytNr == 101):
#        print("Aussentemp: ",HB,LB,Erg)
#        print("Man: ",Ex,MH,LB,Mant)
       
    if (Erg < 0): Erg = Erg + 2**16
    
    Byt[BytNr+1]=  int(Erg/256)
    Byt[BytNr]=  int(Erg%256)
    
    #print(BytNr, HB,LB,Erg)
    
##    if Byt[BytNr] < 0  or Byt[BytNr+1] < 0 or Byt[BytNr] > 255 or Byt[BytNr+1] > 255:
##            print(BytNr, HB,LB,Byt[BytNr],Byt[BytNr+1])
##            print (Ex,MH,Mant,Erg)

  
##############################################################################    
def LeseWertAusZeile(Datei):
    Zeile = Datei.readline()
    Pos = Zeile.find(" = ") + 3
    Wert = Zeile[Pos:-1]
    return Wert

##############################################################################

def Gasdaten():
    global Byt
    global LetzteDateiGasAenderung, fileGas
    global ErsteGasmessung

    try:
        if (LetzteDateiGasAenderung != os.path.getmtime(fileGas) or ErsteGasmessung == True):
            #print (os.path.getmtime(fileGas))   
            Zeitstempel = time.strftime("%d.%m.%Y %H:%M:%S")
            print ("Gasmessung vom "+Zeitstempel)
            Datei = (fileGas, "r")

            Zeitpunkt = LeseWertAusZeile(Datei)
            Zeitdifferenz = LeseWertAusZeile(Datei)
            NeuerZaehlerstand = LeseWertAusZeile(Datei)
            VolStrom = LeseWertAusZeile(Datei)
            Datei.close()
            
            LetzteDateiGasAenderung = os.path.getmtime(fileGas)
            ErsteGasmessung = False
  
            print(Zeitpunkt)
            print(Zeitdifferenz)
            print(NeuerZaehlerstand)
            print(VolStrom)  
          
            Wert = int(float(NeuerZaehlerstand)*100)
            Byt[322] = (Wert) & 0xff
            Byt[323] = (Wert>>8) & 0xff
            Byt[324] = (Wert>>16) & 0xff
                            
            Wert = int(float(VolStrom) *100)
            Byt[325] = (Wert) & 0xff
            Byt[326] = (Wert>>8) & 0xff
            
    except FileNotFoundError as e:
           print  ("Datei 'Gasdaten.heis' fehlt in Ramdisk")

                                   
###################################################################

async def LeseAdresse():
    global Byt
   
   #Connect and read value from KNX bus.
    xknx = XKNX()
    await xknx.start()
    
    #for GA in range(0,38):
    for GA in Adressliste:
        Adresse = '0/0/'+ str(GA)
        #print ("Gruppe = ",str(GA))
        value_reader = ValueReader(xknx, GroupAddress(Adresse))
        telegram = await value_reader.read()
        if telegram is not None:
            Z=str(telegram)
            Teilen= Z.split('-')
            GrAdr = int(Teilen[0])
            Wert = Teilen[1].split(',')
            ind = Adressliste.index(GrAdr)
            Adr = Varpos[ind]   #an diese Position wird das Byte geschrieben
            #print (Adr,ind,GrAdr,Wert)
            #an der richtigen Stelle im Array ablegen
            for n in range(len(Wert)):  
                #Byt[BytNr[GrAdr-1]+n]= int(Wert[n])
                Byt[Adr+n]= int(Wert[n])
    await xknx.stop()
    #Byt[101]=135
    #Byt[102]=186
    for n in BytListe: 
        FlieskommaInInt(n)
  
     
   
 ################# Unterprogramme ################################
def LED_schalten():
    
    global LEDPin
    global LEDStatus
    
    if LEDStatus:   
        LEDStatus = False
    else:
        LEDStatus = True
    
    #print (LEDStatus)
    GPIO.output(LEDPin, LEDStatus)
    
 ################# Unterprogramme ################################
def DateninDatenbank():
    
    Spalten= "(Temperatur1,Temperatur2,Temperatur3,Temperatur4)"
    Values = ' VALUES (%d,%d,%d,%d);' % (Wert(0),Wert(2),Wert(4),Wert(6))
     
    SQL_Befehl = "INSERT INTO messdaten " + Spalten + Values 
    curs.execute (SQL_Befehl)
    DB.commit()
###################################################################
def DatenzumPC():  #über UDP
   
    global Serverantwort
    global Serveranfrage
    
    outstr=', '.join(str(x) for x in Byt)
    #print ("Zum PC",outstr)
    PCDaten = str(outstr)
   
    if Serveranfrage:   #Wenn Antwort von Heisopo da-> anhängen an PC Daten
        PCDaten = PCDaten + Serverantwort
        Serveranfrage = False
        
    sock.sendto(PCDaten.encode('utf-8'), (ip, port))
    print ("Sende " + str(len(Byt)) + " Bytes um PC")
  

################# Unterprogramme ################################
def DatenzuHeisopo():

    global AktZeit
    global Serverantwort
    global Serveranfrage
    
    Theisopo=30   #Sendepause, nur alle 20 sec zum Server senden
    try:   
        if (time.time()- AktZeit) < Theisopo: return
        AktZeit = time.time()
        outstr=', '.join(str(x) for x in Byt)
        #print (outstr)
        url = "http://www.heisopo.de/Raspberry/EingangRaspberry.php"
        payload ={'Value': outstr}
        Serveranfrage = True
        r = requests.post(url, data=payload)
    
        print (r.status_code)
        Serverantwort="Inet\n"+ r.text
        print (Serverantwort)
        #print ("Zu Heisopo : "+ str(Byt[286:288])+ str(Byt[292:294]))
        DatenInTextdatei(outstr)
    except:
        Serverantwort="Inet\n Keine Internetverbindung !"
        print ("Fehler: keine Internetverbindung")

################# Unterprogramme ################################          
def PVDatenZuHeisopo(PVMax):
    #zum Server schicken
             try:   
                url = "http://www.heisopo.de/Raspberry/EingangPVDaten.php"
                payload ={'PVDaten': PVMax}
                r = requests.post(url, data=payload)
                #print (r.status_code)
                print (r.text)
             except:
                print ("Fehler: keine Internetverbindung")

################################################################################          
def StromDatenZuHeisopo(Strom):
    #zum Server schicken
             try:   
                url = "http://www.heisopo.de/Raspberry/EingangStromDaten.php"
                payload ={'StromDaten': Strom}
                r = requests.post(url, data=payload)
                if (r.status_code == 500):
                    print ("Fehler im php-Sript 'EingangStromDaten.php'")
                #print (r.status_code)
                print (r.text)
             except:
                print ("Fehler: keine Internetverbindung")
                
                
################################################################################          
def ZaehlerstaendeZuHeisopo(ZST):
    #zum Server schicken
            
             try:   
                url = "http://www.heisopo.de/Raspberry/EingangZaehlerstaende.php"
                
                payload ={'Zaehlerstaende': ZST}
                r = requests.post(url, data=payload)
                if (r.status_code == 500):
                    print ("Fehler im php-Sript 'EingangZaehlerstaende.php'")
                #print (r.status_code)
                print (r.text)
             except:
                print ("Fehler: keine Internetverbindung")
                


################# Unterprogramme ################################     
#################################################################
def PVWerteSelektieren(I,PVZeile,BS):
             global GesEnergie
             global AktEnergie 
             global HeutEnergie
        
            #Macht aus der Datenzeile des Wechselrichters einzelne Werte
            
             posStart = PVZeile.find("[")+1
             posEnde = PVZeile.find("]")

             PVText= PVZeile[posStart:posEnde]
             #print ("PV-Daten=" + PVText) 
             #print ("Start:" + str(posStart) + " Ende:" + str(posEnde)+ " Länge=" + str(len(PVText)))
             
             if (len(PVText) > 10):
                 PVText = PVText.replace("'","")
                 PVText = PVText.split(", ")
                 #print ("PVText = " + str(PVText))
        
                 
                 #Aktuell erzeugte Leistung    
                 AktEnergie[I] = int(PVText[0])
                 Byt[BS] = (AktEnergie[I]) & 0xff
                 Byt[BS+1] = (AktEnergie[I]>>8) & 0xff
                 
                 #An diesem Tag erzeute Leistung
                 HeutEnergie[I] = int(float(PVText[1]) *1000)
                 Byt[BS+2] = (HeutEnergie[I]) & 0xff
                 Byt[BS+3] = (HeutEnergie[I]>>8) & 0xff
                 
                 #bisher erzeugte Gesamtleistung (Zählerstand
                 GesEnergie[I] = int(float(PVText[2])*10)
                 Byt[BS+4] = (GesEnergie[I]) & 0xff
                 Byt[BS+5] = (GesEnergie[I]>>8) & 0xff
             else:
                
                Datname = open("/mnt/ramdisk/Fehler.txt",'a')
                print(Datname.write(PVZeile+"\n"))
                Datname.close()

             #print (str(I) + " - " + str(AktEnergie[I]) + " - " +  str(HeutEnergie[I])+  "->" + str(Byt[BS:BS+2]) )   
             
################# Unterprogramme ################################        
def LeseDatenVomSolarserver():
        #Daten werden aus Textdatei von Ramdisk gelesen
        #Textdatei wir jede Minute von LesePV.py erstellt 
        global GesEnergie
        global AktEnergie 
        global HeutEnergie
        Bytstart =[122,130,286,292]    #Adressen der Byts zum Ablegen der Daten
        KennNr = 0
        Zeile=4*[0]
        I=0 
        
        try:       
            Datei= open("/mnt/ramdisk/Aktsol.sol","r")
            for line in Datei: 
                Zeile[I]=line.rstrip()
                PVWerteSelektieren(I,Zeile[I],Bytstart[I])
                I=I+1
            Datei.close()
            
             #print("AlteEnergie: " + str(AktEnergie), " - NeueEnergie = " + str(Wert))
            #print (Byt[286:298])
             #Energiewerte nachts zurücksetzten auf Null
             #if Wert1 < HeutEnergie:
              #    GesEnergiePV1 == 0
              #    AktEnergie = 0
              #    HeutEnergie = 0
                      
             #if Wert > AktEnergie:
               #  KennNr=1
               # AktEnergie = Wert
             
             #elif Wert1 > HeutEnergie:
                 #KennNr=2
                 #HeutEnergie = Wert1
             
             #elif Wert2 > GesEnergiePV1:
                 #KennNr=3
                 #GesEnergiePV1 = Wert2 
             
             #if KennNr > 0 :
                    #Datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    #outstr=(str(KennNr) + "," + Datum + "," + str(AktEnergie) + "," +  str(HeutEnergie) + "," + str(GesEnergiePV1))
                    #PVDatenZuHeisopo(outstr)
                    #print (outstr)
             #else:
                    #print("Energie nicht groesser") 
                 
        except:
             print ("Fehler: Datei Aktsol.sol ist nicht vorhanden oder Daten nicht vorhanden",Zeile)

        #print (Byt[130:135])
        #print (Byt[286:297])
        # (GesEnergie)
            
                   
################# Unterprogramme ################################
def DatenInTextdatei(Datenstrom):
            #Daten weredn in Texdatei gespeichert und auf Ramdisk abgelegt
             Textdatei= open("/mnt/ramdisk/Daten.heis","w")
             #print ("Dat=" + str(Datenstrom))
             Zeitstempel = time.strftime("%d.%m.%Y %H:%M:%S") +"\n"
             Datenstrom = Zeitstempel +  str(Datenstrom)
             Textdatei.write(Datenstrom)
             Textdatei.close()
       
################# Unterprogramme ################################
def NeustartzuHeisopo(RechnerID):
    try:   
        url = "http://www.heisopo.de/Raspberry/Neustarts.php"
        payload ={'Value': RechnerID}
        r = requests.post(url, data=payload)
          #print (r.status_code)
        #Serverantwort="Neustart\n"+ r.text
         
        print (r.text)
    except:
        print ("Fehler: keine Internetverbindung")

#########################################################################     
def HandyLogzuHeisopo(GeraeteIP):

    global Byt
    outstr = GeraeteIP + ',' + str(datetime.now()) + ',' + str(Byt[159])
  
    try:
        url = "http://www.heisopo.de/Raspberry/HandyLogs.php"
        payload ={'Value': outstr}
        r = requests.post(url, data=payload)
  
        #print (payload)
        #print (r.status_code)
        #Serverantwort="Handy\n"+ r.text
         
        print (r.text)
    
        
    except:
        print ("Fehler: keine Internetverbindung (Handy)")

  
#########################################################################    
def DatenzumArduino():
        global Byt
        
        Anz = 200
        ToArd = (Anz+1)*[0] #200 Byt für Arduino vorbereiten
        ToArd[:161] = Byt[:161]   #160 Byt holen zum neuen Array   
        
        #Weitere Byts: 
        ToArd[162:164]  = Byt[286:288]  #Akt erzeugter Strom von PV2,Modul1
        ToArd[164:166]  = Byt[292:294]  #Akt erzeugter Strom von PV2,Modul2
        
        Pruef = 0
        for i in range(0,Anz):
            #print (i,"-",ToArd[i])
            if ToArd[i] < 0 or ToArd[i] > 255:#Testen auf falsche Werte
               ToArd[i] = 0 
            Pruef += ToArd[i]
        
        #try:
        LowByte = Pruef % 256
        ToArd[Anz]= LowByte
        Arduino.write(ToArd[:Anz+1])
        #print ("Sende : "+ str(ToArd[162:166]))
        
        #ToArd[159]= 0; #WLanbyt zurücksetzen
        #except:
        #print (Pruef,"-", LowByte)
        #print (Byt[:Anz+1])
#            for N in Byt:
#                if Byt[i] < 0 or Byt[i] > 255:
#                    print (i,Byt[i])
       
    
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
                    if AnzFrames == 9:  Index += 56
                    
                    Byt[Index] = Rohbyts[Startbyt + j]
                    #print(Index," ",FrameNr,Startbyt," ",j,Startbyt + j,Byt[Index] )
                  
         else: print (FrameNr,"Check Byts DeltaSol nicht OK",Startbyt,check)
                 
    #for i in range(0,10):
   # print (ValuByte)
   

###########################################################    
def ArduinoBytsAuswerten(i,Ard):
      #Daten vom RaspArduino
      
        global Byt
        global FromArd
        
        data = str(Ard)
        data1=data.split(",")
        #print (len(data1))
        del data1[0]  #erstes Element entfernen (ARD)
        del data1[len(data1)-1]  #letztes Element entfernen
        for n in range(0,len(data1)):
            FromArd[n]=int(data1[n])
        
        for j in range(0,170):
             Byt[j+160] = FromArd[j]
#             if (j> 85):
#                print (j+160,Byt[j])
       
#        for j in range(180,185):
#             print (j,Byt[j])
             
        #Neustartinfo von Kellerarduino und Dacharduino in Datenbank auf Server speichern
        if Byt[329] > 0:
            NeustartzuHeisopo(Byt[329])
            
    
################# Unterprogramme ################################
def NiveauszuHeisopo():
  #Programm diente zur Fehlersuche bei Niveau2'
    outstr=', '.join(str(x) for x in Byt[322:329])
    try:   
        url = "http://www.heisopo.de/Raspberry/Niveaufehler.php"
        payload ={'Werte': outstr}
        r = requests.post(url, data=payload)
  

        #print (r.status_code)
       # Serverantwort="Antwort\n"+ r.text
         
        print (r.text)
    
        
    except:
        print ("Fehler: keine Internetverbindung")

################# Unterprogramme ##########################################
def StromdateiLesen():
        #Die Daten für diese Datei werden vom ESP32Strom an Heisopi-Server geschickt.
        #zur Datei '/var/www/html/heisopo/RaspServer/EmpfangStrom.php
        #diese erzeugt die Datei "/mnt/ramdisk/Stromdaten.heis"
        
        fileStrom ="/mnt/ramdisk/Stromdaten.heis"
        try:
           Datei = open(fileStrom, "r")
           Inhalt = Datei.readline()
           Datei.close()
  
        except FileNotFoundError as e:
            print  ("Datei 'Stromdaten.heis' fehlt in Ramdisk")
         
        return Inhalt 

################################################################
def DatenvomESPStrom():
    global Byt
    global GesEnergiePV1
    global StromZeit

    #Diese Daten werden über UDP vom ESPStrom empfangen
    Datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  
    try:
        Inh = StromdateiLesen()
        #------------------------------------------------
        #Stromdaten des Hauptstromzaehlers verarbeiten
        Pos = Inh.find("Daten")
        Last = 0
        if Pos > -1:
            First = Inh.find("[",Pos)+1
            Last = Inh.find("]",First)
            ZS= Inh[First:Last] 
            #print(Pos,First,Last,x)
     
            Byts = ZS.split(",")  #Inhalt der Datei als Bytearray, Zeit wird abgeschnitten
            Byt[331:]= Byts[:12]
            #Byt[238:250]= Byts[12:24]  #Strommessung über Nebenzähler Heizung, Waschen, Buero, Pool
                    
            ZST= "00" + "-" + HauptZaehlerstandBerechnen(Byts,0) +"\n"          #Hauptzählerstand
            ZST= ZST + "01" + "-" + HauptZaehlerstandBerechnen(Byts,4) +"\n"    #Eingespeist
            ZST= ZST + "02" + "-" + str(GesEnergie[0]/10) +"\n"                 #Gesamt PV1
            #ZST= ZST + "02" + "-" + str(1024.3) +"\n"                 #Gesamt PV1
            ZST= ZST + "03" + "-" + str(GesEnergie[1]/10)+ "\n"                 #Gesamt PV2
            ZST= ZST + "04" + "-" + str(GesEnergie[2]/10)+ "\n"                 #Gesamt PV2, Modul1
            ZST= ZST + "05" + "-" + str(GesEnergie[3]/10) + "\n"                #Gesamt PV2, Modul2    
            
            Byt[128]= int(Byts[11]) #beide niederwertige Byts zum Senden an Dachrechner
            Byt[129]= int(Byts[10]) #das ist die aktuelle Leistung des Hauptstromzählers
            #print (Byt[128:130])        
            #Minute = datetime.now().minute
            #print ("Stunde=",Stunde,":",Minute)
            #if (Minute == 59):   #Stromdaten jede Stunde zu Heisopo, gilt nur für Datentabelle 'Stromdaten'
            StromDatenZuHeisopo(Datum + "," + ZS)
                        #print ("Datenzu Heisopo =:",Minute)
         #------------------------------------------------
                   
        #Stromdaten des Shelly verarbeiten
        Pos = Last
       
        while Inh.find("Shelly",Pos) > 0:
            Pos = Inh.find("Shelly",Pos)
        
            First = Inh.find("[",Pos)
            Last = Inh.find("]",First)
            Nr = int(Inh[Pos + 6:First])
            x= Inh[First+1:Last] 
            #print(Nr,Pos,First,Last,"Daten=",x)
 
            Byts = x.split(",")  #Inhalt der Datei als Bytearray, Zeit wird abgeschnitten

            SB = (Nr - 70) *3 + 238  
            EB = SB + 3
            #print ("Wahl = " ,Nr ,SB ,EB)
            Byt[SB:EB]= Byts[0:3]  
            
            Zaehler = str(Nr) +"-" + ZaehlerstandBerechnen (Byts[9:12]) + "\n"
            ZST = ZST + Zaehler
            #print("Shelly",Nr,Zaehler)
            Pos=Last
            
        StaendeInTextdatei(ZST)
        
         #Zaehlerstände alle 3 Minuten zu Heisopo
        if (time.time()- StromZeit) < 3*60: return  #Zaehlerstände alle 5 Minunten Speichern
        StromZeit = time.time()
        ZaehlerstaendeZuHeisopo(Datum + "," + ZST)
        print ("Sende Zählerstände zu Heisopo")
        #print ("Zaehlerstaende:\n"+ZST)   
            
    except:          
                print("keine Daten vom ESP-Strom")
                  
################################################################
def ZaehlerstandBerechnen(y):
            
            Stand = (int(y[0]) + int(y[1]) * 256 +int(y[2]) * 256 ** 2)/100000         
            Stand= format(round(Stand,3))    
            return Stand
################################################################
def HauptZaehlerstandBerechnen(y,S):
            
            Stand = (int(y[3+S]) + int(y[2+S]) * 256 +int(y[1+S]) * 256 ** 2 + int(y[0+S]) * 256 ** 3)/10000         
            Stand= format(round(Stand,3))
       
            return Stand    
               
########################################################################
def StaendeInTextdatei(Text):
            #Daten weredn in Texdatei gespeichert und auf Ramdisk abgelegt
             Textdatei= open("/mnt/ramdisk/Zaehlerstaende.heis","w")
             Textdatei.write(Text)
             Textdatei.close()

def DatenInTextdatei(Datenstrom):
            #Daten weredn in Texdatei gespeichert und auf Ramdisk abgelegt
             Textdatei= open("/mnt/ramdisk/Daten.heis","w")
             #print ("Dat=" + str(Datenstrom))
             Zeitstempel = time.strftime("%d.%m.%Y %H:%M:%S") +"\n"
             Datenstrom = Zeitstempel +  str(Datenstrom)
             Textdatei.write(Datenstrom)
             Textdatei.close()
       
################################################################
def InternetErreichbar():
        #Google anpingen (besteht Internetverbindung?
        global InternetOK
        #stellt fest, ob sich das Internet erreichbar ist
        status,result = sp.getstatusoutput("ping -c1 -w2 google.com")
       
        if status == 0:
            #print("Internet erreichbar")
            if InternetOK == True:
                print("Status geändert: Internet erreichbar")
            return True    
                #HandyImWLan = False
            #print("Handy ist im WLan!")
        else:
            #print("Internet nicht erreichbar")
            if HandyImWLan == False:
                print("Status geändert: Internet nicht erreichbar!")
            return False  
            #HandyImWLan = True

################################################################
def LichtWohnzimmer():
    global Byt
    global IPWohnzimmer
    
    #Einschalten des Wohnzimmerlichtes ab einer gewissen Lichtstärke
    
    #print ("Licht ein bei:", Byt[170]*10)
    
    if Byt[171] == 0 : return   #Lichtsteuerung ausgeschaltet
    
    LichtEin = Byt[170] * 10   #Sollwert, der vom Arduino kommt
    
    EinZeit = 16 * 60 + 5  #Licht frühestens ab 16:05 einschalten
    MaxAus  = 22 * 60 + 5  #nur bis 22:05 kontrollieren
   
    Licht = Byt[217]*256 + Byt[216]   #Lichtstaerke in Lux (Norden)
    AktZeit = Byt[31]*60+Byt[32]      #aktuelle Zeit
    Strom = (int(Byt[273])*256*256 + int(Byt[272])*256 + int(Byt[271]))/100
    
    #print ("Licht=",Licht)
    #print (StatuShellyWohnzimmer())
    #print (Byt[271],Byt[272],Byt[273])
    #print (Strom)
   
    if AktZeit >= EinZeit and AktZeit < MaxAus and Licht < LichtEin and Strom > 90:
            StatusLicht=StatuShellyWohnzimmer()
            if StatusLicht == "aus":
                print ("Licht wird eingeschaltet")
                # URL zum Einschalten des Relais (Relay 0 ist der erste Schalter)
                url = "http://"+IPWohnzimmer+"/relay/0?turn=on"
                response = requests.get(url)    #Licht einschalten
    
    
################################################################    
def StatuShellyWohnzimmer():
    global IPWohnzimmer
    
    # URL zur Abfrage des Relais-Status (relay 0 ist der erste Schalter)
    url = "http://"+IPWohnzimmer+"/relay/0"
    
    try:
    # Senden der HTTP GET-Anfrage an das Shelly-Gerät
        response = requests.get(url)    
        if response.status_code == 200:
            # JSON-Daten der Antwort extrahieren
            data = response.json()
            
            # Abfragen, ob der Shelly eingeschaltet ist
            if data.get('ison'):     
                return "ein"
            else:
                return "aus"
        else:
            print("Fehler: Ungültiger Status-Code {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print("Ein Fehler ist aufgetreten:" + e)
        return "Fehler"

################################################################
def Handy_im_WLan(IP):
        #Funktion stellt fest, ob sich das Handy (IP 192.168.178.23) im WLan befindet
        status,result = sp.getstatusoutput("ping -c1 -w2 " + IP)
        global HandyImWLan
        global Byt
        
        if status == 0:
            if HandyImWLan == True:
                print("Status geändert: Handy ist im WLan!")
                Byt[159] = 1
                HandyLogzuHeisopo(IP) 
            HandyImWLan = False
            #print("Handy ist im WLan!")
        else:
            if HandyImWLan == False:
                print("Status geändert: Handy ist Nicht im WLan!")
                Byt[159] = 2
                HandyLogzuHeisopo(IP) 
            HandyImWLan = True
            #print("Handy NICHT im WLan!")
            
         

################################################################
def RaspZeitHolen():
    global Byt
    
    Jetzt =  datetime.now()
    Byt[28] = Jetzt.year-2000
    Byt[29] = Jetzt.month
    Byt[30] = Jetzt.day 
    Byt[31] = Jetzt.hour
    Byt[32] = Jetzt.minute
    Byt[33] = Jetzt.second
    #print (Byt[28:33])
################################################################
########################------------ Hauptprogramm -----------------------###############
#################################################################Verbindung zur Datenbank öffnen
#DB = MySQLdb.connect(host="localhost",db="Hausrechner",user="root", passwd="tester")
#curs = DB.cursor()
#INIT()

#Serielle Schnittstellen öffnen
if SerOK[0]:
    DeltaSol = serial.Serial(USBDeltaSol, 9600, timeout= 10)
    DeltaSol.isOpen()

if SerOK[1]:
    SunGo = serial.Serial(USBSunGo, 9600, timeout= 10)
    SunGo.isOpen()
 
if SerOK[2]:
    Arduino =serial.Serial(USBArduino, 19200, timeout= 30)
    Arduino.isOpen()


sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
 
Tknx=20   #Sendepause, nur alle 30 sec KNX-Gruppen lesen   
KNXZeit = time.time() - Tknx

NeustartzuHeisopo(1)  #Parameter 1 = Raspberry Pi

if Path(fileGas).exists():#Existiert Datei "Gasdaten
    LetzteDateiGasAenderung = os.path.getmtime(fileGas)


try:  
    while True:
        #if InternetErreichbar():
            #Handy_im_WLan("192.168.178.23")  #Ist Handy im WLan?
      
        ###########-Lese KNX-Gruppenadresse ###########
        LED_schalten()
      
        try:
            if (time.time()- KNXZeit) > Tknx:
                KNXZeit = time.time()
                #GPIO_schalten(11)
                KNXZa += 1
                loop = asyncio.get_event_loop()
                loop.run_until_complete(LeseAdresse())
              
              
        except:          
                print("keine Daten vom KNX-Bus")
                break   
                
###########-Lese DeltaSol ######################  
        LED_schalten()
        while readUSB == 1:
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
                        break
                        
            except:
                  Ausg = "keine Daten von DeltaSol"
                  #label.config(text= Ausg)
                  print(Ausg)
                  break
                  
        readUSB = 2
        #GPIO_schalten(16) 
###########-Lese SunGo- Auf dem Dachboden #############
        LED_schalten()
        while readUSB == 2:        
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
            #GPIO_schalten(18)
            try:
                Ard = Arduino.readline()
                
                if len(Ard)== 0: #Keine Daten-> Fehler erzeugen
                     raise
                
                for i in range(0,len(Ard)):
                    #Suche nach 'ARD'
                    if Ard[i]==65 and Ard[i+1]==82 and Ard[i+2]==68:
                        ArduinoBytsAuswerten(i,Ard)
                        Arduino.flushInput()
                        AnzArduino +=1
                        readUSB = 1
            except:
                  print("keine Daten von Arduino")
                  readUSB = 1
                  
                
#######################################################       
        #GPIO_schalten(0)  #Alle LED aus
        if (AnzDelta + AnzSunGo) > 1:

            print(time.strftime("%d.%m.%Y %H:%M:%S"),"DeltaSol:", AnzDelta,"SunGo:",AnzSunGo,"Arduino:",AnzArduino, "KNX:",KNXZa,"Vom Arduino:",len(Ard))
            #Zeitlabel.config(text=time.strftime("%d.%m.%Y %H:%M:%S"))
            #if Path(fileGas).exists():
            #Gasdaten()
               
            RaspZeitHolen()
            LeseDatenVomSolarserver()
            DatenvomESPStrom()
            LichtWohnzimmer()
            #print (Byt[130:132],Byt[130]+256*Byt[131])
            DatenzuHeisopo()
            DatenzumPC()
            #DatenzumESP32()
            if SerOK[2]: DatenzumArduino() #nur wenn Verbindung vorhanden ist
            #print (Byt[130:132])     #Uhrzeit des Raspberr
       # root.mainloop()    
            
##        
##        key = inkey()
##        if key in ['w','a','s','d']:
##            print (key)
##        if key == 'q':
##            exit()
            
            
except KeyboardInterrupt:
        print ("Verbindung geschlossen")
        #GPIO.output(16, 0)
        #GPIO.output(18, 0)
        #GPIO.cleanup()
        loop.close() 
        DeltaSol.close()
        SunGo.close()
        Arduino.close()

