"""
Stuff to pull content from the web
"""

import requests
import json
import logging
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def fetch_url(url, timeout=30, method="get", retry=0, max_retries=10, payload=None):
    """
    Returns requests.Response object, if max_retries is exceeded, will return
    a NoneType
    """
    logger.debug(f"Fucking {url}")
    try:
        if method == "post":
            res = requests.post(url, timeout=timeout, data=payload)
        else:
            res = requests.get(url, timeout=timeout, params=payload)
    except Exception as e:
        if retry >= max_retries:
            logger.warning(f"Max retries of {max_retries} exceeded")
            return None
        logger.warning(f"Exception {e} on {url}, rety is {retry}, retrying")
        return fetch_url(
            url,
            timeout=timeout,
            method=method,
            retry=retry + 1,
            max_retries=max_retries,
            payload=payload,
        )
    return res


def fetch_soup(url, timeout=30, payload=None):
    """Returns a BeautifulSoup object from a web page or None if
    the response code is anything other than 200"""
    res = fetch_url(url, timeout=timeout, payload=payload)
    if res is None:
        return None
    return BeautifulSoup(res.content, "html.parser")


def fetch_json(url, timeout=30, method="get", payload=None):
    """Returns a dictionary JSON object from a web page or None if
    the response code is anything other than 200 or the response
    cannot be parsed"""
    res = fetch_url(url, timeout=timeout, method=method, payload=payload)

    if res is None:
        return None

    if res.status_code != 200:
        raise Exception(f"Status code of {res.status_code} received")
    try:
        obj = json.loads(res.content)
    except Exception as e:
        raise Exception(f"Could not parse JSON: {e}")

    return obj
