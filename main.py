# main.py
# v0.1
"""
Find, filter and organize open job positions
"""
import datetime
from pandas.errors import EmptyDataError
import random
import sys
import time
import urllib.error
import urllib.request

from options import *
from tools.jobparser import JobParser
from tools.jobsdataframe import JobsDataFrame
try:
    from tools.httperrcodes import HTTP_ERROR_CODES
except ImportError:
    HTTP_ERROR_CODES = None


def xprint(msg: str, level: str="INFO", *, logfile: str=None, **kwargs):
    """Autoformat `info`,`warning`,`error`, etc. messages.

    Parameters
    ----------
    msg : A string containing the message.
    level : Prefix for the message. Defaults to "INFO".
    logfile : `Path` to a writeable file. If provided, the message is also 
        written to the file.
    **kwargs
        Additional keyword arguments. Passed to `print`.

    .. note:: INFO -level (default) messages are directed to `stdout`, 
        others to `stderr`.

    Examples
    --------

        >>> xprint("foobar")
        *** INFO: foobar    # to stdout
        
        >>> xprint("foobar", "WARNING")
        *** WARNING: foobar     # to stderr
    ---
    """
    if level == "INFO":
        stream = sys.stdout
    else:
        stream = sys.stderr

    fmsg = f"*** {level}: {msg}"
    print(fmsg, file=stream, **kwargs)

    if logfile:
        with open(logfile, 'a') as f:
            f.write(fmsg + "\n")

def pagesource(url: str) -> str:
    """Read page source from url

    Parameters
    ----------
    url : Page url as string.

    Returns
    -------
    `str`
        A string containing the page source code, or empty string, if the
        page could not be reached.

    Examples
    --------

        >>> html_src = pagesource("https://quotes.toscrape.com/")
        >>> print(html_src[:100])
        <!DOCTYPE html>
        <html lang="en">
        <head>
                <meta charset="UTF-8">
                <title>Quotes to Scrape</title>
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

def search_jobs(maxpages: int, oldjobs=None):
    """Uses html parser `tools.jobparser.JobParser` to extract job info from 
    page source and saves the results to csv-file specified on `options.CSVFILE`.

    Parameters
    ----------
    maxpages : restrict the number of pages to search
    oldjobs : `DataFrame` containing previously listed jobs

    .. note:: 
        Also uses parameters set in `options`:
        - `options.CSVFILE`
        - `options.DATETIME_FORMAT`
        - `options.CSVCOMMENT`
        - `options.IDCOLUMN`

    ---
    """
    utime = datetime.datetime.now()
    updated = utime.strftime(DATETIME_FORMAT)
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
        if oldjobs is not None:
            isnew = ~jobs[IDCOLUMN].str.lower().isin(oldjobs[IDCOLUMN])
            jobs = jobs[isnew]

        if jobs.empty:
            xprint(f"Now new jobs.")
            break
        else:
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
    if oldjobs is not None:
        oldjobs.to_csv(CSVFILE, mode='a', index=False, header=(i==0))

    return (i != 0)
    

def get_jobs(path, refresh: bool=False, maxpages: int=30, *args, **kwargs):
    """Reads joblistings from csv and makes a spreadsheet.
    
    Parameters
    ----------
    refresh : If `True` checks for new jobs
    maxpages : Restrict the number of pages to search
    *args
        Additional arguments passed to `tools.jobsdataframe.JobsDataFrame.from_csv`
    **kwargs
        Additional keyword arguments passed to `tools.jobsdataframe.JobsDataFrame.from_csv`
    ---
    """
    try:
        oldjobs = JobsDataFrame.from_csv(path, *args, comment=CSVCOMMENT, **kwargs)
    except EmptyDataError:
        oldjobs = None

    if refresh:
        newjobs = search_jobs(maxpages, oldjobs)
        jobs = JobsDataFrame.from_csv(path, *args, comment=CSVCOMMENT, **kwargs)
        if newjobs:
            jobs.spread(XLSXFILE)

    else:
        if oldjobs is not None:
            jobs = oldjobs
        else:
            xprint("All jobs are gone. Try setting REFRESH=True", level="WARNING") 
            return   

    return jobs


if __name__ == "__main__":
    newjobs = get_jobs(CSVFILE, refresh=REFRESH)

