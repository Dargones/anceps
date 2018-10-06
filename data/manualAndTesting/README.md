### Testing data and manually obtained scansions

This folder contains scansions that can be used for testing purposes. Also, the
folder contains manually scanned lines that the algorithm fails to scan.
The data is either in D/S format (for hexameter only) or in _^& format, where
D = dactyl, S = sponee, _ - long syllable, ^ - short syllable, & - anceps.

#### List of files
- Aeneid_mqdq.txt - the whole of Aeneid with scansion from MqDq
- Agamemnon.txt - lines from Seneca's Agamemnon that the program fails to scan 
with annotations explaining why the program fails.
- Medea.txt - same for Seneca's Medea.
- Thyestes.txt - 13 lines of trimeter from Seneca's play.
Courtesy of Professor Pramit Chaudhuri
- trimeter.txt - manually scanned trimeters from several tragedies. Note that
it includes the data from Thyestes.txt. This is used for testing purposes.
- trimeter_annotated.txt - same file but with a header explaining the format and
the sources
- Test.txt - file containing lines from trimeter.txt that the program fails to 
scan or scans incorrectly. 
- hexameter.co.txt - 1000 scanned lines of teh Aeneid.
Courtesy of Professor Ben Johnson
- hexameter.co_original.csv - the original file as sent by Professor Johnson
- hands-up-education.txt - 123 lines of the Aeneid from this 
[webpage](https://www.hands-up-education.org/aplatinscan/index.html).