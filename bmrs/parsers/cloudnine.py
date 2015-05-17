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


DATA_DIR='/home/aahu/Desktop/cloudnine/'
RESULT_DIR='data/cloudnine/'

def html_to_dict(fname, fdate):
    """
    parse a cloudnine html file
    must spec date file was scraped
    """
    d = {}
    try:
        soup = BeautifulSoup(open(fname, encoding='utf-8', errors='ignore'))
    except UnicodeDecodeError:
        logger.info('UnicodeDecodeError... meh {}'.format(fname))
        return

    #first, get cats name
    bcs = soup.find('ol',{'class','breadcrumb'})
    if not bcs:
        logger.warning('no breadcrumb in {}'.format(fname))
        return
    cat = [li.text for li in bcs.find_all('li')]
    listing = cat[-1]
    cat = cat[:-1]
    d['listing'] = listing.strip()
    d['cat'] = tuple(map(lambda x: x.strip(),cat))

    prd = soup.find('div',{'class','productbox'})
    if prd is None:
        return
    div = [l.text for l in prd.find_all('div')]
    if len(div) == 5:
        q_sold = div[-1]
        d['quantity_sold'] = q_sold

    price, ships_from, ships_to, quantity = div[:4]
    d['price'] = price.strip()
    d['ships_from'] = ships_from.strip()
    d['ships_to'] = ships_to.strip()
    d['quantity_available'] = quantity.strip()

    vtag = soup.find(text=re.compile('.*Public PGP key of.*'))
    if str(vtag) == vtag:
        if len(vtag.parent()) > 0:
            d['vendor'] = vtag.parent()[0].text.strip()
        else:
            try:
                d['vendor'] = str(vtag).split('\n')[1].strip()
                logger.debug(d['vendor'])
            except IndexError:
                logger.exception(vtag)
    else:
        try:
            vendor = vtag.parent.find('a').text
            d['vendor'] = vendor.strip()
        except AttributeError:
            logger.warning(vtag)

    d['scrape_date'] = fdate
    return d


def main():
    for datestr in os.listdir(DATA_DIR):
        fdate = dateutil.parser.parse(datestr).date()
        l = []
        datedir = os.path.join(DATA_DIR,datestr)
        for fname in os.listdir(datedir):
            if fname.endswith('product'):
                d = html_to_dict(os.path.join(datedir,fname),fdate=fdate)
                if d is not None:
                    l.append(d)
        if l:
            df = pd.DataFrame(l)
            outname ='cloudnine_'+fdate.isoformat()+'.tsv'
            df.to_csv(os.path.join(RESULT_DIR,outname),'\t',index=False)
            logger.info('done with: '+outname)
        else:
            logger.warning('no data in {}'.format(datestr))


if __name__=='__main__':
    main()
