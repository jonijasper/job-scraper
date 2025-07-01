from html.parser import HTMLParser

class JobParser(HTMLParser):
    # data-job-slug="job-title-foobar-12345"
    JOBINFO = { "data-job-slug": "title",
                "data-category": "category", 
                "data-company": "company", 
                "href": "link"}
    JOB_TAG = "a"
    JOB_ATTR = ("class", "job-box__hover gtm-search-result")
    NEXT_TAG = "link"
    NEXT_ATTR = ("rel", "next")
    

    def __init__(self):
        HTMLParser.__init__(self)
        self.jobs = []

    def handle_starttag(self, tag, attrs):
        pass

    def get_jobs(self):
        return self.jobs