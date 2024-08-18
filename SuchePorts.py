#Identifikation von seriellen Schnittstellen

import serial
import time

Pfad = '/dev/tty'

Moegliche = ["ACM0","ACM1","ACM2","ACM3","S0","USB0","AMA0"]
Schnittstellen=[]
Ser=[]
Geraet=["DeltaSol","SunGo","Arduino"]

##################### Unterprogramm #########################  
def Wert():
    ABC = 100
    return ABC


def TesteVBus(Schnittstelle,Frames):
    Anz = 200
    Testbyts = Anz*[0]   #array mit 180 leeren Elementen
    TZa = 0
    Durchlauf = 0
    #print (Schnittstelle)
    try:
        Testserial = serial.Serial(Schnittstelle, 9600, timeout= 5)
        Testserial.isOpen()
    except:
        print ("Timeout")
        return False
        
    while Durchlauf < Anz:
        DS = Testserial.read()
        if len(DS) > 0:
            if DS[0] == 170:
                TZa = 0
                #print ("Sync-Byte gefunden")
            Testbyts[TZa]=DS[0]
            TZa += 1
            #print(Durchlauf,TZa,DS[0])       
            
            if Testbyts[1]==16 and Testbyts[2] == 0:
                if Testbyts[8]==Frames:
                    return True
        else:
              return False
        Durchlauf += 1           
    return False
############################################################### 
def SucheVBusPort():
    global Geraet
    Frames=[17,10]
    for n in range (0,2):
        #Suche Schnittstelle für DeltaSol
        for Schnittstelle in Schnittstellen:
            Test = Pfad + Schnittstelle
            print ("Teste : ",Schnittstelle + " für " + Geraet[n])
            Erg = TesteVBus(Test,Frames[n])
            if Erg:
                print ("Schnittstelle für " + Geraet[n] +" gefunden",Schnittstelle)
                Ser.append(Schnittstelle)
                Schnittstellen.remove(Schnittstelle)
                break
            
        if not Erg:
            print ("keine Schnittstelle für " + Geraet[n] +" gefunden!")
            Ser.append("KEINE")

############################################################### 
def TesteArduino(Schnittstelle):
    global AktZeit
    Anz = 200
    Testbyts = Anz*[0]   #array mit 180 leeren Elementen
    TZa = 0
    Durchlauf = 0
    #print (Schnittstelle)
    try:
        Testserial = serial.Serial(Schnittstelle, 57600, timeout= 10)
        Testserial.isOpen()
    except:
        print ("Timeout")
        return False
    n=0   
    #while Durchlauf < 2:
    
    while n < Anz:
        try:
            DS = Testserial.read()
            if (time.time()- AktZeit) > 20:
                print ("Zeit abgelaufen")
                return False
            if len(DS) > 0:
                Testbyts[TZa]=DS[0]
                TZa += 1
            n +=1
            #print(n)
        except:
            print ("Keine Verbindung")
            return False   
    #print(Testbyts)    
    for z in range(0,Anz-2):
        #Suche nach "ARD"
         if Testbyts[z]==65 and Testbyts[z+1]==82 and Testbyts[z+2]==68:
            #print ("gefunden")
            return True
    
    return False
#############################################################  
#Arduino Schnittstelle suchen
def SucheArduinoPort():
    global AktZeit
    
    for Schnittstelle in Schnittstellen:
                Test = Pfad + Schnittstelle
                print ("Teste : ",Schnittstelle + " für Arduino")
                AktZeit = time.time()
                Erg = TesteArduino(Test)    
                if Erg:
                    print ("Schnittstelle für Arduino gefunden",Schnittstelle)
                    Ser.append(Schnittstelle)
                    Schnittstellen.remove(Schnittstelle)
                    break
                
    if not Erg:
        print ("keine Schnittstelle für Arduino gefunden!")
        Ser.append("KEINE")

##################### Hauptprogramm #########################                 
    #Suche alle existierenden Schnittstellen
def SerielleSchnittstellen():        
    for Schnittstelle in Moegliche:
        Test = Pfad + Schnittstelle
        try:
            Probe = serial.Serial(Test, 9600, timeout= 5)
            #print (Test)
            Probe.isOpen()
            Schnittstellen.append(Schnittstelle)
            Probe.close()
            
        except:
                 #Schnittstellen.remove(Schnittstelle)
                 #print (Test + " existiert nicht")
            print()

    print ("Alle existierenden seriellen Schnittstellen:",Schnittstellen)

    #Schnittstellen suchen für DeltaSol und SunGo
    SucheVBusPort()
    SucheArduinoPort()

    print ()
    print ("Ergebnis:")
    print ("belegte seriellen Schnittstellen:")
    for i in range(0,3):
        print (Geraet[i]+" : ", Ser[i])


    print ()
    print ("nicht benutzt:")
    print (Schnittstellen)
    return Ser


Ser = SerielleSchnittstellen()