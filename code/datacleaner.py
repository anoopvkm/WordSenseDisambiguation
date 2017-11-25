import xml.etree.ElementTree as et
import os
import json
def extract_senses(filename):
    tree = et.parse(filename)
    root = tree.getroot()

    vocab = set()
    senses = set()
    for child in root:
        word =  child.attrib['text']
        vocab.add(word)

        if 'sense' in child.attrib:
            senses.add(child.attrib['sense'])
    
    return vocab, senses

def extract_meta():
    vocab = set()
    sense = set();
    for subdir, dirs, files in os.walk('../rowdata'):
        for file in files:
            filename = os.path.join(subdir, file)
            if filename.endswith('.xml'):
                v,s = extract_senses(filename)
            
                vocab = vocab.union(v)
                sense = sense.union(s)


    vmap = {}
    i = 0
    for word in vocab:
        vmap[word] = i
        i = i + 1

    json.dump(vmap, open('../vmap.json', 'w'))
    smap = {}
    i = 0
    for word in vocab:
        smap[word] = i
        i = i + 1

    json.dump(smap, open('../smap.json', 'w'))

    

    print len(vocab), len(sense)
                
extract_meta()
