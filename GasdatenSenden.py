from datetime import datetime
import requests

# Gegebener Zeitstring
Zeitpunkt = "2024-12-17T15:58:58+0100"
Zaehlerstand = 8444.256

# Daten, die gesendet werden sollen
payload = {
    'Zeitpunkt': Zeitpunkt,  # Key 'datum' für das Datum
    'Zaehlerstand':Zaehlerstand
}

url = "http://www.heisopo.de/Raspberry/EmpfangGasdaten.php"

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
