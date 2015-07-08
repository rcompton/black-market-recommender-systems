"""
The dataypes across different parses have been a real drag.
This script will dump all the tsvs into a sqllite table that is easier to work with
"""
import pandas as pd
import numpy as np
import re
import ast
import bmrs.postprocessing.priceparsers as pp
import sqlalchemy
import sqlite3
import logging
FORMAT = '%(asctime)-15s %(levelname)-6s %(message)s'
DATE_FORMAT = '%b %d %H:%M:%S'
formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def load_silkroad2():
  logger.info('load_silkroad2')
  FNAME = 'data/silkroad2.tsv'
  df = pd.read_csv(FNAME, sep='\t', parse_dates=['scrape_date'])
  df['price_btc'] = df['price_btc'].map(pp.price_btc_parse)
  df['price_usd'] = df['price_btc'].map(lambda x: None)  # TODO: another way
  df['cat_tuple'] = df['cat'].map(lambda x: tuple(ast.literal_eval(x)))
  df = df.drop('cat', axis=1)
  df['cat_tuple'] = df['cat_tuple'].astype(str)
  df['marketplace'] = 'silkroad2'
  return df


def load_agora():
  logger.info('load_agora')
  FNAME = 'data/agora.tsv'
  df = pd.read_csv(FNAME, sep='\t', parse_dates=['scrape_date'])
  df['vendor'] = df['vendor'].map(lambda x: x.split('/')[2].strip('#'))
  df['price_btc'] = df['price_btc'].map(pp.price_btc_parse)
  df['price_usd'] = df['price_btc'].map(lambda x: None)  # TODO: another way
  df['marketplace'] = 'agora'
  return df


def load_evolution():
  FNAME = 'data/evolution.tsv'
  return pd.read_csv(FNAME, sep='\t', parse_dates=['scrape_date'])


def load_cloudnine():
  logger.info('load_cloudnine')
  FNAME = 'data/cloudnine.tsv'
  df = pd.read_csv(FNAME, sep='\t', parse_dates=['scrape_date'])
  df['cat_tuple'] = df['cat']
  df = df.drop('cat', axis=1)
  df['price_btc'] = df[df['price'].map(pp.is_btc_price)]['price'].map(pp.price_parse)
  df['price_usd'] = df[df['price'].map(pp.is_usd_price)]['price'].map(pp.price_parse)
  df = df.drop('price', axis=1)
  df = df.drop('quantity_available', axis=1)
  df = df.drop('quantity_sold', axis=1)
  df['marketplace'] = 'cloudnine'
  return df


def load_pandora():
  logger.info('load_pandora')
  FNAME = 'data/pandora.tsv'
  df = pd.read_csv(FNAME, sep='\t')
  df['price_usd'] = df['price_usd'].map(pp.price_usd_parse)
  df['price_btc'] = df['price_usd'].map(lambda x: None)  # TODO: another way
  df['listing'] = df['item']
  df = df.drop('item', axis=1)
  df['marketplace'] = 'pandora'
  return df


def load_hydra():
  logger.info('load_hydra')
  FNAME = 'data/hydra.tsv'
  df = pd.read_csv(FNAME, sep='\t')
  df['price_usd'] = df['price_usd'].map(pp.price_usd_parse)
  df['price_btc'] = df['price_usd'].map(lambda x: np.NaN)  # TODO: another way
  df['vendor'] = df['vendor'].map(lambda x: ' '.join(x.split()[:-2]))
  df['cat_tuple'] = df['cat'].map(lambda x: tuple(ast.literal_eval(x)))
  df = df.drop('cat', axis=1)
  df['cat_tuple'] = df['cat_tuple'].astype(str)
  df['listing'] = df['listing'].astype(str)
  df['marketplace'] = 'hydra'
  return df


