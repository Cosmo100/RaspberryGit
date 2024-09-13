
#Testsript zum Lesen der PV Daten aus LesePV.py

Byt=350*[0]         #Daten, die zu heisopo und über UDP zum PC gesendet werden
################# Unterprogramme ################################        
def LeseDatenVomSolarserver():
        #Daten werden aus Textdatei von Ramdisk gelesen
        #Textdatei wir alle 4 min von LesePV.py erstellt 
             global GesEnergie
             global AktEnergie 
             global HeutEnergie
             Bytstart =[122,286,292]
             KennNr = 0
             Zeile=3*[0]
             I=0   
             Datei= open("/mnt/ramdisk/Aktsol.sol","r")
             for line in Datei: 
                Zeile[I]=line.rstrip()
                PVWerteSelektieren(Zeile[I],Bytstart[I])
                I=I+1
   

               
#################################################################
def PVWerteSelektieren(PVZeile,BS):
            #Macht aus der Datenzeile des Wechselrichters einzelne Werte
            
             posStart = PVZeile.find("[")+1
             posEnde = PVZeile.find("]")

             PVText= PVZeile[posStart:posEnde]
             PVText = PVText.replace("'","")
             print ("PV-Daten=" + PVText)
             PVText = PVText.split(", ")
             
             #Aktuell erzeugte Leistung    
             Wert = int(PVText[0])
             Byt[BS] = (Wert) & 0xff
             Byt[BS+1] = (Wert>>8) & 0xff
             
             #An diesem Tag erzeute Leistung
             Wert1 = int(float(PVText[1]) *1000)
             Byt[BS+2] = (Wert1) & 0xff
             Byt[BS+3] = (Wert1>>8) & 0xff
             
             #bisher erzeugte Gesamtleistung
             Wert2 = int(float(PVText[2])*100)
             Byt[BS+4] = (Wert2) & 0xff
             Byt[BS+5] = (Wert2>>8) & 0xff

             print (Wert,Wert1,Wert2)
            


##############################################################################
print ("Programmstart")

LeseDatenVomSolarserver()
