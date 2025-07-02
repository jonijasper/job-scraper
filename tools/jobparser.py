# jobparser.py 
from html.parser import HTMLParser


class JobParser(HTMLParser):
    # for matching and translating attribute names
    JOBINFO = { "data-job-slug": "title",
                "data-category": "category", 
                "data-company": "company", 
                "href": "url"}
    JOB_TAG = "a"
    JOB_ATTR = ("class", "job-box__hover gtm-search-result")
    NEXT_TAG = "link"
    NEXT_ATTR = ("rel", "next")
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.alljobs = {"title": [], "category": [], "company": [], "url": []}
        self.nextpage = None

    def handle_starttag(self, tag, attrs):
        if tag == self.JOB_TAG and self.JOB_ATTR in attrs:
            # found job tag
            job = {"title": "", "category": "", "company": "", "url": ""}
            # specs are in tag attributes:
            for attr,value in attrs:
                if attr in self.JOBINFO:
                    job[self.JOBINFO[attr]] = value
            
            # data-job-slug="job-title-foobar-12345"
            title = job["title"].split('-')
            job["title"] = " ".join(title[:-2])

            for key,value in job.items():
                self.alljobs[key].append(value)

        if tag == self.NEXT_TAG and self.NEXT_ATTR in attrs:
            # tag has link to the next page in "href" attribute
            for attr,value in attrs:
                if attr == "href":
                    self.nextpage = value
