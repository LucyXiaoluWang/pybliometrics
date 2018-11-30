import hashlib
from collections import namedtuple
from os.path import join

from scopus import config
from scopus.classes import Search


class AffiliationSearch(Search):
    @property
    def affiliations(self):
        """A list of namedtuples storing affiliation information,
        where each namedtuple corresponds to one affiliation.
        The information in each namedtuple is (eid name variant documents city
        country parent).

        All entries are strings or None.  variant combines variants of names
        with a semicolon.
        """
        out = []
        order = 'eid name variant documents city country parent'
        aff = namedtuple('Affiliation', order)
        for item in self._json:
            name = item.get('affiliation-name')
            variants = [d.get('$', "") for d in item.get('name-variant', [])
                        if d.get('$', "") != name]
            new = aff(eid=item['eid'],
                      name=name,
                      variant=";".join(variants),
                      documents=item.get('document-count', '0'),
                      city=item.get('city'),
                      country=item.get('country'),
                      parent=item.get('parent-affiliation-id'))
            out.append(new)
        return out

    def __init__(self, query, count=200, start=0,
                 max_entries=5000, refresh=False):
        """Class to perform a search for an affiliation.

        Parameters
        ----------
        query : str
            A string of the query, e.g. "af-id(60021784)".

        count : int (optional, default=200)
            The number of entries to be displayed at once.  A smaller number
            means more queries with each query having less results.

        start : int (optional, default=0)
            The entry number of the first search item to start with.

        refresh : bool (optional, default=False)
            Whether to refresh the cached file if it exists or not.

        max_entries : int (optional, default=5000)
            Raise error when the number of results is beyond this number.
            The Scopus Search Engine does not allow more than 5000 entries.

        Raises
        ------
        ScopusQueryError
            If the number of search results exceeds max_entries.

        Notes
        -----
        Json results are cached in ~/.scopus/affiliation_search/{fname}, where
        fname is the hashed version of query.

        The results are stored as a property named authors.
        """

        self.query = query
        qfile = join(config.get('Directories', 'AffiliationSearch'),
                     hashlib.md5(query.encode('utf8')).hexdigest())
        url = 'https://api.elsevier.com/content/search/affiliation'
        Search.__init__(self, query, qfile, url, refresh, count, start,
                        max_entries)

    def __str__(self):
        s = """{query}
        Resulted in {N} hits.
    {entries}"""
        return s.format(query=self.query, N=len(self._json),
                        entries='\n    '.join([str(a) for a in self._json]))
