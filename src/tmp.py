from src.utilities import *

with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/tmp.txt") as file:
    lines = file.readlines()
with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/tmp.txt", 'w') as file:
    for line in lines:
        file.write(multireplace(re.sub('[^a-z]', '', line.lower()), {'v': 'u', 'j': 'i', 'quic': 'quid', 'gn': 'cn'}) + '\n')


with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/tmp_compare_saved.txt") as file:
    lines = file.readlines()
with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/tmp_compare.txt", 'w') as file:
    for line in lines:
        file.write(multireplace(re.sub('[^a-z]', '', line.lower()),
                                {'v': 'u', 'j': 'i', 'quic': 'quid', 'gn': 'cn'}) + '\n')