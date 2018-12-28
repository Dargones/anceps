from src.scansion import *
import datetime

BACKUP_METER_TYPE = TRIMETER
now = datetime.datetime.now()

def convert_meter(meter, meter_type, line):
    """
    Reduce the meter to the notation that does ont differentiate between
    teh types of anceps. Also, check that such meter is acceptable
    :param meter: Meter to convert
    :param meter_type: Type of meter used
    :param line: The actual text of the line
    :return:
    """
    result = scansion_versions(meter, meter_type, 0)
    if len(result) > 1 or result == []:
        result = scansion_versions(meter, BACKUP_METER_TYPE, 0)
        if len(result) > 1 or result == []:
            print('WARNING. A line is not scanned properly: ' + line + " " + str(meter) + " " + str(len(result)))
            return re.sub('&', 'X', meter)
        else:
            print("The backup meter type was used for line: " + line)
    meter = result[0]
    return re.sub('&', 'X', ''.join(meter))


def read_manual_data(filename, meter_type):
    """
    Read the manually scanned lines into a dictionary
    :param filename:
    :param meter_type: Type of meter used
    :return:
    """
    with open(filename) as file:
        lines = [x.split('|')[0].lower() for x in file.readlines()]
    dictionary = {}
    for line in lines:
        text = multireplace(re.sub('[^a-z]', '', line), {'v': 'u', 'j': 'i'})
        meter = line
        meter = re.sub(']', '_', meter)
        meter = convert_meter(re.sub('[^&\\^_]', '', meter), meter_type, line.rstrip('\n'))
        # marking vowels long by position as unknown
        vocab = re.sub('_([^a-zA-Z\^\[\]_]* [^a-zA-Z\^\[\]_]*)([xz]|['+ CONSONANTS +']{2})', r'&\1\2', line)
        vocab = re.sub(
            '_(['+CONSONANTS+'][^a-zA-Z\^\[\]_]* [^a-zA-Z\^\[\]_]*[' + CONSONANTS + '])', r'&\1', vocab)
        vocab = re.sub(
            '_([xz]|['+ CONSONANTS +']{2})([^a-zA-Z\^\[\]_]* )',r'&\1\2', vocab)
        # elision
        vocab = re.sub('(['+VOWELS+'])(m?[^a-zA-Z\^\[\]_]* [^a-zA-Z\^\[\]_]*h?['+VOWELS+'])', r'\1&\2', vocab)
        # elision of long vowels
        dictionary[text] = (meter, vocab)
    return dictionary


def merge_data(automatic_file, manual_file, input_file, output_file, meter_type):
    """
    Create a master full with full scansions of the input_file
    :param automatic_file:  The file with automatically scanned lines
    :param manual_file:     The file with manually scanned lines
    :param input_file:      The file with the actual text
    :param output_file      The file to which to write the result
    ;:param meter_type:     Type of meter used to scan the data
    :return:
    """
    with open(input_file) as file:
        text = file.readlines()
    with open(automatic_file) as file:
        lines = file.readlines()
        scansions = [re.sub('[^&X\\^_|]', '', x.split('\t')[0]) for x in lines]
        vocabs = [x.split('\t')[1] for x in lines]
        scores = [float(x.split('\t')[2].rstrip('\n')) for x in lines]
    dictionary = read_manual_data(manual_file, meter_type)
    with open(output_file, 'w') as file:
        file.write("/*\nCreated by Aleksandr Fedchin on %d/%d/%d.\n" %(now.day, now.month, now.year))
        file.write("This is the complete scansion of trimeter sections of _\n")
        file.write("The edition used is _\nEstimated accuracy: 98%\n\n")
        file.write("Each line contains a verse from the original text, a list of words from that\n"
                   "verse with their inferred scansions, the scansion itself, and one of the\n"
                   "following tags:\n"
                   "    'm' - if the line was manually scanned\n"
                   "    'v' - if automatically produced scansion was manually verified\n"
                   "    'c' - if automatically produced scansion was corrected\n"
                   "    'u' - if the line was left unscanned\n"
                   "    confidence score that the program assigns to the line (higher=better)\n\n"
                   "")
        file.write("Key:\n"
                   "X - monosyllabic anceps (can also be marked as _ or ^)\n"
                   "_ - long syllable\n^ - short syllable\n"
                   "& - the quantity is unknown\n"
                   "(for elided syllables, anceps syllables, or syllables long by position)\n")
        result = ""
        unscanned = 0
        for i, line in enumerate(text):
            key = multireplace(re.sub('[^a-z]', '', line.lower()), {'v': 'u', 'j': 'i'})
            scansion = scansions[i]
            vocab = vocabs[i]
            postfix = str(round(scores[i], 2))
            if key in dictionary:
                if scansion == '&' or '|' in scansion:
                    postfix = "m"
                elif len(scansion.split('|')) == 1 and scansion != dictionary[key][0]:
                    postfix = "c"
                    print("Warning: Scansions don't match for line: " + line
                          + str(scansion) + "\n" + str(dictionary[key][0]))
                elif len(scansion.split('|')) == 1 and scansion == dictionary[key][0]:
                    postfix = "v"
                scansion = dictionary[key][0]
                vocab = dictionary[key][1]
            if '|' in scansion or '&' in scansion or scansion == "":
                vocab = ""
                unscanned += 1
                postfix = "u"
                if not key in dictionary:
                    print("Warning: Line is not scanned: " + line + '\t' + scansion)
                    # print(line.rstrip('\n'))
                    pass
                scansion = ""
            result += line.rstrip(' \n') + '\t' + vocab.rstrip('\n') + '\t' + scansion + '\t' + postfix + '\n'

        if unscanned != 0:
            file.write("Note that there are " + str(unscanned) +
                       " lines that are not scanned\n")
        file.write("*/\n\n" + result)


def winge_converter(file1, file2, outputfile):
    lines = [line.rstrip('\n') for line in open(file1)]
    for i, line in enumerate(open(file2)):
        line = line.rstrip('\n')
        if i + 1 < len(lines):
            if lines[i + 1] == '':
                lines[i + 1] = line
        else:
            lines.append(line)
    lines = [multireplace(line, {'u': '^', '-': '_', '|': ''}) for line in lines]
    lines = [scansion_versions(line, TRIMETER, 0) for line in lines]
    for i, line in enumerate(lines):
        if len(line) == 0:
            lines[i] = '&'
        elif len(line) == 1:
            lines[i] = ' '.join(line[0])
        else:
            print("Ambiguity")
            exit(-1)
    with open(outputfile, 'w') as file:
        file.writelines('\n'.join(lines))


if __name__ == "__main__":
    name = "Thyestes.txt"
    merge_data("/Users/alexanderfedchin/PycharmProjects/Scansion_project/output/" + name,
               "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/manualAndTesting/" + name,
               "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/trimeters/" + name,
               "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/completedScansions/" + name, TRIMETER)
    """winge_converter(
        "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/winge/testPart1.txt",
        "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/winge/testPart2.txt",
        "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/winge/test.txt")"""