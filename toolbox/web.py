"""
    toolbox.web
    ~~~~~~~
    Stuff to pull content from the web
"""
import requests
import json
from bs4 import BeautifulSoup


def fetch_url(url, timeout=120, verbose=False, method='get', **kwargs):
    """Returns requests.Response object"""
    if method == 'get':
        res = requests.get(url, timeout=timeout, params=kwargs)
    elif method == 'post':
        res = requests.post(url, timeout=timeout, data=kwargs)
    if verbose:
        print('fetched %s (%s)' % (res.url, res.status_code))
    return res


def fetch_soup(url, timeout=120, verbose=False, **kwargs):
    """Returns a BeautifulSoup object from a web page or None if
    the response code is anything other than 200"""
    res = fetch_url(url, timeout=timeout, verbose=verbose, **kwargs)
    if res.status_code != 200:
        return None
    return BeautifulSoup(res.content, 'html.parser')


def fetch_json(url, timeout=120, verbose=False, method='get', **kwargs):
    """Returns a dictionary JSON object from a web page or None if
    the response code is anything other than 200 or the response
    cannot be parsed"""
    res = fetch_url(url, timeout=timeout, verbose=verbose,
        method=method, **kwargs)
    if res.status_code != 200:
        raise Exception('Status code of %s received' % res.status_code)
    try:
        obj = json.loads(res.content)
    except Exception as e:
        raise Exception('Could not parse JSON: %s' % res.content)
    return obj
