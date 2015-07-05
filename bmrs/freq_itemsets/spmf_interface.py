
import os
import uuid
import pandas as pd
# coding: utf-8
import subprocess


def run_spmf_association_rule(baskets):
  """
  given a list of sets (ie market baskets)
  assign ints to each item in the data
  format and run spmf via subprocess
  map back to original format
  return dataframe
  """

  # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
  all_items = set([item for sublist in baskets for item in sublist])

  # spmf wants ints
  lbls = {}
  rev_lbls = {}
  for idx, item in enumerate(all_items):
    lbls[item] = str(idx)
    rev_lbls[str(idx)] = item

  SPMF_INPUT = 'data/spmf_input_{}.txt'.format(uuid.uuid1())

  with open(SPMF_INPUT, 'w') as fout:
    for basket in baskets:
      fout.write(' '.join([lbls[item] for item in basket]))
      fout.write('\n')

  SPMF_OUTPUT = 'data/spmf_output_{}.txt'.format(uuid.uuid1())
  subprocess.call(["java", "-jar", "bin/spmf.jar", "run", "FPGrowth_association_rules",
                   SPMF_INPUT, SPMF_OUTPUT, ".01", ".1"])

  l = []
  with open(SPMF_OUTPUT, 'r') as fin:
    for line in fin:
      d = {}
      antecedent = line.split('==>')[0].strip()
      d['antecedent'] = [rev_lbls[a] for a in antecedent.split()]
      consequent = line.split('==>')[1].split('#')[0].strip()
      d['consequent'] = [rev_lbls[c] for c in consequent.split()]
      support = line.split(':')[1].split('#')[0].strip()
      d['support'] = int(support)
      confidence = line.split(':')[2].strip()
      d['confidence'] = float(confidence)
      l.append(d)
  df = pd.DataFrame(l)
  # reorder columns
  df = df[['antecedent', 'consequent', 'support', 'confidence']]
  df = df.sort('confidence', ascending=False)
  return df


def run_spmf_freq_itemsets(baskets, min_support=.1):
  """
  given a list of sets (ie market baskets)
  assign ints to each item in the data
  format and run spmf via subprocess
  map back to original format
  return dataframe
  """

  # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
  all_items = set([item for sublist in baskets for item in sublist])

  # spmf wants ints
  lbls = {}
  rev_lbls = {}
  for idx, item in enumerate(all_items):
    lbls[item] = str(idx)
    rev_lbls[str(idx)] = item
  SPMF_INPUT = 'data/spmf_input_{}.txt'.format(uuid.uuid1())

  with open(SPMF_INPUT, 'w') as fout:
    for basket in baskets:
      fout.write(' '.join([lbls[item] for item in basket]))
      fout.write('\n')

  SPMF_OUTPUT = 'data/spmf_output_{}.txt'.format(uuid.uuid1())
  subprocess.call(["java", "-jar", "bin/spmf.jar", "run", "Charm_MFI",
                   SPMF_INPUT, SPMF_OUTPUT, str(min_support)])

  l = []
  with open(SPMF_OUTPUT, 'r') as fin:
    for line in fin:
      d = {}
      itemset = line.split('#SUP:')[0].strip()
      d['itemset'] = [rev_lbls[a] for a in itemset.split()]
      support = line.split(':')[1].split('#')[0].strip()
      d['support'] = int(support)
      l.append(d)
  df = pd.DataFrame(l)
  # reorder columns
  df = df[['itemset', 'support']]
  df = df.sort('support', ascending=False)

  os.unlink(SPMF_INPUT)
  os.unlink(SPMF_OUTPUT)

  return df


def load_evo():
  df = pd.read_csv('/home/aahu/Downloads/evolution/evolution/products_vendors.tsv',
                   sep='\t')
  # discard meta-categories"
  meta_cats = ['Other', 'Drugs', 'Guides & Tutorials', 'Fraud Related',
               'Services', 'Digital Goods', 'Electronics', 'Custom Listings']
  df = df[df['category'].map(lambda x:x not in meta_cats)]
  return df


def main():
  #df = load_evo()

  df = pd.read_csv('data/pandora/pandora_2014-09-25.tsv', sep='\t')

  baskets = []
  dfg = df.groupby('vendor')
  for name, group in dfg:
    basket = set(group['category'])
    baskets.append(basket)

  rule_df = run_spmf_freq_itemsets(baskets)
  # rule_df.to_csv('learned_rules.tsv',index=False,sep='\t')
  print(rule_df)

if __name__ == '__main__':
  main()
