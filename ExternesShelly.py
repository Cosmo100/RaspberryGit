
#Externes Shelly mit API-URL abfragen,
#Json Paket zerlegen und in Datenbank auf Heisopo-Datenbank speichern
#script wird jede viertelstande vom Raspberry als cronjob ausgeführt (crontab -e)

import requests
from requests.auth import HTTPBasicAuth
import re		#Reguläre Ausdrücke
from datetime import datetime

APIURL = "https://shelly-146-eu.shelly.cloud/device/status/?Content-Type=application/x-www-form-urlencoded&id=10061cd282f8&auth_key=MWUyNGVidWlk7E63EDECAE18383DBD89F610A3FEC8D80A2176772344C47993DAABAAF5A63751FC465FE14AF5341F"
HeisopoURL = "http://www.heisopo.de/Raspberry/EingangExtShelly.php"
Debug = False

######################### Subroutinen ############################
def JsonTextZerlegen(Daten):
	
	Online = WertSelektieren(Daten, "online", False)
	if (Debug): print ("Online=" + Online )

	Zustand = WertSelektieren(Daten, "output", False)
	if (Debug): print ("Zustand=" + Zustand )
	
	Zeit = WertSelektieren(Daten, "ts")
	datum_zeit = datetime.fromtimestamp(Zeit).strftime("%d.%m.%Y %H:%M")
	if (Debug): print ("Zeit:",datum_zeit)
	
	Spannung = WertSelektieren(Daten, "voltage")
	SpannungF = "{:.1f} V".format(Spannung)
	if (Debug): print ("Spannung="+Spannung)
	
	Strom = WertSelektieren(Daten, "current")
	StromF = "{:.2f} A".format(Strom)
	if (Debug): print ("Strom="+Strom)
	
	Leistung = WertSelektieren(Daten, "apower")
	LeistungF = "{:.2f} W".format(Leistung)
	if (Debug): print ("Leistung="+Leistung)
	
	Zaehlerstand = WertSelektieren(Daten, "total")/1000
	ZaehlerstandF = "{:.3f} kWh".format(Zaehlerstand)
	if (Debug): print ("Zaehlerstand=" + Zaehlerstand)
	 
	Temperatur = WertSelektieren(Daten, "tC")
	TemperaturF = "{:.1f} °C".format(Temperatur)
	if (Debug): print ("Temperatur=" + Temperatur)
	
	#Zaehlerstand = 13.95		#Dummy Daten
	#datum_zeit = datetime(2024, 12, 2, 12, 33, 0)		0
	
	data = {
    "Online": Online,
    "Zustand": Zustand,
    "Zeit": datum_zeit,
    "Spannung": Spannung,
    "Strom": Strom,
    "Leistung": Leistung,
    "Zaehlerstand": Zaehlerstand,
    "Temperatur": Temperatur
	}

	
	DatenzuHeisopo(data)

	 
##################################################################

def DatenzuHeisopo(Daten):

	global AktZeit
	global HeisopoURL
    
	Theisopo=5   #Sendepause, nur alle 20 sec zum Server senden
	try:   
		#if (time.time()- AktZeit) < Theisopo: return
		#AktZeit = time.time()
		
		r = requests.post(HeisopoURL, data=Daten)
		print (r.status_code)
		Serverantwort="Antwort von Heisopo: \n"+ r.text
		print (Serverantwort)
        
	except:
		print (r.status_code + " - Fehler vom Heisopo-Server!")
		

##################################################################
def WertSelektieren(Daten,Wert,Zahl=True):
	 
		Laenge = len(Wert)
		Pos = Daten.find(Wert)+Laenge+2
		EndPos = Daten.find(",", Pos)

		Erg = Daten[Pos:EndPos]
		#print(Erg)
		
		if(not Zahl): return Erg

		Val =  re.sub(r"[^0-9.:]", "", Erg)

		return float(Val)


######################### Hauptprogrammm ######################################

response = requests.get(APIURL)  #Anfrage an Shelly

if (response.status_code == 200):
	#print (response.text)
	JsonTextZerlegen(response.text)
	
else:
	print ("Fehlermeldung von Shelly-Cloud "+ response.status_code)
