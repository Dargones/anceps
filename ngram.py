" this module is a tool for automatic creation of n-grams for newsela data "


import compare, scansion
import subprocess
import sys
is_py2 = sys.version[0] == '2'


def prepare(list, manyVersions = False, linesPerV = 100, timesRun = 1, recompute=False):
    newList = []
    for file in list:
        print('Preparing ' + file + '...')
        # scansion.main('input/' + file, 'output/dict.txt', 'output/usual/' +
                     # file)
        if not manyVersions:
            if recompute:
                compare.ngram_format('output/usual/' + file, 'output/for_ngrams/' +
                                file, False)
            newList.append(file)
        else:
            for i in range(timesRun):
                newFile = file.split('.')
                newFile = '.'.join(newFile[:-1]) + '-' + str(i) + '.' + newFile[-1]
                if recompute:
                    compare.ngram_format('output/usual/' + file,
                                     'output/for_ngrams/' +
                                     newFile, True, linesPerV)
                newList.append(newFile)
    return(newList)



def build_ngrams(inputFile, outputFile):
    """
    Build an ngram-model from the file
    """
    subprocess.call(["ngram-count",'-order', '1', "-text", inputFile, "-no-sos", "-no-eos", "-wbdiscount", "-lm", outputFile])


def article_perplexity(articleName,lmName):
    """
    :param articleName: the name of the article to calculate perplexity
    :param lmName: the name of the language model (.bo extension)
    :return: the perplexity
    """
    if is_py2:
        ouput=subprocess.check_output(["ngram", "-lm", lmName,
                                       "-ppl", articleName, "-debug", "2"],
                                      shell=False).split('\n')
    else:
        ouput = subprocess.run(["ngram", "-lm", lmName, "-ppl", articleName,
                                "-debug", "2"],
                               stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
    perplexity = ouput[-2].split(' ')
    return float(perplexity[-1])


if __name__ == '__main__':
    timesPerFile = 20
    sampleSize = 25
    vergil_learn = 'Aeneid/books1_5.txt'
    ovid_learn = 'Metamorphoses/books1_5.txt'
    list = ['6', '7', '8', '9', '10', '11', '12', '6', '7', '8',
            '9', '10', '11', '12', '13', '14', '15']
    for i in range(len(list)):
        list[i] = 'book' + list[i] + '.txt'
        if i >= 7:
            list[i] = 'Metamorphoses/' + list[i]
        else:
            list[i] = 'Aeneid/' + list[i]
    list = prepare(list, True, sampleSize, timesPerFile)
    prepare([vergil_learn, ovid_learn], False)
    vergil = 'output/for_ngrams/vergil.bo'
    ovid = 'output/for_ngrams/ovid.bo'
    build_ngrams('output/for_ngrams/' + vergil_learn, vergil)
    build_ngrams('output/for_ngrams/' + ovid_learn, ovid)
    count = 0
    for i in range(len(list)):
        print(list[i])
        v_p = article_perplexity('output/for_ngrams/' + list[i], vergil)
        o_p = article_perplexity('output/for_ngrams/' + list[i], ovid)
        if i <= 7 * timesPerFile:
            if v_p < o_p:
                count += 1
            print('V = ' + str(v_p) + ', O = ' + str(o_p) + ' ' + str(v_p < o_p))
        else:
            if v_p > o_p:
                count += 1
            print(
                'V = ' + str(v_p) + ', O = ' + str(o_p) + ' ' + str(v_p > o_p))
    print(count/len(list))
