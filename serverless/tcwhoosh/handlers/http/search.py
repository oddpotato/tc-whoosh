from utils import response
import os

import simplejson as json

import whoosh
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import exists_in, open_dir

postSchema = Schema(postText=TEXT(stored=True, analyzer=StemmingAnalyzer()), 
                                 slug=ID(stored=True), author=TEXT(stored=True), authorSlug=TEXT(stored=True), 
                                 createdAt=NUMERIC(stored=True), parentslug=ID(stored=True), parentName=TEXT(stored=True))
userprofileSchema = Schema(name=TEXT(stored=True), userBio=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                                 userlanguage=TEXT, userSlug=TEXT(stored=True, phrase=False),
                                 userCoverPic=ID, userProfilePic=ID, createdAt=NUMERIC(stored=True), trustLevel=TEXT(stored=True))

class SearchTC:
    def __init__(self):
        self.response = response.Response()
        self.entity = None
        self.search_term = None
        self.search_field = None

    def searchTC(self, event, context):
        print(event['body'])
        print(type(event['body']))
        bodyContents = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        if 'entity' not in bodyContents or 'search' not in bodyContents or 'field' not in bodyContents:
            print("Missing required parameters in the request body.")
            return self.response.standard({"success": False, "message": "Missing required parameters: entity, search, field"}, "error")
        if bodyContents["entity"] not in ["post", "userprofile"]:
            return self.response.standard({"success": False, "message": "Invalid entity type. Acceptable entries are 'post' or 'userprofile'."}, "error")
        self.entity = bodyContents["entity"]
        self.search_term = bodyContents["search"]
        self.search_field = bodyContents["field"]
        return self.runQuery()

    def runQuery(self):
        print(os.listdir("/mnt/efs"))
        entityFunction = f"search_{self.entity}"
        func = getattr(self, entityFunction, None)
        if func is None:
            raise AttributeError("No such function exists - please check list of acceptable entries in the help section")
        return func()
    
    def search_post(self):
        from whoosh.qparser import QueryParser
        myindex = whoosh.index.open_dir("/mnt/efs/tcwhooshdataposts")
        qp = QueryParser('postText', schema=postSchema)
        q = qp.parse(self.search_term)
        with myindex.searcher() as s:
            try:
                results = s.search(q)
                print(f"Search results for '{q}': {len(results)} found.")
                return self.response.standard({"success": True, "results": [dict(result) for result in results]}, "success")
            except Exception as e:
                print(f"Error during search: {e}")
                return self.response.standard({"success": False, "message": str(e)}, "error")

    def search_userprofile(self):
        from whoosh.qparser import QueryParser
        myindex = whoosh.index.open_dir("/mnt/efs/tcwhooshdatauserprofiles")
        qp = QueryParser(self.search_field, schema=userprofileSchema)
        q = qp.parse(self.search_term)
        with myindex.searcher() as s:
            try:
                results = s.search(q)
                print(f"Search results for '{q}': {len(results)} found.")
                return self.response.standard({"success": True, "results": [dict(result) for result in results]}, "success")
            except Exception as e:
                print(f"Error during search: {e}")
                return self.response.standard({"success": False, "message": str(e)}, "error")

searching = SearchTC()

def lookup(event, context):
    print(event)
    return searching.searchTC(event, context)

if __name__ == "__main__":
    event = {}
    context = {}
    print(lookup(event, context))