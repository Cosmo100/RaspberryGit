#Dies ist kein Phyton-Programm, sondern eine Anleitung, wie Git-hub benutzt wird



Dokumentation unter https://docs.github.com/de

Beispiel am Raspberry:
    Öffne mit Power Shell Admin den Zufriff auf Raspberry:
    ssh root@heisopi
    password: tester10
    
    wir starten im Pfad /root
    wechsele in Pfad "Schreibtisch":
    cd Schreibtisch
    
    git add *.py
    git push --set-upstream origin main
    Meldung: Enter passphrase for key '/root/.ssh/id_ed25519':
    Eingabe Passwort: tester10
    
    oder nach einer Änderung:
     git status
     git add *.py
     git commit -m "Noch eine Änderung"
     git push
     Meldung: Enter passphrase for key '/root/.ssh/id_ed25519':
     Eingabe Passwort: tester10
     
    
    

Die wichtigsten Befehle:

https://www.devguide.at/git/wichtigsten-befehle-fuer-ein-lokales-repository/

git Status: Zeigt die geänderten Dateien
