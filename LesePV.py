#LesePV.py liest die Router der PV-Anlagen aus und speichert diese
#in Ramdisk in Datei 'PV.sol'
#Es werden 3 Zeilen geschrieben:
#Zeile 1: Dateidatum und Daten der PV-Anlage 1
#Zeile 2: Daten der PV-Anlage 2, Modul1 (östlich)
#Zeile 3: Daten der PV-Anlage 2, Modul2 (westlich)
#diese Datei wird von Homerechner.py gelesen
#und dann an Heisopo übertragen

import requests
import datetime
import json
from requests.auth import HTTPBasicAuth


url = "http://192.168.178.49"
url1 = "http://192.168.178.49/status.html"          #Anlage1
url2 ="http://192.168.178.53:8050/getOutputData"    #Anlage2

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
    #print("Aktuelle Leistung:",Wert[0],"Watt")
    #print("heute produzierte Energie:",float(Wert[1])*1000,"Wh")
    #print("insgesamt produzierte Leistung:",Wert[2],"kWh")

    
    #Daten in eine Datein schreibe
    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Öffnen der Datei im Schreibmodus und Schreiben der Daten
    #PV.sol sammelt alle Daten, Aktsol.sol nur die aktuellen Daten
    
   
except:
    print("Login-in in PV-Server hat nicht funktioniert. Antwortcode: ",Antwcode)
    Login()
   
   
   
####### Anfrage an Anlage 2 ######################### 
print ("Anfrage an Anlage 2")

try:
    # Senden der GET-Anfrage
    response = requests.get(url2)

    # Überprüfen, ob die Anfrage erfolgreich war (Statuscode 200)
    if response.status_code == 200:
        # Auswerten der Antwort (z. B. JSON-Format)
        daten = response.json()  # Wenn die Antwort im JSON-Format vorliegt
        data = daten.get('data')
        #print("Antwortdaten:", data)

        Modul1=3*[0]
        Modul2=3*[0]
        Modul1[0]=str(data['p1'])
        Modul2[0]=str(data['p2'])
        Modul1[1]=str(data['e1'])
        Modul2[1]=str(data['e2'])
        Modul1[2]=str(data['te1'])
        Modul2[2]=str(data['te2'])
        
        print (Modul1)
        print (Modul2)
      
    else:
        print("Fehler: HTTP", response.status_code, "-", response.reason)

except requests.exceptions.RequestException as e:
    print("Ein Fehler ist aufgetreten:", e)
    

#Alle Daten in  Datei schreiben
with open("/mnt/ramdisk/Aktsol.sol", "w") as file:
        file.write(date_string + ": " + str(Wert[:3]) + "\n" + str(Modul1)+ "\n" + str(Modul2))
