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


DATA_DIR='/home/aahu/Desktop/hydra/'
RESULT_DIR='data/hydra/'
if not os.path.exists(RESULT_DIR):
    os.mkdir(RESULT_DIR)

def html_to_df(fname, fdate):
    """
    parse a hydra html file
    """
    try:
        soup = BeautifulSoup(open(fname, encoding='utf-8', errors='ignore'))
    except UnicodeDecodeError:
        logger.info('UnicodeDecodeError... meh {}'.format(fname))
        return

    cat = [x.strip() for x in soup.find('title').text.split("::")]

    tbl = soup.find('tbody')
    if not tbl:
         logger.warning('no items in {}'.format(fname))
         return

    l = []
    for item in tbl.find_all('tr', class_=re.compile('odd|even')):
        try:
            listing = item.find('a', href=re.compile('/sale/.*')).text
            vendor = item.find('a', href=re.compile('/vendor/.*')).text
            details = item.find('td', {'class',"col-xs-4"})
            price = None
            ships_to = None
            ships_from = None
            if details:
                price = details.find('h5',{'class',"text-success"})
                if price:
                    price = price.text
                ships = details.find_all('span')[-1]
                if ships:
                    ships_from,ships_to = ships.text.split('  ')
            d = {}
            d['listing'] = listing.strip()
            d['price_usd'] = price.split()[0]
            d['vendor'] = vendor.strip()
            d['ships_from'] = ships_from.strip()
            d['ships_to'] = ships_to.strip()
            d['category'] = cat
            d['scrape_date'] = fdate
            l.append(d)
        except:
            pass

    return pd.DataFrame(l)


def main():
    for datestr in os.listdir(DATA_DIR):
        fdate = dateutil.parser.parse(datestr).date()
        l = []
        datedir = os.path.join(DATA_DIR,datestr)
        catdir = os.path.join(datedir,'category')
        if not os.path.exists(catdir):
            continue
        logger.info(catdir)
        l = []
        for cat in os.listdir(catdir):
            #logger.info(cat)
            if int(cat.split('.html')[0])%100 != 0:  # avoid double counts
                l.append(html_to_df(os.path.join(catdir,cat),fdate))
        df = pd.concat(l)
        if len(df) > 0:
            outname ='hydra_'+fdate.isoformat()+'.tsv'
            df.to_csv(os.path.join(RESULT_DIR,outname),'\t',index=False)
            logger.info('wrote {0} lines to: {1}'.format(len(df),outname))
        else:
            logger.warning('no data?'+catdir)


if __name__=='__main__':
    main()
