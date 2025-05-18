import simplejson as json

from whoosh.index import create_in
from whoosh.fields import *

with open("./data/posts.json", "r") as f:
    data = json.load(f)

class CreateTCWhooshData:
    def __init__(self, entity):
        # It's not a class if it doesn't start with boop
        self.boop = "boop"
        self.entity = entity
        # Data and schema
        self.postData = data
        self.postSchema = Schema(postText=TEXT(stored=True), 
                                 slug=ID(stored=True), author=TEXT(stored=True), authorSlug=TEXT(stored=True), 
                                 createdAt=NUMERIC(stored=True), parentslug=ID(stored=True), parentName=TEXT(stored=True))
        # Let's fire this bb up!
        self.binaryData = create_in(f"tcwhooshdata{entity}", self.postSchema)

    def findFunction(self):
        print("Boop")
        entityFunction = f"create_index_{self.entity}"
        func = getattr(self, entityFunction, None)
        if func is None:
            raise AttributeError("No such function exists - please check list of acceptable entries in the README")
        return func()

    def findParent(self, post):
        if 'maintrunk' in post:
            return [{
                "slug": post["maintrunk"]["slug"],
                "name": post["maintrunk"]["name"]
            }]
        if 'userprofile' in post:
            return [{
                "slug": post["userprofile"]["slug"],
                "name": post["userprofile"]["name"]
            }]
        if 'subwiki' in post:
            return [{
                "slug": post["subwiki"]["slug"],
                "name": post["subwiki"]["name"]
            }]
        raise ValueError("No parent found for post")

    def create_index_posts(self):
        # Create an index in the directory "tcwhooshdata" with the schema defined above
        writer = self.binaryData.writer()
        for post in self.postData:
            # Add each post to the index
            parentData = self.findParent(post['data'])
            writer.add_document(
                postText=post["postText"],
                slug=post["slug"],
                author=post["authors"][0]['name'],
                authorSlug=post["authors"][0]['slug'],
                createdAt=post["createdAt"] / 1000,
                parentslug=parentData[0]['slug'],
                parentName=parentData[0]['name']
            )
        writer.commit() 
        print("Index created successfully in tcwhooshdata directory")

    def search_index(self, query):
        from whoosh.qparser import QueryParser
        with self.binaryData.searcher() as searcher:
            query = QueryParser("postText", self.binaryData.schema).parse(query)
            results = searcher.search(query)
            print(results[0])

if __name__ == "__main__":
    whoosh_data = CreateTCWhooshData('posts')
    whoosh_data.findFunction()
    whoosh_data.search_index("third")

# >>> schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
# >>> ix = create_in("indexdir", schema)
# >>> writer = ix.writer()
# >>> writer.add_document(title=u"First document", path=u"/a",
                # content=u"This is the first document we've added!")
# >>> writer.add_document(title=u"Second document", path=u"/b",
                # content=u"The second one is even more interesting!")
# >>> writer.commit()
# >>> from whoosh.qparser import QueryParser
# >>> with ix.searcher() as searcher:
# query = QueryParser("content", ix.schema).parse("first")
# results = searcher.search(query)
# results[0]