### StatikLabel

StatikLabel ist ein PyQt5 Program, dass es ermöglicht Label für statische Systeme zu erstellen und mit diesen zu arbeiten. 

Nach dem Installieren der requirements:
```
python main.py
```

#### Label Tab
Öffnet eine leere GUI, in die man in dem Explorermanager eine Label und Bild datei Laden kann: 
![Example](assets/labeler.png)

In diesem Tab ist es möglich nodes zu setzen, diesen type werte zu geben wie z.B Festlager etc. und diese dann mit staeben zu Verbinden. 

#### Normalized Tab
Dieses System kann man sich dann Normalisiert anzeigen lassen und bearbeiten:
![Example](assets/normalizer.png)

In der Normalisiertung werden ähnliche längen in den verschiedenen axen gefunden und somit eine "perfektes" System erstellt, an dem es möglich ist die Berechnungen für einen Polplan zu machen.


#####  Polplan

###### Erkenunng und aufteilung in die Scheibe:
![Example](assets/scheiben.png)

###### Beschriftung der Pole der einzelnen scheiben:
![Example](assets/pole.png)

###### Erkennung welcher der Scheiben von sich aus fest sind:
![Example](assets/feste_scheiben.png)

###### Analyse des gesamten system
! noch nicht Implementiert !






