import xml.etree.ElementTree as et
import os
import json
import collections
def extract_senses(filename):
    tree = et.parse(filename)
    root = tree.getroot()

    vocab = set()
    senses = set()
    for child in root:
        word =  child.attrib['text']
        word = word.lower()
        vocab.add(word)

        if 'sense' in child.attrib:
            senses.add(child.attrib['sense'])
    
    return vocab, senses

def extract_senses_top(filename, vocabmap):
    tree = et.parse(filename)
    root = tree.getroot()

    vocab = set()
    senses = set()
    for child in root:
        word =  child.attrib['text']
        word = word.lower()
        vocab.add(word)
        
        if 'sense' in child.attrib:
            senses.add(child.attrib['sense'])
            if word in vocabmap:
                vocabmap[word].add(child.attrib['sense'])
            else:
                tset = set()
                tset.add(child.attrib['sense'])
                vocabmap[word] = tset
    
    return vocab, senses, vocabmap


def extract_meta():
    vocab = set()
    sense = set()
    vcmap = {}
    for subdir, dirs, files in os.walk('../rowdata'):
        for file in files:
            filename = os.path.join(subdir, file)
            if filename.endswith('.xml'):
                v,s, vcmap = extract_senses_top(filename, vcmap)
            
                vocab = vocab.union(v)
                sense = sense.union(s)

 
    ct = collections.Counter()
    for word in vcmap:
        ct[word] = len(vcmap[word])


    sense = set()
    tvocab = set()
    for k,v in  ct.most_common(100):
        tvocab.add(k)
        sense  = sense.union(vcmap[k])

    words = ['star', 'planet','actor','frequency', 'fish', 'bass','music', 'sound', 'instrument', 'bank', 'finance', 'financial', 'financier', 'institute', 'slope', 'water', 'river']

    tvocab = set()
    sense = set() 
    for word in words:
        tvocab.add(word)
        if word in vcmap:
            sense = sense.union(vcmap[word])


    for word in words:
        print 'word sense count', word, ct[word]

    vocab = get_words(tvocab)
    
    
    smap = {}
    i = 0
    for word in sense:
        smap[word] = i
        i = i + 1
    
    smap['O'] = i


    vmap = {}
    i = 0
    for word in vocab:
        if word in words and word in vcmap:
            for sense in vcmap[word]:
                tword  = word+str(smap[sense])
                vmap[tword] = i
                i = i+1

        else:
            vmap[word] = i
            i = i + 1

    json.dump(vmap, open('../vmapw2v.json', 'w'))
  
    json.dump(smap, open('../smapw2v.json', 'w'))

    print smap
    #print len(vocab), len(sense)

    return vmap, smap, tvocab

def get_words(tvocab):
    vocab = set()
    for subdir, dirs, files in os.walk('../rowdata'):
        for file in files:
            filename = os.path.join(subdir, file)
            if filename.endswith('.xml'):
                tmp = get_words_sentences(filename, tvocab)
                vocab = vocab.union(tmp)


    return vocab
                
                
def get_words_sentences(filename,tvocab):
    tree = et.parse(filename)
    root = tree.getroot()

    sense = []
    data = []
    senses = []
    sentences = [] 
    prev = 'dummy'
    flag = False

    vocab = set()
    tempvocab = set()
    st = []
    for child in root:
        word =  child.attrib['text']
        word = word.lower()
        if child.attrib['break_level'] == 'NO_BREAK' and prev != 'dummy':
            prev = "not dummy"
        elif child.attrib['break_level'] == 'NO_BREAK':
            prev = "not dummy" 
            st.append(word)
            tempvocab.add(word)
            if word in tvocab:
                flag = True
       

        elif child.attrib['break_level'] == 'SPACE_BREAK' or child.attrib['break_level'] == 'LINE_BREAK':
            
            st.append(word)
            tempvocab.add(word)
            if word in tvocab:
                flag = True
        else:
            #print filename, st
            st = [] 
            if flag :
                vocab = vocab.union(tempvocab)
            tempvocab = set()
            flag = False
            
            tempvocab.add(word)
            if word in tvocab:
                flag = True
      
    return vocab 

