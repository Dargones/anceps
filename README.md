# Scansion project

## [Download archive](https://dargones.github.io/Scansion_project/Archive.zip)

## File by file description:
* scansion.py

  The bulk of the algorithm. At first, scans all the lines, for which the longitude of vowels by position gives enough information
  for determining the meter pattern. Then, builts a dictionary based on lines already scanned and uses the dictionary to scan the lines, for which
  the meter pattern has not been determined. Repeats this procedure untill no further progress is done.

* compare.py

  Prints the distribution of different meter patterns (a unigram) obtained from the output of scansion.py. Also, evaluates algorithm's performance, 
  comparing its output with the data from manual_result.txt.

* input/input.txt

  A 1000 lines from the first four books of Aeneid followed by the rest of the Aeneid and Eclogues. 

* input/manual_result.txt

  The "answer key" for the first 1000 lines from input.txt. Professor Ben Johnson (hexameter.co) kindly shared this data with me. 
  
## Running the program:
* To scan latin poetry run scansion.py:
  ```
  python3 scansion.py input dict output
  ```
  Here, *input* is the name of the file that contains the lines to be scanned, *dict* is the name of the file to which the program 
  should print generated dictionary, and *output* is the name of the file to which the program should print the scanned lines.   
  Example (this will work with the files in the repository): 
  ```
  python3 scansion.py input/input.txt output/dict.txt output/scanned_lines.txt
  ```

* To evaluate algorithm's performance and see the frequency distribution of different meter patterns run output.py:
  ```
  python3 compare.py input_file test_file
  ```
  Here, *input_file* is the name of the file that contains the output of scanasion.py, and *test_file* is the name of the file that 
  contains "answer key" for the scansion
  
  Example (this will work with the files in the repository after running scansion.py): 
  ```
  python3 compare.py output/scanned_lines.txt input/manual_result.txt 
  ```

## Acknowledgements:
The 1000 of scanned lines from Aeneid that I used for testing purposes were kindly shared with me by Professor Ben Johnson (who is administrating hexameter.co)
