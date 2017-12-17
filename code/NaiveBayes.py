import json
import nltk
import numpy as np

num_senses  = 666

pos2idx={
        'CC':0,
        'CD':1,
        'DT':2,
        'EX':3,
        'FW':4,
        'IN':5,
        'JJ':6,
        'JJR':7,
        'JJS':8,
        'LS':9,
        'MD':10,
        'NN':11,
        'NNP':12,
        'NNPS':13,
        'NNS':14,
        'PDT':15,
        'POS':16,
        'PRP':17,
        'PRP$':18,
        'RB':19,
        'RBR':20,
        'RBS':21,
        'RP':22,
        'SYM':23,
        'TO':24,
        'UH':25,
        'VB':26,
        'VBD':27,
        'VBG':28,
        'VBN':29,
        'VBP':30,
        'VBZ':31,
        'WDT':32,
        'WP':33,
        'WP$':34,
        'WRB':35,
        '``' :36,
        "''":37,
        '$':38,
        '(':39,
        ')':40,
        ',':41,
        '--':42,
        '.':43,
        ':':44,
        '#':45
        }


with open("../sl.json","r") as f:
    sl = json.load(f)

with open("../smap.json","r") as f:
    smap = json.load(f)
    smap_inv = {v:k for k,v in smap.iteritems()}

with open("../vmap.json","r") as f:
    vmap = json.load(f)
    vmap_inv = {v:k for k,v in vmap.iteritems()}

with open("../vl.json","r") as f:
    vl = json.load(f)



# word pos sense
def init_joint():
    for word in vmap_inv.keys():
            for pos in pos2idx.values():
                for sense in range(num_senses):
                    joint[word,pos,sense] = 0

        
def calc_pos_tags(sentence):
    worded_sentence = map(lambda(t): vmap_inv[t],sentence)
    pos = nltk.pos_tag(worded_sentence)
    pos = [tag[1] for tag in pos]
    pos_num = map(lambda(t): pos2idx[t],pos)
    return pos_num

def calculate_joint_num():
    for sent_idx,sentence in enumerate(vl):
        try:
            pos_tags = calc_pos_tags(sentence)
        except:continue
        #print pos_tags
        #print sentence
        for word_idx,word in enumerate(sentence):
            sense = sl[sent_idx][word_idx]
            #print word_idx
            tag = pos_tags[word_idx]
            joint[word,tag,sense] = joint[word,tag,sense] + 1
            

def calculate_word_tag_num(word,tag):
    num = 0
    for sense in range(num_senses):
        num = num + joint[word,tag,sense]
    return num

def predict_sense(word,tag):
    word_tag_num = calculate_word_tag_num(word,tag)
    maxcnt = -1
    ind = -1
    calc_sense = -1
    for sense in range(num_senses-1):
        cnt = joint[word,tag,sense]
        if cnt>maxcnt:
            maxcnt = cnt
            calc_sense = sense
    return calc_sense

def find_class_precision(sense):
    tp = confusion_matrix[sense][sense]
    fp = 0
    for i in range(num_senses-1):
        if i != sense:
            fp = fp + confusion_matrix[sense][i]
    return (tp,fp)


#print sl[1]
#print vl[0]
#init_joint()
print "Joint inited",len(vmap)*len(pos2idx)*num_senses
num = len(vmap)*len(pos2idx)*num_senses
dim = (len(vmap),len(pos2idx),num_senses)
joint = np.zeros(num).reshape(*dim)
print joint.shape
print "Finally inited joint"
#print len(sentence)*20

calculate_joint_num()
print "Calculated joint"

total_words = 0
correct_predictions = 0

confusion_matrix = np.zeros((num_senses,num_senses))


for sent_idx,sentence in enumerate(vl):
    try:
        pos_tags = calc_pos_tags(sentence)
    except:continue

    for word_idx,word in enumerate(sentence):
        predicted_sense = predict_sense(word,pos_tags[word_idx])
        actual_sense = sl[sent_idx][word_idx]
        if actual_sense != 665:
            total_words = total_words + 1
            if predicted_sense == actual_sense:
               correct_predictions = correct_predictions + 1 
            confusion_matrix[predicted_sense][actual_sense] = confusion_matrix[predicted_sense][actual_sense] + 1
                

print "Correct predictions ",correct_predictions
print "Total words ",total_words
print "Confusion Matrix",confusion_matrix

for i in range(num_senses-1):
    tp,fp = find_class_precision(i)
    print "Precision of class ",i," is ", tp/(tp+fp)
#print len(vmap)
#calc_pos_tags(vl[1])
#print vmap_inv
