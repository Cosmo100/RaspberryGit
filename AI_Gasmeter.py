
#Gasmeter mit API-URL abfragen,
#Json Paket zerlegen 
#Überprüfen, ob Wert gültig ist (no error)
#wenn ja -> Speichern als Text in Datei in AI_onTheEdge.heis

#Datei wird später von "Homrechner.py" gelesen und zu Heisopo.de geschickt
#script wird alle 5 Minuten vom Raspberry als cronjob ausgeführt (crontab -e)

import requests
import json
from requests.auth import HTTPBasicAuth
import re		#Reguläre Ausdrücke
from datetime import datetime
import os
filename ="/mnt/ramdisk/AI_onTheEdge.heis"

APIURL = "http://192.168.178.57/json"
######################### Subroutinen ############################
def GasdatenZuHeisopo(Zeitpunkt, Zaehlerstand):
	
	url = "http://www.heisopo.de/Raspberry/EmpfangGasdaten.php"
	
		# Daten, die gesendet werden sollen
	payload = {
	'Tabelle':"Gas",
    'Zeitpunkt': Zeitpunkt,  # Key 'datum' für das Datum
    'Zaehlerstand':Zaehlerstand}
		

	# HTTP POST senden
	try:
		response = requests.post(url, data=payload)
		if response.status_code == 200:
			print("Erfolgreich gesendet!")
			print("Antwort des Servers:", response.text)
		else:
			print("Fehler beim Senden. Statuscode:", response.status_code)
	except Exception as e:
		print("Fehler beim Senden der Anfrage:", e)

#########################################################################

def JsonTextZerlegen(Daten):
	
	Dat =json.loads(Daten)
	Fehler = Dat["main"]["error"]
	
	
	if (Fehler == "no error"):
		Zaehlerstand = Dat["main"]["value"]
		Zeitpunkt = Dat["main"]["timestamp"]
		print(Zaehlerstand)
		with open(filename, "w",) as file:
			file.write(Zaehlerstand)
			file.writelines(" um " + Zeitpunkt)
			print ("Datei "+ filename + " geschrieben - kein Fehler")
			GasdatenZuHeisopo(Zeitpunkt, Zaehlerstand)
	else:		
		print ("Fehler:"+Fehler)

#########################  Hauptprogramm ##########################
try:
	response = requests.get(APIURL)  #Anfrage an Gas-ESP

	if (response.status_code == 200):
		print (response.text)
		JsonTextZerlegen(response.text)
		
	else:
		print ("Fehlermeldung von Shelly-Cloud "+ response.status_code)
		
except Exception as err:
    print("Ein unerwarteter Fehler ist aufgetreten: ")
    

#Prüfe, ob Datei existiert, wenn nicht ->Dummy anlegen
if not os.path.exists(filename):
	print("Die Datei existiert nicht -wird angelegt")
	with open(filename, "w",) as file:
		file.write("8000.000")
