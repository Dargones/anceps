### MQDQ based data

The directory contains hexameter scansions downloaded from the 
[MQDQ database](http://mizar.unive.it/mqdq/public/) and dictionaries of
vowel quantities based on this data. Some files are only locally avaliable.

#### List of files and directories:

- original - files as downloaded from MQDQ
- clean - same files preprocessed to create lists of words with quantities 
marked
- metafile.txt - list of all these files (except for works of Horace and Ausonius)
- metafile_extra.txt - list of all works of Horace and Ausonius
- dictionary.txt - a dictionary assembled from the files listed in metafile.txt
(see *mqdqParser.py*)
- dictionaries - other (author based) dictionaries