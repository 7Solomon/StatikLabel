### StatikLabel

StatikLabel ist ein PyQt5 Program, dass es ermöglicht Label für statische Systeme zu erstellen und mit diesen zu arbeiten. 

Nach dem Installieren der requirements:
```
python main.py
```

#### Label Tab
Öffnet eine leere GUI, in die man in dem Explorermanager eine Label und Bild datei Laden kann: 
<img src="assets/labeler.png" width="500px">


In diesem Tab ist es möglich nodes zu setzen, diesen type werte zu geben wie z.B Festlager etc. und diese dann mit staeben zu Verbinden. 

#### Normalized Tab
Dieses System kann man sich dann Normalisiert anzeigen lassen und bearbeiten:
<img src="assets/normalizer.png" width="500px">


In der Normalisiertung werden ähnliche längen in den verschiedenen axen gefunden und somit eine "perfektes" System erstellt, an dem es möglich ist die Berechnungen für einen Polplan zu machen.


#####  Polplan

###### Erkenunng und aufteilung in die Scheibe:
<img src="assets/scheiben.png" width="300px">

###### Beschriftung der Pole der einzelnen scheiben:
<img src="assets/pole.png" width="300px">

###### Erkennung welcher der Scheiben von sich aus fest sind:
<img src="assets/feste_scheiben.png" width="300px">

###### Analyse des gesamten system
! noch nicht Implementiert !



### Probleme

* Die erkennung von scheiben ist für Normal- und Querkraftgelenke in manche Axen richtungen nicht Funktional und muss durch manuelle connections ausgebessert werden.

* Mann muss noch viele dinge beachten da die Implementiereung nicht für Falsche benutzung ausgelegt ist. Dies ist etwas arbeit, auf die ich zurzeit noch nicht so viel Lust habe. 
    - (z.b Man muss neue datentypen initialisieren bei manchen system da ich connections erst am ende hizugefügt habe)

* Die Visualisierung der (Nodes)Lager ist noch richtungslos, das müsste man rein aus ästhetisch gründen ändern. Ist jedoch nicht für die Funktionsweise maßgebend.

* Die Normalisierung funtioniert eigentlich immer sehr gut, außerdem in dem System as hier als Beispiel gezeigt wird, dort werden manche Staebe als 2l angegeben obwohl sie nur 1l lang sind. Das ist nur bei diesem System, man müsste jedoch schauen ob die Normalisierung noch ein paar ungenauigkeiten beinhaltet.





