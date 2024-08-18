import time
import os
from datetime import datetime

 
filename ="/mnt/ramdisk/Gasdaten.heis"
LetzteDateiAenderung = os.path.getmtime(filename)
################## Unterprogramme ##########################################
def GasdateiLesen():
        #global LetzteZeit,LetzteImpulse,LetzterStand
        global NeueZeit, NeueImpulse, NeuerStand
    
        try:
           Datei = open(filename, "r")
           NeueZeit = Datei.readline()
           NeueImpulse = Datei.readline()
           NeuerStand = Datei.readline()
           
           Datei.close()
  
        except FileNotFoundError as e:
            print  ("Datei 'Gasdaten.heis' fehlt in Ramdisk")


##################Hauptprogramm ##########################################
global AlterStand, AlteImpulse,AlteZeit            

print ("Programm startet um : " + time.strftime("%d.%m.%Y %H:%M:%S")) 

while True:
    if (LetzteDateiAenderung != os.path.getmtime(filename)):
         try:
           
                    Zeitstempel = time.strftime("%d.%m.%Y %H:%M:%S")
            
                    print ("Gasmessung vom "+Zeitstempel)
                    GasdateiLesen()
                    
                    LetzteDateiAenderung = os.path.getmtime(filename)
                    #print (NeueZeit + NeueImpulse + NeuerStand)
                    
                    #beim ersten Start 
                    if 'AlterStand' not in locals():
                        AlteZeit = NeueZeit
                        AlteImpulse = NeueImpulse
                        AlterStand = NeuerStand
                        
                                   
                    #Berechnung der Zeitdifferenz zwischen den Impulsen
                    NT = datetime.strptime(NeueZeit[:-2], "%Y-%m-%dT%H:%M:%S")
                    AT = datetime.strptime(AlteZeit[:-2], "%Y-%m-%dT%H:%M:%S")
                    Zeitdiff = (NT-AT).total_seconds()
                    
                    #Anzahl der vergangenen Impulse
                    Impulsdiff = int(NeueImpulse[:-1]) - int(AlteImpulse)
                    NeuerStand = float(NeuerStand[:-1]) + Impulsdiff * 0.01
                    if (Zeitdiff > 0):
                        VolStrom = 600/ Zeitdiff;
                   
                        print ("Zeitdiff: " + str(Zeitdiff) + " sec")
                        print ("Impulsdiff: " + str(Impulsdiff) + " Impulse")
                        print ("Zaehler: " + str(round(NeuerStand,2)) + " m³")
                        print ("VolStrom: " + str(round(VolStrom,2)) + " l/min")
                      
                        print()
                       
                                
                    AlteZeit = NeueZeit
                    AlteImpulse = NeueImpulse
                    AlterStand = NeuerStand
                    
                           except:          
             print("Keine Datei zum Lesen")
