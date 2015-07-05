#!/usr/bin/python3
# coding: utf-8

from bs4 import BeautifulSoup
import re
import pandas as pd
import dateutil
import os
import traceback

import logging
FORMAT = '%(asctime)-15s %(levelname)-6s %(message)s'
DATE_FORMAT = '%b %d %H:%M:%S'
formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


DATA_DIR = '/media/aahu/buffalo/dknet/evolution/'
RESULT_DIR = 'data/evolution/'
if not os.path.exists(RESULT_DIR):
  os.mkdir(RESULT_DIR)


def html_to_df(fname, fdate):
  """
  parse an evolution html file
  must spec date file was scraped
  """
  soup = BeautifulSoup(open(fname))

  logger.info('processing: {}'.format(fname))
  soup = BeautifulSoup(open(fname))
  profs = soup.find_all(href=re.compile('http://k5zq47j6wd3wdvjq.onion/profile/.*'))
  l = []
  for p in profs:
    try:
      if p.text != 'simurgh':  # Welcome back simurgh!
        d = {}
        d['vendor'] = p.text.strip()
        d['listing'] = p.fetchPrevious()[1].text.strip()
        d['category'] = soup.title.text.strip().split('::')[1].strip()
        # try:
        #     fn = p.fetchNext()
        #     if len(fn) >= 2:
        #         d['cats_ships'] = p.fetchNext()[1].text.strip()
        #         d['price_btc'] = p.fetchNext()[2].text.strip()
        # except:
        #     logger.exception(p)
        d['scrape_date'] = fdate
        l.append(d)
    except:
      logger.exception(p)
  return pd.DataFrame(l)


def catdir_to_df(catdir, fdate):
  fs = os.listdir(catdir)
  fs = map(lambda x: os.path.join(catdir, x), fs)
  l = [html_to_df(f, fdate) for f in fs]
  return pd.concat(l).reindex()


def main():
  for datestr in os.listdir(DATA_DIR):
    d1 = os.path.join(DATA_DIR, datestr)
    fdate = dateutil.parser.parse(datestr)
    catdir = os.path.join(d1, 'category')
    if os.path.exists(catdir):
      logger.info(catdir)
      df = catdir_to_df(catdir, fdate)
      outname = 'category_df_' + datestr + '.tsv'
      df.to_csv(os.path.join(RESULT_DIR, outname), '\t', index=False)


if __name__ == '__main__':
  main()
