### The code

This directory contains all the code that it takes to scan a Latin text. Please,
note that the code should be executed from the parent folder (the repository's 
root folder)

#### List of files

- *scraping.py* - module for web scraping
[MusisQueDeoQue](http://mizar.unive.it/mqdq/public/index) and [poetiDItalia](http://mizar.unive.it/poetiditalia/public/)
databases. Set the DATABASE parameter before using. The progress might not be 
correcly displayed unless you set the NUM_AUTHORS variable. Also, you need to 
specify the output directory by setting the BASEDIR variable.

- *mqdqParser.py* - module for extracting and using information about natural
vowel quantities from the scanned MqDq texts. Usages:
    ```
    python3 mqdqParser.py clean FILE CLEANED_FILE
    python3 mqdqParser.py merge FILE_1 FILE_2 ... FILE_N DICT_NAME
    python3 mqdqParser.py automatic METAFILE
    ```

- *uproblem.py* - uses data from Perseus to build a dictionary that maps words 
in Latin transcription (no "v" or "j") to German-like transcription 
(differentiating consonants "v" and "j" from vowels "u" and "i")

- *meter_converted.py* - a script to merge the manually obtained data with 
the automatically scanned lines to get the complete scansion of a text .

- *compare.py* - the program prints the distribution of different meter patterns 
(a unigram) obtained from the output of scansion.py. 
It also evaluates algorithm's performance, 
  comparing its output with manually obtained data. Usage:
  ```
  python3 compare.py input_file test_file text_file format
  ```
  Here, *input_file* is the name of the file that contains the output of 
  scansion.py, *test_file* is the name of the file that contains "answer key" 
  for the scansion, *text_file* is the name of the file with initial text 
  (given to scansion.py), and *format* is the format of the output. 
  Format can either be "longshort" (e.g. -UU-UU-UU---UU--), or 
  "dactylspondee" (e.g. DDDS).
 
- *utilities.py* - a collection of different constants, paths, and utilities

- *similarity.py* - a script for calculation cosine similarities between the
 plays (with the plays being represented as vectors, where each dimension is a 
 certain meter type). Usage:
  ```
  python3 similarity.py input_file
  ```
  
- *scansion.py* - the actual scansion algorithm. Usage:
  ```
  python3 scansion.py file-1 file-2 ... file-n
  ```
- *analyze* - some tools for conducting analysis (thes might not work at th emoment)
