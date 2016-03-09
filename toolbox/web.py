import requests
import json
from bs4 import BeautifulSoup

def fetch_soup(url, timeout=120, verbose=False, **kwargs):
    """
    Returns a BeautifulSoup object from a web page or None if
    the response code is anything other than 200
    """
    res = fetch_url(url, timeout=timeout, verbose=verbose, **kwargs)
    if res.status_code != 200:
        return None
    return BeautifulSoup(res.content, 'html.parser')


def fetch_json(url, timeout=120, verbose=False, **kwargs):
    """
    Returns a dictionary JSON object from a web page or None if
    the response code is anything other than 200 or the response
    cannot be parsed
    """
    res = fetch_url(url, timeout=timeout, verbose=verbose, **kwargs)
    if res.status_code != 200:
        return None
    try:
        return json.loads(res.content)
    except:
        return None


def fetch_url(url, timeout=120, verbose=False, **kwargs):
    """
    Returns the contents of a URL
    """
    res = requests.get(url, timeout=timeout, params=kwargs)
    if verbose:
        print('fetched %s (%s)' % (res.url, res.status_code))
    return res
