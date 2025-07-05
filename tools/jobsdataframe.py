import pandas as pd
import re
import warnings
warnings.filterwarnings("ignore",
    "Pandas doesn't allow columns to be created via a new attribute name", 
    UserWarning)


class JobsDataFrame(pd.DataFrame):
    _INVALID_TITLE_REGEX = re.compile('[\\\\*?:/\\[\\]]')
    _BLACKLISTFILE = ".blacklist.dat"

    def __init__(self, *args, **kwargs):
        pd.DataFrame.__init__(self, *args, **kwargs)
        self.last_refresh = None
        self.blacklist = {}
        self._blacklist_reader()
        if not "buzz" in self.columns:
            self._buzz()

    def _blacklist_reader(self):
        with open(self._BLACKLISTFILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    name = line[1:]
                    self.blacklist[name] = set()
                elif line:
                    self.blacklist[name].add(line.lower())

    def _buzz(self):
        # " foo " or " bar ": contains(' foo | bar ')
        pattern = ' ' + ' | '.join(self.blacklist["buzzwords"]) + ' '
        mask = self["title"].str.contains(pattern)
        tags = ['x' if x else None for x in mask]
        self.insert(0,"buzz",tags)

    def _get_mask(self):
        x = ~self["category"].str.lower().isin(self.blacklist["categories"])
        y = ~self["company"].str.lower().isin(self.blacklist["companies"])
        mask = x & y
        return mask

    def spread(self, filename: str, filter: bool=True, *args, **kwargs):
        if filter:
            df = self[self._get_mask()]
        else:
            df = self

        filename = f"{self.last_refresh}_{filename}"
        categories = df["category"].drop_duplicates().sort_values()

        with pd.ExcelWriter(filename, *args, **kwargs) as writer:
            # list categories on the first sheet
            categories.to_excel(writer,sheet_name="categories", index=False)
            writer.sheets["categories"].autofit()

            # separate sheet for each category
            for cat in categories:
                sheetname = self._INVALID_TITLE_REGEX.sub(' ', cat)[:31]
                cat_df = df[df["category"] == cat]
                if any(cat_df.buzz == 'x'):
                    cols = ["buzz","title","company","url"]
                else:
                    cols = ["title","company","url"]

                cat_df.sort_values("title")
                cat_df.to_excel(writer, sheet_name=sheetname, index=False,
                            columns=cols)
                writer.sheets[sheetname].autofit()

    @staticmethod
    def from_csv(path, *args,**kwargs):
        df = JobsDataFrame(pd.read_csv(path,*args,**kwargs))
        with open(path, 'r') as f:
            df.last_refresh = f.readline().strip().split(',')[-1]

        return df