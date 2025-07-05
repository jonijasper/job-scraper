# main.py
# v0.1
"""
Find, filter and organize open job positions
"""
import datetime
import random
import sys
import time
import urllib.error
import urllib.request

from tools.jobparser import JobParser
from tools.jobsdataframe import JobsDataFrame
try:
    from tools.httperrcodes import HTTP_ERROR_CODES
except ImportError:
    HTTP_ERROR_CODES = None

CSVFILE = "jobs.csv"
CSVCOMMENT = '#'
PAGE = "https://duunitori.fi/tyopaikat/alue/jyvaskyla?order_by=date_posted"

def xprint(msg: str, level: str="INFO", logfile: str=None):
    """ Autoformat info, warning, error, etc. messages.

    INFO -level (default) messages are directed to stdout, others to stderr.
    
    Message format:

        *** level: msg

    Args:
        msg: A string containing the message.
        level (optional): Prefix for the message. Defaults to "INFO".
        logfile (optional): Path to file. If provided, the message is also
            written to the file.
    ---        
    """
    if level == "INFO":
        stream = sys.stdout
    else:
        stream = sys.stderr

    fmsg = f"*** {level}: {msg}"
    print(fmsg, file=stream)

    if logfile:
        with open(logfile, 'a') as f:
            f.write(fmsg + "\n")

def pagesource(url: str) -> str:
    """Read page source from url

    Args:
        url: Page url as string.

    Returns:
        str: A string containing the page source code, or empty string, if the
            page could not be reached.

    Example:
        html_src = pagesource("https://quotes.toscrape.com/")
    ---
    """
    d0 = datetime.date(2024, 4, 16)
    v0 = 125
    diff = datetime.date.today() - d0
    version = v0 + (diff.days // 30)
    browser = (f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}.0) "
                f"Gecko/20100101 Firefox/{version}.0")

    req = urllib.request.Request(url, headers={'User-Agent': browser})
    try:
        with urllib.request.urlopen(req) as response:
            source_bytes = response.read()

    except urllib.error.URLError as e:
        err = f"{e.reason}"
        if hasattr(e, 'code'):
            err = f"{e.code} " + err
            if HTTP_ERROR_CODES:
                _, desc = HTTP_ERROR_CODES[e.code]
                if desc:
                    err += f"\n\t{desc}."

        xprint(err, level="ERROR")
        xprint(url, level="PAGE")
        page = ""
    
    else:
        page = source_bytes.decode('utf-8', 'replace')

    return page

def search_jobs(maxpages: int):
    """Uses html parser to extract job info from page source and saves the
    results to csv-file.
    ---
    """
    updated = datetime.date.today()
    xprint(f"Writing results to {CSVFILE}.")
    with open(CSVFILE, 'w') as f:
        f.write(f"{CSVCOMMENT}Updated,{updated}\n")

    parser = JobParser()
    url = PAGE
    i=0
    while url:
        html_src = pagesource(url)
        parser.feed(html_src)
        jobs = JobsDataFrame(parser.alljobs)
        jobs.to_csv(CSVFILE, mode='a', index=False, header=(i==0))

        i+=1
        if i < maxpages:
            url = parser.nextpage
            parser.reset_()
            time.sleep(3)
        else:
            url=None

        xprint(f"Page {i}/{maxpages} done.")
    
    parser.close()
    

def get_jobs(*args, refresh: bool=False, maxpages: int=30, **kwargs):
    if refresh:
        search_jobs(maxpages)
    
    return JobsDataFrame.from_csv(*args, comment=CSVCOMMENT, **kwargs)


if __name__ == "__main__":
    jobs = get_jobs(CSVFILE, refresh=True)
    jobs.spread("jobs.xlsx")
