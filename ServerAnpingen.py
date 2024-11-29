import subprocess

urlPV1 = "192.168.178.49"
urlPV2 = "192.168.178.37"

def PVServeranpingen(url):
	# Ping-Befehl ausführen
	try:
		output = subprocess.check_output(["ping", "-c", "1", url], universal_newlines=True)
		print("Antwort erhalten von {0}:\n{1}".format(url, output))
	except subprocess.CalledProcessError:
		print("Keine Antwort von {0}".format(url))


PVServeranpingen(urlPV1)
PVServeranpingen(urlPV2)
