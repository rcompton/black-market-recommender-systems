#!/usr/bin/python3
# coding: utf-8

from bs4 import BeautifulSoup
import re
import pandas as pd
import dateutil
import os
import traceback
import unicodedata as ud
import itertools
import logging
FORMAT = '%(asctime)-15s %(levelname)-6s %(message)s'
DATE_FORMAT = '%b %d %H:%M:%S'
formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


DATA_DIR = '/media/aahu/buffalo/dknet/agora'
RESULT_DIR = 'data/agora/'
if not os.path.exists(RESULT_DIR):
  os.mkdir(RESULT_DIR)


def no_table_html_to_df(fname, fdate, cat):
  """
  when the table parse fails try this
  """
  pass


def html_to_df(fname, fdate):
  """
  parse an agora html file
  """
  try:
    soup = BeautifulSoup(open(fname, encoding='utf-8', errors='ignore'))
  except UnicodeDecodeError:
    logger.info('UnicodeDecodeError... meh {}'.format(fname))
    return

  cat = soup.find('title')
  if cat:
    cat = cat.text.strip()
  else:
    logger.warning('no cat in {}'.format(fname))
    return

  tbl = soup.find('tbody')
  tbl = soup.find('table', {'class', 'products-list'})
  if not tbl:
    logger.warning('no items in {}'.format(fname))
    return no_table_html_to_df(fname, fdate, cat)

  l = []
  for item in tbl.find_all('tr', {'class', 'products-list-item'}):
    #     try:
    listing = item.find('a', href=re.compile('/p/.*'))
    if listing:
      listing = listing.text
    else:
      return
    vendor = item.find('a', {'class', 'gen-user-link'}, href=re.compile('/vendor/.*'))
    if vendor:
      vendor = vendor.get('href')
    else:
      return

    price = None
    pricel = [x.text for x in item.find_all('td') if 'BTC' in x.text]
    if len(pricel) > 0:
      price = pricel[0].strip()

    ships_from = None
    ships_to = None
    ships = [x for x in item.find_all('td') if ('From:' in x.text) or ('To:' in x.text)]
    if len(ships) > 0:
      shipl = ships[0].text.split('\n')
      ships_from = [x for x in shipl if 'From:' in x]
      if ships_from:
        ships_from = ships_from[0].replace('From:', '').strip()
      else:
        ships_from = None
      ships_to = [x for x in shipl if 'To:' in x]
      if ships_to:
        ships_to = ships_to[0].replace('To:', '').strip()
      else:
        ships_to = None

      d = {}
      d['listing'] = listing.strip()
      d['price_btc'] = price.split()[0]
      d['vendor'] = vendor.strip()
      d['ships_from'] = ships_from
      d['ships_to'] = ships_to
      d['category'] = cat
      d['scrape_date'] = fdate
      l.append(d)
  #     except:
  #         pass
  #
  return pd.DataFrame(l)


def main():
  for datestr in os.listdir(DATA_DIR):
    try:
      fdate = dateutil.parser.parse(datestr).date()
      datedir = os.path.join(DATA_DIR, datestr)
      catdir = os.path.join(datedir, 'cat')
      if not os.path.exists(catdir):
        continue
      logger.info(catdir)

      # figure category files
      catfiles = []
      for root, dirnames, filenames in os.walk(catdir):
        for filename in filenames:
          catfiles.append(os.path.join(root, filename))

      l = []
      for catfile in catfiles:
        df0 = html_to_df(catfile, fdate)
        l.append(df0)
      df = pd.concat(l)
      if len(df) > 0:
        outname = 'agora_' + fdate.isoformat() + '.tsv'
        df.to_csv(os.path.join(RESULT_DIR, outname), '\t', index=False)
        logger.info('wrote {0} lines to: {1}'.format(len(df), outname))
      else:
        logger.warning('no data?' + catdir)
    except:
      pass

if __name__ == '__main__':
  main()
