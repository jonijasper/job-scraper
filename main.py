import datetime
import pandas as pd
import sys
import urllib.error
import urllib.request

def _demo(x: list=[0, ]):
    if 0 in x:
        URL = "https://quotes.toscrape.com/"
        page = pagesource(URL)
        print(page.splitlines()[:5])

    if 1 in x:
        foo = {"a":[1,2,3], "b":["foo","bar","asd"]}
        bar = pd.DataFrame(foo)
        print(bar)

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
    print(fancy, file=stream)

    if logfile:
        with open(logfile, 'a') as f:
            f.write(msg + "\n")

def uusimmat_jkl():
    URL = "https://duunitori.fi/tyopaikat/alue/jyvaskyla?order_by=date_posted"

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


def jobinfo(html_src: str) -> list[dict]:
    """Uses html parser to extract job info from page source.
    
    Args:
        html_src: Html code to parse.
    
    Returns:
        list: A list of dictionaries containing job information.
    ---
    """
    return []

def jobhandler(jobs: list[dict]) -> pd.DataFrame:
    """Organizes job listings.
    
    Args:
        jobs: A list of dictionaries containig job information.
    
    Returns:
        pandas.DataFrame: Table of job listings.
    ---
    """


if __name__ == "__main__":
    _demo()
    print(f"\N{goat}")