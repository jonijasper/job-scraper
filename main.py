# main.py
# v0.1
"""
Find, filter and organize open job positions
"""
import datetime
import pandas as pd
import random
import sys
import time
import urllib.error
import urllib.request

from tools.jobparser import JobParser


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
        >>> pagesource("https://quotes.toscrape.com/")
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

    except urllib.error.HTTPError as e:
        stdmsg(e.reason, level="ERROR (HTTP)")
        return ""

    except urllib.error.URLError as e:
        stdmsg(e.reason, level="ERROR (Connection)")
        return ""

    page = source_bytes.decode('utf-8', 'replace')

    return page


def jobhandler() -> pd.DataFrame:
    """Uses html parser to extract job info from page source.
    
    Returns:
        pandas.DataFrame: Job details.
    ---
    """
    parser = JobParser()
    url = "https://duunitori.fi/tyopaikat/alue/jyvaskyla?order_by=date_posted"
    MAXPAGES = 30
    i=0
    while url:
        html_src = pagesource(url)
        parser.feed(html_src)
        url = parser.nextpage
        parser.nextpage = None

        i+=1
        if i < MAXPAGES:
            r = abs(random.gauss(mu=0, sigma=4))
            t = min(10, r)
            time.sleep(1 + t)
        else:
            url=None
            

    jobs = pd.DataFrame(parser.alljobs)
    parser.close()

    return jobs
    

if __name__ == "__main__":
    jobs = jobhandler()
    jobs.to_csv("jobs.csv", index=False)
    jobs = pd.read_csv("jobs.csv")
    # jobs = jobs.sort_values(by="category")
    print(jobs.head(10))
    print(f"\N{goat}")