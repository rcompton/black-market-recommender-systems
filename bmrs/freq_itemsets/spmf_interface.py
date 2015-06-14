
import os
import uuid
import pandas as pd
# coding: utf-8
import subprocess

def run_spmf_freq_itemsets(baskets, min_support=.1):
    """
    given a list of sets (ie market baskets)
    assign ints to each item in the data
    format and run spmf via subprocess
    map back to original format
    return dataframe
    """

    #http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    all_items = set([item for sublist in baskets for item in sublist])

    #spmf wants ints
    lbls = {}
    rev_lbls = {}
    for idx,item in enumerate(all_items):
        lbls[item] = str(idx)
        rev_lbls[str(idx)] = item
    SPMF_INPUT = 'data/spmf_input_{}.txt'.format(uuid.uuid1())

    with open(SPMF_INPUT,'w') as fout:
        for basket in baskets:
            fout.write(' '.join([lbls[item] for item in basket]))
            fout.write('\n')

    SPMF_OUTPUT = 'data/spmf_output_{}.txt'.format(uuid.uuid1())
    subprocess.call(["java", "-jar", "bin/spmf.jar", "run", "Charm_MFI",
                    SPMF_INPUT, SPMF_OUTPUT, str(min_support)])

    l = []
    with open(SPMF_OUTPUT,'r') as fin:
        for line in fin:
            d = {}
            itemset = line.split('#SUP:')[0].strip()
            d['itemset'] = [rev_lbls[a] for a in itemset.split()]
            support = line.split(':')[1].split('#')[0].strip()
            d['support'] = int(support)
            l.append(d)
    df = pd.DataFrame(l)
    #reorder columns
    df = df[['itemset', 'support']]
    df = df.sort('support',ascending=False)

    os.unlink(SPMF_INPUT)
    os.unlink(SPMF_OUTPUT)

    return df

def load_wastapunk():
    df = pd.read_csv('https://gist.githubusercontent.com/svolpe43/1ff9bc56f7f000da796e/raw/e7d0085c7979306507380cb12b7e59578c6dae05/gistfile1.txt', sep=',')
    dtabse = []
    for row in df.iterrows():
        dtabse.append(set(row[1]))
    return dtabse

def main():
    dtabse = load_wastapunk()
    min_support = 50.0/len(dtabse)
    print('fractional support required: {}'.format(min_support))

    df = run_spmf_freq_itemsets(dtabse,min_support)
    print(df[df['itemset'].map(lambda x:len(x)==2)])




if __name__=='__main__':
    main()