def load_bitstamp():
  logger.info('load_bitstamp...')
  f = '/home/aahu/Dropbox/black-market-recommender-systems/data/bitstampUSD.csv'
  btp = pd.read_csv(f, header=None, names=['trade_date', 'trade_price', 'trade_vol'])
  btp['trade_date'] = pd.to_datetime(btp['trade_date'], unit='s')
  btp = btp[['trade_date', 'trade_price']]
  btp = btp.set_index('trade_date')
  return btp.resample('D', how='mean')


def merge_bitstamp(df, btp):
  logger.info('len df {}'.format(len(df)))
  assert len(df[df['price_btc'].notnull() & df['price_usd'].notnull()]) == 0
  dfm = pd.merge(df, btp, left_on='scrape_date', right_index=True)
  df1 = df[df['price_btc'].notnull()].copy()
  df2 = df[df['price_usd'].notnull()]
  if len(df1) > 0:
    df1['price_usd'] = dfm[['trade_price', 'price_btc']].apply(lambda x: x[0] * x[1], axis=1)
    dfout = pd.concat((df1, df2))
  else:
    dfout = df2
  logger.info('len dfout {}'.format(len(dfout)))
  return dfout


def build_table():
  dbname = 'sqlite+pysqlite:////home/aahu/Dropbox/black-market-recommender-systems/data/bmrs.db'
  conn = sqlalchemy.create_engine(dbname, module=sqlite3.dbapi2)

  df = load_evolution()
  print(df)
  #
  # btp = load_bitstamp()
  #
  # # do cloudnine first it has the perfect schema
  # df = load_cloudnine()
  # logger.info(df.columns)
  # merge_bitstamp(df, btp)
  # df.to_sql('bmrs', conn, index=False, if_exists='replace')
  #
  # df = load_pandora()
  # logger.info(df.columns)
  # merge_bitstamp(df, btp)
  # df.to_sql('bmrs', conn, index=False, if_exists='append')
  #
  # df = load_agora()
  # logger.info(df.columns)
  # merge_bitstamp(df, btp)
  # df.to_sql('bmrs', conn, index=False, if_exists='append')
  #
  # df = load_hydra()
  # logger.info(df.columns)
  # merge_bitstamp(df, btp)
  # print(df.dtypes)
  # df.to_sql('bmrs', conn, index=False, if_exists='append')
  #
  # df = load_silkroad2()
  # logger.info(df.columns)
  # merge_bitstamp(df, btp)
  # df.to_sql('bmrs', conn, index=False, if_exists='append')
  # return


def dedup_table():
  # http://stackoverflow.com/a/7745635/424631
  dbname = 'sqlite+pysqlite:////home/aahu/Dropbox/black-market-recommender-systems/data/bmrs.db'
  conn = sqlalchemy.create_engine(dbname, module=sqlite3.dbapi2)
  init_size = pd.read_sql('SELECT COUNT(*) FROM bmrs;', conn)
  logger.info('initial size: {}'.format(init_size))
  logger.info('batch scrapes together...')
  q = """
  SELECT d1.*
  FROM bmrs d1
    LEFT OUTER JOIN bmrs d2
    ON (d1.listing = d2.listing AND d1.vendor = d2.vendor AND
      d1.marketplace = d2.marketplace AND d1.category = d2.category AND
      d1.cat_tuple = d2.cat_tuple AND d1.ships_from = d2.ships_from AND
      d1.ships_to = d2.ships_to AND d1.scrape_date < d2.scrape_date)
  WHERE d2.listing IS NULL AND d2.vendor IS NULL AND
  d2.marketplace IS NULL AND d2.category IS NULL AND
  d2.cat_tuple IS NULL AND d2.ships_from IS NULL AND d2.ships_to IS NULL;
  """
  df = pd.read_sql(q, conn)
  df = df.drop_duplicates()
  print(df)
  logger.info('shape now: {}'.format(df.shape))
  logger.info('overwriting old table...')
  df.to_sql('bmrs', conn, index=False, if_exists='replace')
  return


def main():

  build_table()
  #dedup_table()
  pass

if __name__ == '__main__':
  main()
