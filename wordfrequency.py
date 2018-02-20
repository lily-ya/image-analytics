''' (3)
This script obtain words and their frequencies. 
Input file: Edmunds_Extraction.csv, output file: Word_post.csv. 
It creates a second output file (pairs of words) but do not use it. For your own data file, change in the name of the input file in the script, make sure the text is in the 3rd column (if necessary insert blank column(s) before the text column to make the latter the 3rd). All input files should be placed in the Python27 directory before running the scripts. 
'''

import csv
from nltk.corpus import stopwords
import re
import string
from collections import defaultdict

stop = stopwords.words('english')

inter1 = []
sentences_all = []
sentences_clean = []
sentences_unpun = []

dictionary1 = {}
d2_dict = defaultdict(dict)

with open('edmunds_Extraction.csv') as f:
    rows = csv.reader(f, delimiter = ',')
    for row in rows:
        inter1.append(row[2])

for row in inter1:
    sentences = re.split(r' *[\.\?!][\'"\)\]]* *', row)

    for s in sentences:
        in1 = ''.join(s)
        out = re.sub('[%s]' % re.escape(string.punctuation), '', in1.lower())
        sentences_all.append(out)

for sentence in sentences_all:
    s = []
    for i in sentence.split():
        if i not in stop:
            s.append(i)
    sentences_clean.append(s)

for sentence in sentences_clean:
    #print sentence
    for word in sentence:
        dictionary1[word] = 0

for sentence in sentences_clean:
    for word in sentence:
        dictionary1[word] = dictionary1[word] + 1

for sentence in sentences_clean:
    for word in sentence:
        for word2 in sentence:
            if(word != word2):
                d2_dict[word][word2] = 0

for sentence in sentences_clean:
    for word in sentence:
        for word2 in sentence:
            if(word != word2):
                d2_dict[word][word2] = d2_dict[word][word2] + 1

writer = csv.writer(open('word_freq.csv', 'wb'))
for key, value in dictionary1.items():
    writer.writerow([key, value])

writer = csv.writer(open('word_pair_freq.csv', 'wb'))
for key1, value1 in d2_dict.items():
    for key2, value2 in d2_dict[key1].items():
        writer.writerow([key1, key2, value2])
print "written to word_freq.csv and word_pair_freq.csv"
