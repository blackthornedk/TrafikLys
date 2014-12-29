TrafikLys
=========

Et lille projekt, der aflæser trafikstatus på en Juniper SRX240, og viser det på et
'trafiklys', udformet som 8 LED'ere, koblet til en Arduino Uno.

Traf.py kører på en Soekris net4801, og henter trafikstatus via SNMP.
Status skrives ud på seriel porten, til en Arduino Uno, koblet på USB porten i
Soekrisen.

TrafficLigthSerial.ino er Arduino sketchen der kører på Uno'en.
LED'erne er koblet på port 2 til 9, der er indstillet som outputs.
LED'erne sourcer altså fra Arduinoen.
