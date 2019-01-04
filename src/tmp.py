from src.utilities import *

text = "Octavia.txt"

with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/trimeters/" + text) as file:
    lines = file.readlines()
with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/tmp.txt", 'w') as file:
    for line in lines:
        file.write(multireplace(re.sub('[^a-z]', '', line.lower()), {'v': 'u', 'j': 'i', 'quic': 'quid', 'gn': 'cn'}) + '\n')


with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/trimeters/OtherEditions/" + text) as file:
    lines = file.readlines()
with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/tmp_compare.txt", 'w') as file:
    for line in lines:
        file.write(multireplace(re.sub('[^a-z]', '', line.lower()),
                                {'v': 'u', 'j': 'i', 'quic': 'quid', 'gn': 'cn'}) + '\n')