from src.utilities import *

replace = {' ⁔': '\n', '⁔ ': '\n', '⁔': '\n', ' ': '\n',
           'ā': 'a_', 'ă': 'a^', 'Ā': 'A_', 'Ă': 'A^',
           'ē': 'e_', 'ĕ': 'e^', 'Ē': 'E_', 'Ĕ': 'E^',
           'ī': 'i_', 'ĭ': 'i^', 'Ĭ': 'I^',
           'ŏ': 'o^', 'ō': 'o_', 'Ŏ': 'O^', 'Ō': 'O_',
           'ū': 'u_', 'ŭ': 'u^', 'V̄': 'U_', 'V̆': 'U^',
           'ȳ': 'y_', 'y̆': 'y^',
           'ǣ': '[ae]', 'Ǣ': '[Ae]', 'æ': '[ae]',
           'œ̄́': '[Oe]', 'œ̄': '[oe]',
           'œ': '[oe]', 'Œ̄': '[Oe]'}

embellishments = {replace[x]: x for x in replace.keys()}

input = "Be^ne^fi^ci^um ho^mo ho^mi^ni_ qui_ da^t, i^mi^ta_tu_r de^o&s"
print(multireplace(input, embellishments))