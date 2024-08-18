#Script liest den Router der PV-Anlage aus und speichert diese
#in Ramdisk in Datei 'PV.sol'
#diese Datei wird von Hemerechner.py gelesen

import requests
import datetime
from requests.auth import HTTPBasicAuth


url = "http://192.168.178.49"
url1 = "http://192.168.178.49/status.html"

def Login():
    print("erste Anfrage")
    r = requests.post(url)
    
    if r.status_code == 401:    
        response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))
        print ("Erfolg")
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 

Login()
# senden einer GET-Anfrage an die URL
response = requests.get(url1)
Antwcode = response.status_code
# Überprüfen ob die Anfrage erfolgreich war
if Antwcode == 200:
    # Zugreifen auf den HTML-Inhalt der Seite
    text = str(response.content)

    # Ausgabe des HTML-Inhalts
    #print(text)
 
Start = "var webdata_now_p" #Ab diesem Text wird selektiert
Ende = "var webdata_utime"    #bis zu diesem Text wird selektiert

try:

    posStart = text.find(Start)
    posEnde = text.find(Ende)

    Auswahl = text[posStart:posEnde]
#print (Auswahl)

    I=0
    Wert=5*[0]
    while len(Auswahl) > 40:
         startIndex = Auswahl.find(chr(34))
         endIndex = Auswahl.find(chr(34), startIndex + 1)
     
         Wert[I] = Auswahl[startIndex + 1: endIndex]
         Auswahl = Auswahl[endIndex+5:]
         I+=1
     
    print (Wert[:3])
    print("Aktuelle Leistung:",Wert[0],"Watt")
    print("heute produzierte Energie:",float(Wert[1])*1000,"Wh")
    print("insgesamt produzierte Leistung:",Wert[2],"kWh")

    
    #Daten in eine Datein schreibe
    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Öffnen der Datei im Schreibmodus und Schreiben der Daten
    #PV.sol sammelt alle Daten, Aktsol.sol nur die aktuellen Daten
    #with open("/mnt/ramdisk/PV.sol", "a") as file:
        #file.write(date_string + ": " + str(Wert[:3]) + "\n")
       
    with open("/mnt/ramdisk/Aktsol.sol", "w") as file:
        file.write(date_string + ": " + str(Wert[:3]) + "\n")

except:
    print("Login-in in PV-Server hat nicht funktioniert. Antwortcode: ",Antwcode)
    Login()
     