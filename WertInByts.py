import struct 

Byt=3*[0]

Wert = 5623.9
Wert = int(Wert *100)

Byt[0] = (Wert>>16) & 0xff
Byt[1] = (Wert>>8) & 0xff
Byt[2] = (Wert) & 0xff


print (Byt)