
from bmrs.freq_itemsets import spmf_interface
import os
import pandas as pd

import logging
FORMAT = '%(asctime)-15s %(levelname)-6s %(message)s'
DATE_FORMAT = '%b %d %H:%M:%S'
formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def load_agora():
  DATA_DIR = '/home/aahu/Dropbox/black-market-recommender-systems/data/agora/'
  l = []
  for fname in os.listdir(DATA_DIR):
    if fname.endswith('.tsv'):
      df0 = pd.read_csv(os.path.join(DATA_DIR, fname), sep='\t', parse_dates=['scrape_date'])
      l.append(df0)
  df = pd.concat(l)
  logger.info(df.columns)
  logger.info(df.shape)
  return df


def main():
  df = load_agora()

  baskets = []
  dfg = df.groupby('vendor')
  for name, group in dfg:
    basket = set(group['category'])
    baskets.append(basket)

  fitms = spmf_interface.run_spmf_freq_itemsets(baskets, min_support=.02)

  print(fitms)


if __name__ == '__main__':
  main()
