from utils import response

import simplejson as json

import whoosh
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import exists_in, open_dir

branchSchema = Schema(colour=TEXT, icon=TEXT, description=TEXT(stored=True, analyzer=StemmingAnalyzer()), id=ID, summary=TEXT(stored=True, analyzer=StemmingAnalyzer()), slug=TEXT(stored=True), followers=NUMERIC, totalPosts=NUMERIC, tags=KEYWORD(stored=True), createdAt=NUMERIC(stored=True), label=TEXT(stored=True, analyzer=StemmingAnalyzer()))
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

    def searchTC(self, event, context):
        print(event['body'])
        # print(type(event['body']))
        bodyContents = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        if 'entity' not in bodyContents or 'search' not in bodyContents:
            print("Missing required parameters in the request body.")
            return self.response.standard({"success": False, "message": "Missing required parameters: entity, search"}, "error")
        if bodyContents["entity"] not in ["post", "userprofile", "branch"]:
            return self.response.standard({"success": False, "message": "Invalid entity type. Acceptable entries are 'post', 'userprofile', or 'branch'."}, "error")
        self.entity = bodyContents["entity"]
        self.search_term = bodyContents["search"]
        return self.runQuery()

    def runQuery(self):
        entityFunction = f"search_{self.entity}"
        func = getattr(self, entityFunction, None)
        if func is None:
            raise AttributeError("No such function exists - please check list of acceptable entries in the help section")
        return func()
    
    def search_branch(self):
        from whoosh.qparser import QueryParser
        myindex = whoosh.index.open_dir("/mnt/efs/tcwhooshdatabranchs")
        qp = QueryParser('description', schema=branchSchema)
        q = qp.parse(self.search_term)
        with myindex.searcher() as s:
            try:
                results = s.search(q, limit=None)
                return self.response.standard({"success": True, "results": self.filterResults(results, 'description')}, "success")
                # return self.filterResults(results, 'description')  # Convert results to a list of dictionaries
            except Exception as e:
                print(f"Error during search: {e}")
                return self.response.standard({"success": False, "message": str(e)}, "error")

    def search_post(self):
        from whoosh.qparser import QueryParser
        myindex = whoosh.index.open_dir("/mnt/efs/tcwhooshdataposts")
        qp = QueryParser('postText', schema=postSchema)
        q = qp.parse(self.search_term)
        with myindex.searcher() as s:
            try:
                results = s.search(q, limit=None)
                print(f"Search results for '{q}': {len(results)} found.")
                return self.response.standard({"success": True, "results": self.filterResults(results, 'postText')}, "success")
            except Exception as e:
                print(f"Error during search: {e}")
                return self.response.standard({"success": False, "message": str(e)}, "error")

    # 13/6/25 (Fin) - I'm bored on a train this entire function is 💅whatever💅
    def search_userprofile(self):
        from whoosh.qparser import QueryParser
        myindex = whoosh.index.open_dir("/mnt/efs/tcwhooshdatauserprofiles")
        userprofileFields = ['name', 'userBio']
        resultsToReturn = {}
        for field in userprofileFields:
            query = QueryParser(field, schema=userprofileSchema)
            question = query.parse(self.search_term)
            with myindex.searcher() as s:
                try:
                    results = s.search(question)
                    resultsToReturn[field] = self.filterResults(results, field)
                except Exception as e:
                    print(f"Error during search: {e}")
                    return self.response.standard({"success": False, "message": str(e)}, "error")
        return self.response.standard({"success": True, "results": resultsToReturn}, "success")

    def filterResults(self, results, field):
        allResults = [dict(result) for result in results]
        exactMatches = [x for x in allResults if self.search_term.lower() in x[field].lower()]
        partialMatches = [x for x in allResults if x not in exactMatches]
        return {
            "exactMatches": exactMatches,
            "partialMatches": partialMatches,
            "totalResultCount": len(results),
        }

searching = SearchTC()

def lookup(event, context):
    print(event)
    return searching.searchTC(event, context)

# def alphabranch(event, context):
#     print(event)
#     return searching.searchTC(event, context)

if __name__ == "__main__":
    event = {}
    context = {}
    print(lookup(event, context))