def handle_sentence_word2vec(filename, vmap, smap, tvocab):
    tree = et.parse(filename)
    root = tree.getroot()

    sense = []
    data = []
    senses = []
    sentences = [] 
    prev = 'dummy'
    flag1 = True
    flag2 = False
    st = []
    for child in root:
        word =  child.attrib['text']
        word = word.lower()
        if child.attrib['break_level'] == 'NO_BREAK' and prev != 'dummy':
            prev = "not dummy"
        elif child.attrib['break_level'] == 'NO_BREAK':
            prev = "not dummy"
            if word in vmap:
                data.append(vmap[word])
                st.append(word)
            else:
                flag1 = False
                continue

            if 'sense' in child.attrib and child.attrib['sense'] in smap:
                flag2 = True;
                sense.append(smap[child.attrib['sense']])
            else:
                sense.append(smap['O'])
       

        elif child.attrib['break_level'] == 'SPACE_BREAK':
            if word in vmap:
                data.append(vmap[word])
                st.append(word)
            else:
                flag1 = False
                continue;
            if 'sense' in child.attrib and child.attrib['sense'] in smap:
                flag2 = True
                sense.append(smap[child.attrib['sense']])
            else:
                sense.append(smap['O'])
        else:
            if flag1 and flag2:
                senses.append(sense)
                sentences.append(data)
                #print filename, st
            flag1 = True
            flag2 = False
            sense = []
            data = []
            st = []
            if word in vmap:
                data.append(vmap[word])
                st.append(word)
            else:
                flag1 = False
                continue

            if 'sense' in child.attrib and child.attrib['sense'] in smap:
                flag2 = True
                sense.append(smap[child.attrib['sense']])
            else:
                sense.append(smap['O'])
       
            

        #print len(senses), len(sentences)
#        print len(senses[0]), len(sentences[0])
    return (senses, sentences)


def handle_sentence(filename, vmap, smap, tvocab):
    tree = et.parse(filename)
    root = tree.getroot()

    sense = []
    data = []
    senses = []
    sentences = [] 
    prev = 'dummy'
    flag1 = True
    flag2 = False
    st = []
    for child in root:
        word =  child.attrib['text']
        word = word.lower()
        if child.attrib['break_level'] == 'NO_BREAK' and prev != 'dummy':
            prev = "not dummy"
        elif child.attrib['break_level'] == 'NO_BREAK':
            prev = "not dummy"
            if word in vmap:
                data.append(vmap[word])
                st.append(word)
            else:
                flag1 = False
                continue

            if 'sense' in child.attrib and child.attrib['sense'] in smap:
                flag2 = True;
                sense.append(smap[child.attrib['sense']])
            else:
                sense.append(smap['O'])
       

        elif child.attrib['break_level'] == 'SPACE_BREAK':
            if word in vmap:
                data.append(vmap[word])
                st.append(word)
            else:
                flag1 = False
                continue;
            if 'sense' in child.attrib and child.attrib['sense'] in smap:
                flag2 = True
                sense.append(smap[child.attrib['sense']])
            else:
                sense.append(smap['O'])
        else:
            if flag1 and flag2:
                senses.append(sense)
                sentences.append(data)
                #print filename, st
            flag1 = True
            flag2 = False
            sense = []
            data = []
            st = []
            if word in vmap:
                data.append(vmap[word])
                st.append(word)
            else:
                flag1 = False
                continue

            if 'sense' in child.attrib and child.attrib['sense'] in smap:
                flag2 = True
                sense.append(smap[child.attrib['sense']])
            else:
                sense.append(smap['O'])
       
            

        #print len(senses), len(sentences)
#        print len(senses[0]), len(sentences[0])
    return (senses, sentences)

def extract_features():
    
    vmap, smap, tvocab = extract_meta()
    '''print 'Extracted meta data'
    print tvocab
    sl = []
    vl = []
    for subdir, dirs, files in os.walk('../rowdata'):
        for file in files:
            filename = os.path.join(subdir, file)
            if filename.endswith('.xml'):
                print filename
                senses, sentences = handle_sentence(filename, vmap, smap, tvocab)
                sl.extend(senses)
                vl.extend(sentences)
                print len(sl), len(vl), len(senses), len(sentences)
 
    json.dump(sl, open('../sl.json', 'w'))
    json.dump(vl, open('../vl.json', 'w')) 

    a = json.load(open('../sl.json'))
    b = json.load(open('../vl.json'))
    c = json.load(open('../vmap.json'))
    d = json.load(open('../smap.json'))
    print len(a), len(b)
    print len(c), len(d)
    print c['the']'''


               
extract_features()
