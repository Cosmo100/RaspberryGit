#Dies ist kein Phyton-Programm, sondern eine Anleitung, wie Git-hub benutzt wird


Dokumentation unter https://docs.github.com/de

Beispiel am Raspberry:
    Öffne mit Power Shell Admin den Zufriff auf Raspberry:
    ssh root@heisopi
    password: tester10
    
    wir starten im Pfad /root
    wechsele in Pfad "Schreibtisch"
    cd Schreibtisch
   
    git add *.py
    git push --set-upstream origin main
    Meldung: Enter passphrase for key '/root/.ssh/id_ed25519':
    Eingabe Passwort: tester10
    
    oder:
     git commit -m "Noch eine Änderung"
     git push
     Meldung: Enter passphrase for key '/root/.ssh/id_ed25519':
     Eingabe Passwort: tester10
    
    
    Pfad root/Schreibtisch komplett auf Git Hub:
