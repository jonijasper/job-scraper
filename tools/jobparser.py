# jobparser.py 
from html.parser import HTMLParser


class JobParser(HTMLParser):
    # for matching and translating attribute names
    JOBINFO = { "a": "posted",
                "b": "title",
                "data-category": "category", 
                "data-company": "company", 
                "href": "url",
                "data-job-slug": "slug"
}
    # for matching relevant tags and attributes
    JOB_ATTR = {"a": ("class", "job-box__hover gtm-search-result")}
    TITLE_ATTR = {"h3": ("class", "job-box__title")}
    DATE_ATTR = {"span": ("class", "job-box__job-posted")}
    NEXT_ATTR = {"link": ("rel", "next")}
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.alljobs = {value: [] for value in self.JOBINFO.values()}
        self.nextpage = None
        self.currentjob = None
        self.titleopen = False
        self.dateopen = False

    def _jobdone(self):
        # add job to list
        for key,value in self.currentjob.items():
            self.alljobs[key].append(value)
        self.titleopen = False
        self.dateopen = False
        self.currentjob = None

    def reset_(self):
        self.alljobs = {value: [] for value in self.JOBINFO.values()}
        self.nextpage = None

    def handle_starttag(self, tag, attrs):
        # tags containing job information
        if tag in self.JOB_ATTR and self.JOB_ATTR[tag] in attrs:
            if self.currentjob:
                self._jobdone()

            self.currentjob = {key: "" for key in self.alljobs.keys()}
            # specs are in tag attributes:
            for attr,value in attrs:
                if attr in self.JOBINFO:
                    self.currentjob[self.JOBINFO[attr]] = value

            # href="/tyopaikat/tyo/...."
            self.currentjob["url"] = "https://duunitori.fi" + self.currentjob["url"]

        elif self.currentjob:
            if tag in self.TITLE_ATTR and self.TITLE_ATTR[tag] in attrs:
                self.titleopen = True

            elif tag in self.DATE_ATTR and self.DATE_ATTR[tag] in attrs:
                self.dateopen = True

        # tag containing link to the next page
        elif tag in self.NEXT_ATTR and self.NEXT_ATTR[tag] in attrs:
            if self.currentjob:
                self._jobdone()

            for attr,value in attrs:
                if attr == "href":
                    self.nextpage = value
                    return

    def handle_data(self, data):
        if self.currentjob:
            if self.titleopen:
                self.currentjob["title"] = data
                self.titleopen = False
                
            elif self.dateopen:
                self.currentjob["posted"] = data.split()[-1]
                self.dateopen = False

                self._jobdone()

