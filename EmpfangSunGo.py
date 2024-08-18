#Datenauswertung für DeltaSol BX Plus
#Schnittstelle Datenempfang vom VBus
#https://forum-raspberrypi.de/forum/thread/35528-daten-an-webserver-uebertragen/#

import serial
import MySQLdb
import time
import requests

ValuByte=[]
Byts=[] 
Za = 0
 ################# Unterprogramme ################################
def DateninDatenbank():
    
    Spalten= "(Temperatur1,Temperatur2,Temperatur3,Temperatur4)"
    Values = ' VALUES (%d,%d,%d,%d);' % (Wert(0),Wert(2),Wert(4),Wert(6))
     
    SQL_Befehl = "INSERT INTO messdaten " + Spalten + Values 
    curs.execute (SQL_Befehl)
    DB.commit()
    
   
################# Unterprogramme ################################
def DatenzuHeisopo():
 
    outstr=', '.join(str(x) for x in ValuByte)
    url = "http://www.heisopo.de/Raspberry/EingangRaspberry.php"
    payload ={'Value': outstr}
    r = requests.post(url, data=payload)

    print (r.text)
    #print (r.url)
################# Unterprogramme ################################
def DatenzumServer():
    url = "http://heisopi/Heizung/DeltaSolDaten.php"
    r = requests.post(url)
    print (r)
###########################################################    
def BytsDarstellen():
    for FrameNr in range(1,11):
         Startbyt = FrameNr * 6 + 4
         St= (FrameNr-1) * 4
         check = 0
         #print (Startbyt+6)
         for j in range(Startbyt,Startbyt+6):
                        check = check+Byts[j]
         
         #print (FrameNr,check,Byts[Startbyt + 6])               
         if (check | 128) & 255 == 255:            #Cheksumme OK!
                #MSB setzen
                MSB = Byts[Startbyt + 4]
                #print (FrameNr,"Check OK",Startbyt)
                for j in range(0,4):
                    if (MSB & (1<<j)) > 0:
                        Byts[Startbyt + j] = Byts[Startbyt + j] | 128
                    ValuByte.append (Byts[Startbyt + j])
         else: print (FrameNr,"Check nicht OK",Startbyt,check)
                 
    #for i in range(0,10)
         if len (ValuByte) == 40:
             print (ValuByte,len (ValuByte))

##    print ("Temperatur 1 =",Wert(0))
##    print ("Temperatur 2 =",Wert(2))
##    print ("Temperatur 3 =",Wert(4))
##    print ("Temperatur 4 =",Wert(6))
##    print ("Temperatur 5 =",Wert(8)) 
##    print ("Temperatur 6 =",Wert(10))
##    print ("Temperatur 7 =",Wert(12))
##    print ("Temperatur 8 =",Wert(14))
##    print ("Temperatur 9 =",Wert(16))
##    
##    print ("Relais 1 =",Wert(40,1)) 
##    print ("Relais 2 =",Wert(41,1))
##    print ("Relais 3 =",Wert(42,1))
##    print ("Relais 4 =",Wert(43,1))
##    print ("Relais 5 =",Wert(44,1))
    
    #print ("Zeit =",Wert(48,4)) 
    print(time.strftime("%d.%m.%Y %H:%M:%S"))
    
   
################# Unterprogramme ################################
def Wert(ByteNr,N=2):
    Erg=0
    for i in range(0,N):
            Erg = Erg + ValuByte[ByteNr+i] * 256**i
            
    return Erg
    


############### Hauptprogramm ##################################

for x in range(113):  #array mit 112 leeren Elementen
   Byts.append(0)

#Verbindung zur Datenbank öffnen
#DB = MySQLdb.connect(host="localhost",db="Hausrechner",user="root", passwd="tester")
#curs = DB.cursor()

DeltaSol = serial.Serial('/dev/ttyACM1', 9600) # Namen ggf. anpassen
DeltaSol.isOpen()
#time.sleep(5) # der Arduino+w resettet nach einer Seriellen Verbindung, daher muss kurz gewartet werden
 

try:
    while True:
        By = DeltaSol.read()
      
        if By[0] == 170:
            Za = 0
            #print ("Sync-Byte gefunden")
        Byts[Za]=By[0]
        Za += 1
        #print(Za,By[0])       
            
        if Za == 70 and Byts[1]==16 and Byts[2] == 0:
            if Byts[8]==10:
                print ("Empfang von Delta Sol")
                BytsDarstellen()
                #DatenzuHeisopo()
                del ValuByte[:]
       # print(Za,By)
        
except KeyboardInterrupt:
       DeltaSol.close()


