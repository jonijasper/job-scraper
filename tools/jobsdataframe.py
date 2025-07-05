import pandas as pd
import re
import warnings
warnings.filterwarnings("ignore",
    "Pandas doesn't allow columns to be created via a new attribute name", 
    UserWarning)


class JobsDataFrame(pd.DataFrame):
    _INVALID_TITLE_REGEX = re.compile('[\\\\*?:/\\[\\]]')
    
    _COLS = ["posted", "title", "company", "url"]
    _BUZZCOL = "buzz"
    _CAT = "category"
    _COMP = "company"
    _SHEETCOL = "category"
    _FIRSTSHEET = "index"
    _BUZZMATCHCOL = "slug"
    _BUZZMARKERS = ('x', None)
    
    _BLACKLISTFILE = ".blacklist.dat"
    _BTITLEMARKER = '#'
    _BLACKBUZZ = "buzzwords"
    _BCAT = "categories"
    _BCOMP = "companies"

    def __init__(self, *args, **kwargs):
        pd.DataFrame.__init__(self, *args, **kwargs)
        self.last_refresh = None
        self.blacklist = {}
        self._blacklist_reader()
        if not self._BUZZCOL in self.columns:
            self._buzzer()

    def _blacklist_reader(self):
        with open(self._BLACKLISTFILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith(self._BTITLEMARKER):
                    name = line[1:]
                    self.blacklist[name] = set()
                elif line:
                    self.blacklist[name].add(line.lower())

    def _buzzer(self):
        # "-foo-" or "-bar-": contains('-foo-|-bar-')
        buzzwords = self.blacklist[self._BLACKBUZZ]
        pattern = '-' + '-|-'.join(buzzwords) + '-'
        mask = self[self._BUZZMATCHCOL].str.contains(pattern)
        tags = [self._BUZZMARKERS[0] if x else self._BUZZMARKERS[1] 
            for x in mask]
        self.insert(0,self._BUZZCOL,tags)

    def _get_mask(self):
        x = ~self[self._CAT].str.lower().isin(self.blacklist[self._BCAT])
        y = ~self[self._COMP].str.lower().isin(self.blacklist[self._BCOMP])
        mask = x & y
        return mask

    def spread(self, filename: str, filter: bool=True, *args, **kwargs):
        if filter:
            df = self[self._get_mask()]
        else:
            df = self

        filename = f"{self.last_refresh}_{filename}"
        categories = df[self._SHEETCOL].drop_duplicates().sort_values()

        with pd.ExcelWriter(filename, *args, **kwargs) as writer:
            # list categories on the first sheet
            categories.to_excel(writer,sheet_name=self._FIRSTSHEET, index=False)
            writer.sheets[self._FIRSTSHEET].autofit()

            # separate sheet for each category
            for cat in categories:
                sheetname = self._INVALID_TITLE_REGEX.sub(' ', cat)[:31]
                cat_df = df[df[self._SHEETCOL] == cat]
                if any(cat_df[self._BUZZCOL] == self._BUZZMARKERS[0]):
                    cols = [self._BUZZCOL, *self._COLS]
                else:
                    cols = self._COLS

                cat_df.to_excel(writer, sheet_name=sheetname, index=False,
                            columns=cols)
                writer.sheets[sheetname].autofit()

    @staticmethod
    def from_csv(path, *args,**kwargs):
        df = JobsDataFrame(pd.read_csv(path,*args,**kwargs))
        with open(path, 'r') as f:
            df.last_refresh = f.readline().strip().split(',')[-1]

        return df