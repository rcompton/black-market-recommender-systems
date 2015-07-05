#!/usr/bin/python3
# coding: utf-8

from bs4 import BeautifulSoup
import re
import pandas as pd
import dateutil
import os
import traceback

import concurrent.futures

import logging
FORMAT = '%(asctime)-15s %(levelname)-6s %(message)s'
DATE_FORMAT = '%b %d %H:%M:%S'
formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


DATA_DIR = os.path.join(os.getenv('HOME'), 'Desktop/evolution/')
RESULT_DIR = 'data/evolution/'
if not os.path.exists(RESULT_DIR):
  os.mkdir(RESULT_DIR)


def listing_html_to_dict(fname, fdate):
  """
  parse an evolution listing html file
  must spec date file was scraped
  """
  logger.debug(fname)
  d = {}
  try:
    soup = BeautifulSoup(open(fname, encoding='utf-8', errors='ignore'))
  except UnicodeDecodeError:
    logger.info('UnicodeDecodeError... meh {}'.format(fname))
    return
  if soup.title.text.strip() == 'Evolution   :: Home':
    logger.info('Home listing... {}'.format(fname))
    return

  d['scrape_date'] = fdate

  col8 = soup.find('div', class_="col-md-8 page-product")
  vendor = col8.find(href=re.compile('http://k5zq47j6wd3wdvjq.onion/profile/.*'))
  d['vendor'] = vendor.text.strip()

  bcs = soup.find('ol', {'class', 'breadcrumb'})
  if not bcs:
    logger.warning('no breadcrumb in {}'.format(fname))
    return
  cat = [li.text for li in bcs.find_all('li')]
  listing = cat[-1]
  cat = cat[:-1]
  d['listing'] = listing.strip()
  d['cat_tuple'] = tuple(map(lambda x: x.strip(), cat))
  d['category'] = d['cat_tuple'][-1]

  md7 = soup.find('div', class_='col-md-7')
  if md7 is None:
    logger.warning('no md7')
    print(soup.prettify())
    return
  price = md7.find('strong')
  if price:
    d['price'] = price.text.strip()
  ship = md7.find('dl', class_="dl-horizontal")
  if ship:
    for dt in ship.find_all('dt'):
      if dt.text.lower() == 'ships from':
        d['ships_from'] = dt.find_next_sibling('dd').text.strip()

  alldivs = soup.find_all('div', class_='container')
  bigdiv = [x for x in alldivs if x.parent == soup.body]
  if len(bigdiv) > 0:
      #d['big_text'] = bigdiv[0]
    for h4 in bigdiv[0].find_all('h4'):
      if h4.text.strip() == 'Description':
        d['description'] = h4.find_next_sibling('p').text.strip()
      if h4.text.strip() == 'Ships To':
        d['ships_to'] = h4.find_next_sibling('p').text.strip()
  # logger.info(d)
  return d


def listdir_to_df(listdir, fdate):
  logger.info('processing: {}'.format(listdir))
  fs = os.listdir(listdir)
  fs = map(lambda x: os.path.join(listdir, x), fs)
  l = []
  for f in fs:
    if os.path.isfile(f):
        # try:
      l.append(listing_html_to_dict(f, fdate))
      # except:
      # logger.exception(f)
  dfout = pd.DataFrame(l)
  logger.info('shape dfout: {}'.format(dfout.shape))
  print(dfout.head(3))
  return dfout


def tuple_eater(tup):  # for concurrent
  return listdir_to_df(tup[0], tup[1])


def get_dirs_and_dates():
  l = []
  for datestr in os.listdir(DATA_DIR):
    d1 = os.path.join(DATA_DIR, datestr)
    fdate = dateutil.parser.parse(datestr)
    listdir = os.path.join(d1, 'listing')
    if os.path.exists(listdir):
      l.append((listdir, fdate))
  return l


def main():
  inp = get_dirs_and_dates()

  # concurrent!
  with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
    dfs = executor.map(tuple_eater, inp)

  # write
  df = pd.concat(dfs)
  outname = 'listing_df_' + datestr + '.tsv'
  df.to_csv(os.path.join(RESULT_DIR, outname), '\t', index=False)


if __name__ == '__main__':
  main()
