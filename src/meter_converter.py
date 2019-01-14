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


def merge_data(automatic_file, manual_file, input_file, output_file, switchingLines=None, meter_type=TRIMETER):
    """
    Create a master full with full scansions of the input_file
    :param automatic_file:  The file with automatically scanned lines
    :param manual_file:     The file with manually scanned lines
    :param input_file:      The file with the actual text
    :param output_file      The file to which to write the result
    ;:param meter_type:     Type of meter used to scan the data
    :return:
    """
    if switchingLines is not None:
        switches = {multireplace(re.sub('[^a-z]', '', line.lower()), {'v': 'u', 'j': 'i'}): False
                for line in open(switchingLines).readlines()}
    else:
        switches = {}
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
                   "X - monosyllabic anceps (can also be marked as _ or ^ wherever the line is\n\t"
                   "scanned manually)\n"
                   "_ - long syllable\n^ - short syllable\n"
                   "& - the quantity is unknown (for elided syllables, anceps syllables,\n\t"
                   "or syllables long by position)\n")
        result = ""
        unscanned = 0
        resolutions = 0
        resolutions_switches = 0
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
            resolutions += len(list(re.findall('\^\^', scansion)))
            if key in switches:
                resolutions_switches += len(list(re.findall('\^\^', scansion)))
                switches[key] = True
            result += line.rstrip(' \n') + '\t' + vocab.rstrip('\n') + '\t' + scansion + '\t' + postfix + '\n'

        if unscanned != 0:
            file.write("Note that there are " + str(unscanned) +
                       " lines that are not scanned\n")
        if False in [switches[x] for x in switches.keys()]:
            print("Not all switching lines were encountered")
            print([x for x in switches.keys() if not switches[x]])
        file.write("Resolution rate: " + str(round(resolutions / len(text), 3)))
        if len(switches.keys()) != 0:
            file.write("\nResolution rate in lines in which speakers remain the same: " +
                       str(round((resolutions - resolutions_switches) / (len(text) - len(switches.keys())), 3)))
            file.write("\nResolution rate in lines in which speakers change: " +
                    str(round(resolutions_switches / len(switches.keys()), 3)))
        file.write("\n*/\n\n" + result)


def winge_converter(source):
    lines = [line.rstrip('\n') for line in open(source)]
    lines = [multireplace(line, {'u': '^', '-': '_', '|': ''}) for line in lines]
    lines = [scansion_versions(line, TRIMETER, 0) for line in lines]
    for i, line in enumerate(lines):
        if len(line) == 0:
            lines[i] = ''
        elif len(line) == 1:
            lines[i] = ''.join(line[0])
        else:
            print("Ambiguity")
            exit(-1)
    with open(source, 'w') as file:
        file.writelines('\n'.join(lines))


if __name__ == "__main__":
    name = "Troades.txt"
    merge_data("/Users/alexanderfedchin/PycharmProjects/Scansion_project/output/" + name,
               "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/manualAndTesting/" + name,
               "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/trimeters/" + name,
               "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/completedScansions/" + name,
               "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/trimeters/switchingLines/" + name,
               TRIMETER)
    """
    winge_converter(
        "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/winge/" + name)"""