from src.scansion import *
import sys


def convert(input_file_name, output_file_name):
    """
    Convert the data from the manually scanned files to a format that can be
    used in compare.py
    :param input_file_name:  the name of the file to convert
    :param output_file_name: the name of teh file to save converted data to
    :return:
    """
    with open(input_file_name) as file:
        lines = file.readlines()
    with open(output_file_name, 'w') as file:
        for line in lines:
            meter = re.sub(r'[^\^&_]', '', line)
            meter = scansion_versions(meter, TRIMETER, 0)
            if len(meter) > 1 or meter == []:
                print('WARNING. A line is not scanned properly: ' + line)
                file.write(line)
                continue
            meter = meter[0]
            meter = re.sub('X', '&', ''.join(meter))
            j = 0
            for i in range(len(line)):
                if line[i] in ['^', '_', '&']:
                    line = line[:i] + meter[j] + line[i + 1:]
                    j += 1
            file.write(line)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: %s input_file_name output_file_name" % sys.argv[0])
        sys.exit(-1)
    convert(sys.argv[1], sys.argv[2])