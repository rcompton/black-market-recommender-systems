import re
import pandas as pd

def price_btc_parse(s):
    if pd.isnull(s):
        return None
    if ('usd' in s.lower()) or ('$' in s):
        return None
    flt = re.findall("\d+\.\d+",s)
    if len(flt) > 0:
        return float(flt[0])
    return None

def price_usd_parse(s):
    if pd.isnull(s):
        return None
    if ('btc' in s.lower()) or ('฿' in s):
        return None
    if ('usd' not in s.lower()) and ('$' not in s):
        return None
    flt = re.findall("\d+\.\d+",s)
    if len(flt) > 0:
        return float(flt[0])
    return None

def is_btc_price(s):
    if pd.isnull(s):
        return False
    if ('btc' in s.lower()) or ('฿' in s):
        return True
    return False

def is_usd_price(s):
    if pd.isnull(s):
        return False
    if ('usd' in s.lower()) or ('$' in s):
        return True
    return False

def price_parse(s):
    if pd.isnull(s):
        return None
    if ('usd' in s.lower()) or ('$' in s):
        return price_usd_parse(s)
    if ('btc' in s.lower()) or ('฿' in s):
        return price_btc_parse(s)
    return None
