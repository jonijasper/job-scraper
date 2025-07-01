import pandas as pd

def _demo(x: list = [0,1,]):
    if 0 in x:
        URL = "https://quotes.toscrape.com/"

    if 1 in x:
        foo = {"a":[1,2,3], "b":["foo","bar","asd"]}
        bar = pd.DataFrame(foo)
        print(bar)

def uusimmat_jkl():
    URL = "https://duunitori.fi/tyopaikat/alue/jyvaskyla?order_by=date_posted"

def pagesource(url: str) -> str:
    """Read page source from url

    Args:
        url (str): Page url as string.

    Returns:
        str: A string containing the page source code.

    Example:
        >>> pagesource("https://quotes.toscrape.com/")
    ---
    """
    return ""

def jobinfo(html_src: str) -> list[dict]:
    """Uses html parser to extract job info from page source.
    
    Args:
        html_src (str): Html code to parse.
    
    Returns:
        list: A list of dictionaries containing job information.
    ---
    """
    return []

def jobhandler(jobs: list[dict]) -> pd.DataFrame:
    """Organizes job listings.
    
    Args:
        jobs (list): A list of dictionaries containig job information.
    
    Returns:
        pandas.DataFrame: Table of job listings.
    ---
    """


if __name__ == "__main__":
    _demo()
    print(f"\N{goat}")