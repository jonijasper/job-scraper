# jobparser.py 
from html.parser import HTMLParser


class JobParser(HTMLParser):
    # for matching and translating attribute names
    JOBINFO = { "data-job-slug": "title",
                "data-category": "category", 
                "data-company": "company", 
                "href": "url"}
    # for matching relevant tags and attributes
    JOB_TAG = "a"
    JOB_ATTR = ("class", "job-box__hover gtm-search-result")
    NEXT_TAG = "link"
    NEXT_ATTR = ("rel", "next")
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.alljobs = {value: [] for value in self.JOBINFO.values()}
        self.nextpage = None

    def reset_(self):
        self.alljobs = {value: [] for value in self.JOBINFO.values()}
        self.nextpage = None

    def handle_starttag(self, tag, attrs):
        # tags containing job information
        if tag == self.JOB_TAG and self.JOB_ATTR in attrs:
            job = {key: "" for key in self.alljobs.keys()}
            # specs are in tag attributes:
            for attr,value in attrs:
                if attr in self.JOBINFO:
                    job[self.JOBINFO[attr]] = value
            
            # data-job-slug="job-title-foobar-12345"
            title = job["title"].split('-')
            job["title"] = " ".join(title[:-2])

            # href="/tyopaikat/tyo/...."
            job["url"] = "https://duunitori.fi" + job["url"]

            # add job to list
            for key,value in job.items():
                self.alljobs[key].append(value)

        # tag containing link to the next page
        elif tag == self.NEXT_TAG and self.NEXT_ATTR in attrs:
            for attr,value in attrs:
                if attr == "href":
                    self.nextpage = value
