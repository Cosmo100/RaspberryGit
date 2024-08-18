import time
import os
from datetime import datetime

 
fileStrom ="/mnt/ramdisk/Stromdaten.heis"
LetzteDateiAenderung = os.path.getmtime(fileStrom)
################## Unterprogramme ##########################################
def StromdateiLesen():
        
        global Inhalt
    
        try:
           Datei = open(fileStrom, "r")
           Inhalt = Datei.readline()
           Datei.close()
  
        except FileNotFoundError as e:
            print  ("Datei 'Stromdaten.heis' fehlt in Ramdisk")


##################Hauptprogramm ##########################################
        

print ("Programm startet um : " + time.strftime("%d.%m.%Y %H:%M:%S")) 

while True:
    if (LetzteDateiAenderung != os.path.getmtime(fileStrom)):
         #try:
                    Zeitstempel = time.strftime("%d.%m.%Y %H:%M:%S")
            
                    print ("Strommessung vom "+ Zeitstempel)
                    StromdateiLesen()
                    
                    LetzteDateiAenderung = os.path.getmtime(fileStrom)
                    #print (NeueZeit + NeueImpulse + NeuerStand)
                   
                    #print (Inhalt)
                    
                    x= Inhalt[22:-2]  #Inhalt der Datei als Bytearray, Zeit wird abgeschnitten
                    Byts = x.split(",")  #Inhalt der Datei als Bytearray, Zeit wird abgeschnitten
                    print (Byts)
                    By=[]
                    for Elem in Byts:
                        Wert = bytes(Elem,'utf-8')
                        By.append(Wert)
                        
                   
                    print (By)        
                    #print(x[1:5])
                    Wert=float(By[0]*256 *256 *256)
                    #Byts[3] = (Wert) & 0xff
                    #Byts[2] = (Wert>>8) & 0xff
                    #Byts[1] = (Wert>>16) & 0xff
                    #Byts[0] = (Wert>>24) & 0xff
                    
                    print (Wert)
                      
                 
         #except:          
                 #print("Keine Datei zum Lesen")
