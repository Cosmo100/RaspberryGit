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


Wichtig:
Unterscheide zwischen den Protokollen:

for https protocol (Windows)
git remote set-url origin https://github.com/Cosmo100/repository.git

for ssh protocol (Raspberry)
git remote set-url origin git@github.com:Cosmo100/repository.git


'#####################################################################################'
mit Power Shell in Windows: Start in diesem Pfad : C:\Windows\system32> 
ins Hauptverzeichnis:cd.. nochmal cd ..

Beispiel an Arduino:
Wechsel in das gewünschte Git-Verzeichnis: C:\Users\Juerg\Arduino\Eigene\ArduToRasp

Befehl: git init        'Git Repsitory im localen Verzeinis wird angelegt'
Befehl: git add *.ino   'Dateien, die das Repository enthalten soll, werden hinzugefügt'

Befehl: git commit -m "first commit"
Befehl: git branch -M main

//Ab hier funktioniert nicht
Befehl: git remote add origin git@github.com:Cosmo100/ArduToRasp.git
Befehl: git push -u origin main

'###############################################'
Hole Datei wieder von Remote nach Local:
Beispiel Raspberry:
Öffne mit Power Shell Admin den Zufriff auf Raspberry:
    ssh root@heisopi
    password: tester10
    
    wir starten im Pfad /root
    wechsele in Pfad "Schreibtisch":
    cd Schreibtisch

   Erfrage Status mit: git status
 Befehl: git pull  # holt die Dateien von Remote nach local'  
 Meldung: Enter passphrase for key '/root/.ssh/id_ed25519':   
 Passwort: tester10
 
 Hole Datei wieder von Local nach Remote: (Windows)
  Starte Git bash
  wechsele nach verzeichnis: ~/raspberry/Raspberrygit   
 frage nach: git status
 Befehl:  git add 'Anleitung Git.py' oder git add *.py
  Befehl: git commit -m "Erweiterung Anleitung"
     git push
     Meldung: Enter passphrase for key '/root/.ssh/id_ed25519':
     Eingabe Passwort: tester10
