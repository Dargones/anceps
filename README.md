# Scansion project

## [Download archive](https://dargones.github.io/Scansion-project/Archive.zip)

## File by file description:
* scansion.py

  The bulk of the algorithm. At first, it scans all the lines, for which the longitude of vowels by position gives enough information to determine the meter pattern. Then, it builts a dictionary based on lines already scanned and uses the dictionary to scan those lines, for which the meter pattern has not been determined. The program repeats this procedure untill no further progress is done.

* compare.py

  The program prints the distribution of different meter patterns (a unigram) obtained from the output of scansion.py. It also evaluates algorithm's performance, 
  comparing its output with manually obtained data.

* ngram.py

  The program builds two language models (e.g. one based on the first five books of the Aeneid and another based on the first five books of Metamorphoses) and then tries to classify samples that it is given into Vergilian or Ovidian. It then prints the accuracy for ngram models of different orders. Currently the unigrams have the highest accuracy, which is probably due to the fact that scansion.py has too low precision. I plan to use a digitized Latin dictionary in future to increase the accuracy of scansion.py and take advantage of bi- and trgram models.
  
* input/input.txt

  A 1000 lines from the first four books of Aeneid followed by the rest of the Aeneid and Eclogues. 

* input/input_test.txt

  The "answer key" for the first 1000 lines from input.txt. Professor Ben Johnson (hexameter.co) kindly shared this data with me. 
  
* input/aeneid.txt

  The whole of the Aeneid. 

* input/aeneid_test.txt

  The "answer key" for the first 123 lines of the Aeneid. This data was first obtained from hands-up-education.org and then verified by myself. The difference between this anser key and that from hexameter.co is that the former is more detailed. 
  
* input/Aeneid/books1_5.txt, input/Aeneid/books6_12.txt, input/Metamorphoses/books1_5.txt, and input/Metamorphoses/books6_15.txt..

  These the corresponding books from corresponding texts.
  
## Running the program:
* To scan latin poetry run scansion.py:
  ```
  python3 scansion.py input output
  ```
  Here, *input* is the name of the file that contains the lines to be scanned and *output* is the name of the file to which the program should print the scanned lines.   
  Examples (this will work with the files in the repository): 
  ```
  python3 scansion.py input/input.txt output/input_scanned.txt
  ```
  ```
  python3 scansion.py input/aeneid.txt output/aeneid_scanned.txt
  ```

* To evaluate algorithm's performance and see the frequency distribution of different meter patterns run output.py:
  ```
  python3 compare.py input_file test_file text_file format
  ```
  Here, *input_file* is the name of the file that contains the output of scansion.py, *test_file* is the name of the file that contains "answer key" for the scansion, *text_file* is the name of the file with initial text (given to scansion.py), and *format* is the format of the output. Format can either be "longshort" (e.g. -UU-UU-UU---UU--, aeneid_test.txt), or "dactylspondee" (e.g. DDDS, input_test.txt).
  
  Examples (this will work with the files in the repository after running scansion.py): 
  ```
  python3 compare.py output/aeneid_scanned.txt input/aeneid_test.txt input/aeneid.txt longshort
  ```
  ```
  python3 compare.py output/input_scanned.txt input/input_test.txt input/input.txt dactylspondee
  ```
  
* To test the autorship classification algorithm run ngram.py:
  ```
  python3 ngram.py Aeneid/books1_5.txt Metamorphoses/books1_5.txt Aeneid/books6_12.txt Metamorphoses/books6_15.txt 50 1000
  ```
  Here, *model1* is the name of the file on which to build the first language model (it will be automatically scanned by the program). This file should be in the input folder. If the file is input/x.txt, then the parameter should be just x.txt. The same holds for the rest of the parameters. *model2* is the file for the second model, *sample1* is the name of the file from which to take testing samples that are written by the same author, who wrote *model1*. Similarly, *sample2* is the file with samples from the second author. *sampleSize* is the size of the samples on which to test the models (If *sampleSize* >= 100, the accuracy will be higher than 99,7%, and so it makes sense for this parameter to be at least less than 100). *timesToRepeat* indicates the number of samples to draw from each of sample1 and sample2 for testing purposes.
  
  Example (this will work with the files in the repository): 
  ```
  python3 ngram.py Aeneid/books1_5.txt Metamorphoses/books1_5.txt Aeneid/books6_12.txt Metamorphoses/books6_15.txt 30 100
  ```

## Acknowledgements:
The 1000 scanned lines from Aeneid that I used for testing purposes were kindly shared with me by Professor Ben Johnson (who is administrating hexameter.co)
