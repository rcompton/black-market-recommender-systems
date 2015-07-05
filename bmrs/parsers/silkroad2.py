#!/usr/bin/python3
# coding: utf-8

from bs4 import BeautifulSoup
import re
import pandas as pd
import dateutil
import os
import traceback
import unicodedata as ud
import logging
FORMAT = '%(asctime)-15s %(levelname)-6s %(message)s'
DATE_FORMAT = '%b %d %H:%M:%S'
formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


DATA_DIR = '/home/aahu/Desktop/silkroad2/'
RESULT_DIR = 'data/silkroad2/'
if not os.path.exists(RESULT_DIR):
  os.mkdir(RESULT_DIR)


def html_to_df(fname, fdate, cat):
  """
  parse a silkroad2 html file
  """
  try:
    soup = BeautifulSoup(open(fname, encoding='utf-8', errors='ignore'))
  except UnicodeDecodeError:
    logger.info('UnicodeDecodeError... meh {}'.format(fname))
    return

  items = soup.find_all('div', {'class', 'item'})
  if not items:
    logger.warning('no items in {}'.format(fname))
    return

  l = []
  for item in items:
    if not item.find('div', {'class', 'item_title'}):
      continue
    listing = item.find('div', {'class', 'item_title'}).find('a').text

    price = item.find('div', {'class', 'price'})
    if not price:
      price = item.find('div', {'class', 'price_big'})
    if not price:
      price = None
    else:
      price = price.text

    dtag = item.find('div', {'class', 'item_details'})

    vtag = item.find('div', {'class', 'vendor'})
    vendor = None
    if vtag:
      if vtag.find('a'):
        vendor = vtag.find('a').text
    if not vendor:
      if dtag:
        if dtag.find('a'):
          vendor = dtag.find('a').text

    ships_from = None
    ships_to = None
    stag = item.find('div', {'class', 'shipping'})
    if stag:
      try:
        sl = stag.text.split('\n')
        ships_from = [x for x in sl if 'ships from:' in x.lower()][0]
        ships_from = ships_from.replace('ships from:', '').strip()
        ships_to = [x for x in sl if 'ships to:' in x.lower()][0].strip()
        ships_to = ships_to.replace('ships to:', '').strip()
      except:
        logger.info(stag)

    else:
      if dtag:
        try:
          sl = dtag.text.split('\n')
          ships_from = [x for x in sl if 'ships from:' in x.lower()][0]
          ships_from = ships_from.replace('ships from:', '').strip()
          ships_to = [x for x in sl if 'ships to:' in x.lower()][0].strip()
          ships_to = ships_to.replace('ships to:', '').strip()
        except:
          logger.info(dtag)

    d = {}
    d['listing'] = listing
    d['price_btc'] = price
    d['vendor'] = vendor
    d['ships_from'] = ships_from
    d['ships_to'] = ships_to
    d['category'] = cat
    d['scrape_date'] = fdate
    l.append(d)

  return pd.DataFrame(l)


def main():
  for datestr in os.listdir(DATA_DIR):
    fdate = dateutil.parser.parse(datestr).date()
    l = []
    datedir = os.path.join(DATA_DIR, datestr)
    catdir = os.path.join(datedir, 'categories')
    if not os.path.exists(catdir):
      continue
    logger.info(catdir)
    l = []
    for cat in os.listdir(catdir):
      dname = os.path.join(catdir, cat)
      for f in os.listdir(dname):
        fname = os.path.join(dname, f)
        catf = html_to_df(fname, fdate=fdate, cat=cat)
        l.append(catf)
    df = pd.concat(l)
    outname = 'silkroad2_' + fdate.isoformat() + '.tsv'
    df.to_csv(os.path.join(RESULT_DIR, outname), '\t', index=False)
    logger.info('wrote {0} lines to: {1}'.format(len(df), outname))


if __name__ == '__main__':
  main()
