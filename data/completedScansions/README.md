## This file describes how the scansions of the (pseudo-)Senecan plays were obtained.

# Digitized versions of the tragedies

The editions used for all ten plays are those by O. Zwierlein, 1986. The 
digitized versions of these editions are avaliable on
[MusisQue DeoQue](http://mizar.unive.it/mqdq/public/index). I used MqDq texts
(as on January 2019), but discovered a few typos which I corrected using the 
hard copy as a reference.
These corrections concern the following lines: *Thy.* 91, 272, 421, 711, 736, 
1044, 1074, *Her. O.* 1171, 1784, *Oed.* 840, 868, *Tro.* 792, 991, *Phoen.* 
632, *Phaed.* 378, 398.

Only trimeter sections of the tragedies are considered. Lines written in 
other meters or incomplete lines are removed (this mostly concerns choral odes)

# The process of scansion

About 91% of the lines were scanned automatically by the program. In 5.5% of the
cases, the program proposed multiple possible scansions of which I had to
choose the correct one manually. The remaining 3.5% of the lines had to be 
scanned without the program's help. 

The texts were also scanned by Johan Winge's
[Latin macronizer](https://github.com/Alatius/latin-macronizer). I examined 
all the differences between the present scansions and the scansions obtained 
with Winge's program. All the cases in which I decided to keep my scansions,
when Winge proposes a different one, are recorded in the 
*differencesWithWinge.txt* file.

It should be safe to assume that the scansions are correct for at least 98% of
the lines. The number of syllables should be identified correctly with a much
higher accuracy (close or equal to 100%).

# Choices made when creating the scansions

 The ancipites are marked with a special sign (*&*), unless resolution takes 
 place. This is done so because the quantity of ancipites cannot be identified
 automatically with high accuracy (this would require the program to 
 successfully parse Latin syntax).

Sometimes, the line can be scanned in two (or more) different ways and there is
no rule that would determine the only correct scansions. For instance *Med.* 223
could theoretically be scanned in two ways:

1) Māgnĭfĭc(um) ĕt īng|ēns, nūllă quōd | răpĭāt dĭēs:
2) Māgnĭfĭc(um) ĕt īng|ēns, nūllă quŏd ră|pĭāt dĭēs: 

In this case, my program will choose the first scansion, as it assumes that
*muta cum liquida* close the syllable on the word boundary, unless it is 
necessary that the syllable is short for the line to scan.

Other similar assumptions that I make to choose one scansion, IFF a number of 
different scansions is possible are:

* The "o" ending in 1st Sg verb forms is long (even though it can be short in 
Seneca)
* The last syllable of a word ending in "s" which is followed by a word 
starting with a consonantal "u" is long by position. (cf. *Ag.* 397, in which 
"s u" clearly closes the syllable: Fēlīx ăd aū|rēs **nūntĭūs** | uēnīt mĕās.)
* The last syllable of a word that is followed by another word starting with two
 consonants is long by position. This is not generally the case (cf.
 *Allen and Greenough's New Latin Grammar* §603.f.2 and also *Her. F.* 916, 
 *Oed.* 541, and *Ag.* 433)
 
I keep the lines that Zwierlein marks as possibly not genuine, but there is
sometimes a problem in scanning them (e.g. a syllable that is closed must
 scane short like in *Ag.* 934). For these lines I choose the closest 
 appropriate Senecan meter pattern, but in two\three cases this means marking
 a long syllable short. I also remove the square brackets from the text, since
I use them to enclose diphthongs (i.e. the only way to tell that the line is
marked as possibly not genuine by Zwierlein is to look at the hard copy).