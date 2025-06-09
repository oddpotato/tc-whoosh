
import whoosh
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import create_in, exists_in, open_dir

postSchema = Schema(postText=TEXT(stored=True, analyzer=StemmingAnalyzer()), 
                                 slug=ID(stored=True), author=TEXT(stored=True), authorSlug=TEXT(stored=True), 
                                 createdAt=NUMERIC(stored=True), parentslug=ID(stored=True), parentName=TEXT(stored=True))
userprofileSchema = Schema(name=TEXT(stored=True), userBio=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                                 userlanguage=TEXT, userSlug=TEXT(stored=True, phrase=False),
                                 userCoverPic=ID, userProfilePic=ID, createdAt=NUMERIC(stored=True), trustLevel=TEXT(stored=True))

from dataclasses import dataclass
import argparse

@dataclass
class SearchEngine:

    entity: str
    search_term: str
    search_field: str

    def runQuery(self):
        entityFunction = f"search_{self.entity}"
        func = getattr(self, entityFunction, None)
        if func is None:
            raise AttributeError("No such function exists - please check list of acceptable entries in the help section")
        return func()
    
    def search_post(self):
        from whoosh.qparser import QueryParser
        myindex = whoosh.index.open_dir("tcwhooshdataposts")
        qp = QueryParser(self.search_field, schema=postSchema)

        q = qp.parse(self.search_term)
        with myindex.searcher() as s:
            results = s.search(q)
            print(f"Search results for '{q}': {len(results)} found.")
            return [dict(result) for result in results]  # Convert results to a list of dictionaries

    def search_userprofile(self):
        from whoosh.qparser import QueryParser
        myindex = whoosh.index.open_dir("tcwhooshdatauserprofiles")
        qp = QueryParser(self.search_field, schema=userprofileSchema)

        q = qp.parse(self.search_term)
        with myindex.searcher() as s:
            results = s.search(q)
            print(f"Search results for '{q}': {len(results)} found.")
            return [dict(result) for result in results]

def main(entity: str, search: str, field: str):
    search_engine = SearchEngine(entity, search, field)
    results = search_engine.runQuery()
    if results:
        for result in results:
            print(result)
    else:
        print("No results found.")
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Whoosh Search")
    parser.add_argument('-e', '--entity', 
                        type=str, choices=['post', 'userprofile'], required=True, help='Entity to index (post or userprofile)')
    parser.add_argument('-s', '--search', 
                        type=str, default='A wild ñ', 
                        help='Search term to query the index')
    parser.add_argument('-f', '--field', 
                        type=str, default='postText', 
                        help='Field to search in (default: postText)')
    args = parser.parse_args()
    print(args)
    main(args.entity, args.search, args.field)
