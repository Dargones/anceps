# Anceps - a Latin scansion tool

![Anceps](SenecaSocrates.jpg)

## About

**Anceps** is a tool for computer-assisted scansion of Latin poetry. It can 
automatically scan the majority of verses in any Latin meter and can greatly 
speed up the process of manual scansion of difficult lines. Additionally, it
can identify scansions that are inconsistent with the historical period during 
which the given text was written and is otherwise helpful for identifying
metrical anomalies. **Anceps** is being developed by Aleksandr Fedchin ([Bard College](https://www.bard.edu/), 
[Tufts University](https://www.tufts.edu/), [Quantitative Criticism Lab](https://www.qcrit.org/).

**Anceps** differs from existing scansion tools in several respects:

1) **Using meter as a constraint.** Many scansion tools begin by using a POS tagger to macronize 
all the words in a verse and only then proceed to scanning the verse. 
By contrast, **anceps** uses meter as a constraint by considering all the possible 
ways the words in a verse might be macronized that lead to the verse being 
consistent with the meter. Hence, **anceps**'s performance does not depend on the 
quality of the POS tagger but only on the dictionary of natural vowel quantities
which all scansion tools must employ. The downside is that **anceps** cannot be 
used to macronize prose.

2) **Using period- and author-specific frequency-based dictionaries.** The 
traditional approach to automated scansion is to use a dictionary that lists all
theoretically possible ways a word can be macronized. For this purpose, **anceps** 
uses the dictionary based on queries to [Morpheus](https://github.com/PerseusDL) which was created by Alatius 
for his scansion tool. However, theory-guided dictionaries like this one are not
always reliable because they do not specify how frequent a particular scansion
is. Consider `patris`, the genetive of `pater`. The `a` in `patris` can be
either long or short depending on the author and the period. Poets of the 
golden age (Horace, Ovid, Vergil) were more likely to scan `a` short, 
but some of the later poets employed both long and short scansions interchangeably 
(Statius, Lucan), or even preferred the long scansion (Silius Italicus). To
account for differences like these, **anceps** can be used with a frequency-based 
dictionary that for each form specifies how many times it was seen in the works
of each author. Such dictionaries can be built by parsing the scansions of
hexameters and pentameters made with [Pedecerto](http://www.pedecerto.eu/public/) and available on the [MusisQue DeoQue](http://mizar.unive.it/mqdq/public/)
database. With a dictionary like this, **anceps** can pinpoint unusual scansions
and assign confidence scores for each scanned verse.

3) **Command-line interface for manual scansion.** **Anceps** was originally designed
to scan lines of trimeter, which is inherently more difficult than scanning hexameter or
 pentameter. A substantial portion of the lines (around 10%) must be scanned manually
 because the scansion can depend on such things as whether an adjective is in 
 Nom. n. Pl. or Abl. f. Sg. No parser would be able to differentiate between the two 
 forms with full certainty, but a human can! Hence, **anceps** provides an easy-to-use
 command-line interface that promts the user to select the correct scansion 
 whenever the program is unsure.

4) **Configuring for use with any meter.** All that is needed to 
configure **anceps** for use with a new meter is to add a one- or two- line 
definition of that meter to *meter.py*. For instance, **anceps** can be easily 
configured for scansion of Correr's or Dati's trimeter, which is different from 
that of Seneca. 

## Documentation

Below is the description of how **anceps** can be run and configured. New features
may be added in the future.

### Scansion

To scan a text containing one verse of poetry per line, run the following command:

```bash
python -m src.scan.scan fileToScan outputFile meter -manual_file=fileWithManualScansions -dictionary=MqDqDictionary
```

For instance, to scan trimeter sections of Seneca's *Agamemnon* included in this 
repository, run:

```bash
python -m src.scan.scan data/texts/Agamemnon.txt data/fullScansions/Agamemnon.json trimeter -manual_file=data/manualScansions/Agamemnon.txt -dictionary=data/MqDqMacrons.txt
```

There are various argument that can be passed to *scan.py*. For example, you can
use the `--interactive` flag to allow the program to promt the user to select 
the correct scansion when the program is uncertain. To see the full list of 
available flags and arguments, run *scan.py* with the `-h` flag. 

**Anceps** can be easily extended for use with any meter. Consider the following
 lines, which is all one needs to add to *meter.py* to configure **anceps** for 
 scansion of hexameter, pentamerer, and elegiacs:
 
```python
SPONDEE = LONG + LONG
DACTYL = LONG + SHORT + SHORT
H_FOOT = (SPONDEE, DACTYL)  # defines a foot of hexameter
H_FINAL_FOOT = (LONG + UNK, )  # final foot (final syllable can be either long or short)

# one can optionally replace the fifth H_FOOT with [DACTYL]:
HEXAMETER = Meter((H_FOOT, H_FOOT, H_FOOT, H_FOOT, H_FOOT, H_FINAL_FOOT), "hexameter")
PENTAMETER = Meter((H_FOOT, H_FOOT, [LONG], H_FOOT, H_FOOT, [UNK]), "pentameter")

Meter.METERS["elegiacs"] = (HEXAMETER, PENTAMETER)
```

### Creating an MqDq-based dictionary

To create an MqDq-based dictionary, you first have to download MusisQue DeoQue
on your local machine. This can be done by running *scraping.py*. You can either
download the database in full or specify a particular set of authors you wish 
to download as shown below:

```bash
python -m src.mqdq.scraping mqdq -dir=data/test -authors Vergilius Horatius
```

The full set of authors currently available on MqDq can be obtained by running 
the following command:

```bash
python -m src.mqdq.scraping mqdq --list-all-authors
```

After downloading the texts on your local machine, run *dictionary.py* to
create a dictionary based on these texts:

```bash
python -m src.mqdq.dictionary data/MqDq/ data/MqdqMacrons.json
```

### Dependencies and Versions

**Anceps** should be run with `python3` with the following packages installed: `tqdm, requests, selenium`

Firefox is also required as a driver that `selenium` can use to download MqDq data.







