#!/usr/bin/python3
# coding: utf-8

from bs4 import BeautifulSoup
import re
import pandas as pd
import dateutil
import os
import traceback


DATA_DIR='/home/aahu/Desktop/pandora/'
RESULT_DIR='data/pandora/'

def html_to_df(fname, fdate, category):
    """
    parse a pandora html file
    must spec date file was scraped
    """
    soup = BeautifulSoup(open(fname))

    #first, get cat name
    lis = soup.find_all('li')
    cats = {}
    for li in lis:
        cs = li.find(href=re.compile("listing/cat/."))
        if cs is not None:
            cats[cs['href'].split('/')[-1]] = cs.text.strip()
    try:
        catname = cats[category]
    except KeyError:
        catname=category

    tbls = soup.find_all('tr')
    l = []
    for tbl in tbls:
        d = {}
        if len(tbl.find_all('strong')) > 0:
            itemtag = tbl.find('a')
            item = itemtag.find(text=True)
            if item is not None:
                d['item'] = str(item).strip()
                sellertag = itemtag.findNext('a')
                seller = sellertag.find(text=True)
                d['vendor'] = str(seller).strip()
                shipfromtag = sellertag.findNext('strong')
                shipsfrom = shipfromtag.nextSibling
                d['ships_from'] = str(shipsfrom).strip()
                shiptotag = shipfromtag.findNext('strong')
                shipsto = shiptotag.nextSibling
                d['ships_to'] = str(shipsto).strip()
                pricetag = shiptotag.findNext('strong')
                price = pricetag.nextSibling
                d['price_usd'] = str(price).strip()
                d['scrape_date'] = fdate
                d['category'] = catname
                l.append(d)
    return pd.DataFrame(l)


def catdir_to_df(catdir, cat, fdate):
    if not os.path.isdir(catdir):
        print('not dir!, trying to parse the file... ', catdir)
        try:
            return html_to_df(catdir,category=cat, fdate=fdate)
        except:
            traceback.print_tb()
            return
    fs = os.listdir(catdir)
    fs = map(lambda x: os.path.join(catdir,x),fs)
    l = [html_to_df(f,category=cat, fdate=fdate) for f in fs]
    return pd.concat(l)

def main():
    for datestr in os.listdir(DATA_DIR):
        d1 = os.path.join(DATA_DIR, datestr)
        fdate = dateutil.parser.parse(datestr).date()
        catdir = os.path.join(d1,'listing/cat')
        if os.path.exists(catdir):
            l = []
            for cat in os.listdir(catdir):
                onecat_dir = os.path.join(catdir,cat)
                df = catdir_to_df(onecat_dir, cat=cat, fdate=fdate)
                l.append(df)
                print('done with cat: ',cat)
            df = pd.concat(l)
            outname ='pandora_'+fdate.isoformat()+'.tsv'
            df.to_csv(os.path.join(RESULT_DIR,outname),'\t',index=False)
            print('done with: '+outname)


if __name__=='__main__':
    main()
