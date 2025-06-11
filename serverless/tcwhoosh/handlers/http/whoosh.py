from utils import response


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

class Whoosh:
    def __init__(self):
        self.response = response.Response()
        self.entity = None
        self.search_term = None
        self.search_field = None

    def search(self, event, context):
        if not event.get("entity") or not event.get("search") or not event.get("field"):
            return self.response.standard({"success": False, "message": "Missing required parameters: entity, search, field"}, "error")
        if event["entity"] not in ["post", "userprofile"]:
            return self.response.standard({"success": False, "message": "Invalid entity type. Acceptable entries are 'post' or 'userprofile'."}, "error")
        self.entity = event["entity"]
        self.search_term = event["search"]
        self.search_field = event["field"]
        return self.runQuery()

    def runQuery(self):
        entityFunction = f"search_{self.entity}"
        func = getattr(self, entityFunction, None)
        if func is None:
            raise AttributeError("No such function exists - please check list of acceptable entries in the help section")
        return func()
    
    def search_post(self):
        from whoosh.qparser import QueryParser
        myindex = whoosh.index.open_dir("mtn/fs1/tcwhooshdataposts")
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
        myindex = whoosh.index.open_dir("/mtn/fs1/tcwhooshdatauserprofiles")
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

searching = Whoosh()

def lookup(event, context):
    return searching.search(event, context)

if __name__ == "__main__":
    event = {}
    context = {}
    print(lookup(event, context))