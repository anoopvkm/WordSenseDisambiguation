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
    sense = set()
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
    for word in sense:
        smap[word] = i
        i = i + 1
    
    smap['O'] = i
    json.dump(smap, open('../smap.json', 'w'))

    
    print len(vocab), len(sense)
 
    return vmap, smap
def handle_sentence(filename, vmap, smap):
    tree = et.parse(filename)
    root = tree.getroot()

    sense = []
    data = []
    senses = []
    sentences = [] 
    prev = 'dummy'
    for child in root:
        word =  child.attrib['text']
        if child.attrib['break_level'] == 'NO_BREAK' and prev != 'dummy':
            prev = "not dummy"
        elif child.attrib['break_level'] == 'NO_BREAK':
            data.append(vmap[word])
            if 'sense' in child.attrib:
                sense.append(smap[child.attrib['sense']])
            else:
                sense.append(smap['O'])
       

        elif child.attrib['break_level'] == 'SPACE_BREAK':
            data.append(vmap[word])
            if 'sense' in child.attrib:
                sense.append(smap[child.attrib['sense']])
            else:
                sense.append(smap['O'])
        else:
            senses.append(sense)
            sentences.append(data)
            sense = []
            data = []
            

        #print len(senses), len(sentences)
#        print len(senses[0]), len(sentences[0])
    return (senses, sentences)

def extract_features():
    
    vmap, smap = extract_meta()
    print 'Extracted meta data'
    print smap
    sl = []
    vl = []
    for subdir, dirs, files in os.walk('../rowdata'):
        for file in files:
            filename = os.path.join(subdir, file)
            if filename.endswith('.xml'):
                print filename
                senses, sentences = handle_sentence(filename, vmap, smap)
                sl.extend(senses)
                vl.extend(sentences)
                print len(sl), len(vl), len(senses), len(sentences)
 
    json.dump(sl, open('../sl.json', 'w'))
    json.dump(vl, open('../vl.json', 'w'))

    a = json.load(open('../sl.json'))
    b = json.load(open('../vl.json'))

    print len(a), len(b)


               
extract_features()
