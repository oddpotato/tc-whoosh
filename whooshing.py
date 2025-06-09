import simplejson as json

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer

import argparse

with open("./data/posts.json", "r", encoding='utf-8') as f:
    data = json.load(f)

with open ("./data/userprofiles.json", "r") as g:
    userprofileData = json.load(g)

class CreateTCWhooshData:
    def __init__(self, entity):
        # It's not a class if it doesn't start with boop
        self.boop = "boop"
        self.entity = entity
        # Data and schema
        self.postData = data
        self.userprofileData = userprofileData
        self.postSchema = Schema(postText=TEXT(stored=True, analyzer=StemmingAnalyzer()), 
                                 slug=ID(stored=True), author=TEXT(stored=True), authorSlug=TEXT(stored=True), 
                                 createdAt=NUMERIC(stored=True), parentslug=ID(stored=True), parentName=TEXT(stored=True))
        self.userprofileSchema = Schema(name=TEXT(stored=True), userBio=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                                 userlanguage=TEXT, userSlug=TEXT(stored=True, phrase=False),
                                 userCoverPic=ID, userProfilePic=ID, createdAt=NUMERIC(stored=True), trustLevel=TEXT(stored=True))
        # Let's fire this bb up!
        self.binaryData = ""

    def setSchemaAndBindaryData(self):
        fullentityName = f"{self.entity}Schema"
        schemaToUse = getattr(self, fullentityName)
        setattr(self, 'binaryData', create_in(f"tcwhooshdata{self.entity}s", schemaToUse))

    def findFunction(self):
        entityFunction = f"create_index_{self.entity}"
        func = getattr(self, entityFunction, None)
        if func is None:
            raise AttributeError("No such function exists - please check list of acceptable entries in the README")
        try:
            print(f"Running function: {entityFunction}")
            return func()
        # Type Errors were popping up left and right when I was working with ASCII and Unicode so fuck that.
        except TypeError as e:
            print(f"TypeError: {e}. Please check the function parameters for {entityFunction}.")
            raise e
        except Exception as e:
            print(f"An error occurred while running {entityFunction}: {e}")
            raise e

    def create_index_post(self):
        # Create an index in the directory "tcwhooshdata" with the schema defined above
        writer = self.binaryData.writer()
        for post in self.postData:
            # Add each post to the index
            writer.add_document(
                postText=post["postText"],
                slug=post["slug"],
                author=post["author"],
                authorSlug=post["authorSlug"],
                createdAt=post["createdAt"] / 1000,
                parentslug=post['parentslug'],
                parentName=post['parentName']
            )
        writer.commit() 
        print("Index created successfully in tcwhooshdata directory")

    def create_index_userprofile(self):
        # Create an index in the directory "tcwhooshdata" with the schema defined above
        writer = self.binaryData.writer()
        for userprofile in self.userprofileData:
            # Add each post to the index
            writer.add_document(
                createdAt=userprofile["createdAt"] / 1000,
                name=userprofile["name"],
                trustLevel=userprofile["trustLevel"],
                userBio=userprofile["userBio"],
                userlanguage=userprofile["userlanguage"],
                userSlug=userprofile["userSlug"],
                userCoverPic=userprofile["userCoverPic"],
                userProfilePic=userprofile["userProfilePic"]
            )
        writer.commit() 
        print("Index created successfully in tcwhooshdata directory")

    def search_index(self, field: str, query: str):
        from whoosh.qparser import QueryParser
        with self.binaryData.searcher() as searcher:
            # query = QueryParser("postText", self.binaryData.schema).parse(query)
            query = QueryParser(field, self.binaryData.schema).parse(query)
            results = searcher.search(query)
            result = results if len(results) > 0 else None
            if result:
                for item in results:
                    print("Found result:")
                    print("Post Text:", item[field])
            else:
                print("No results found for the query:", query)

def main(entity: str, search: str, field: str):
    whoosh_data = CreateTCWhooshData(entity)
    whoosh_data.setSchemaAndBindaryData()
    whoosh_data.findFunction()
    print(f"Searching for term: {search} in field: {field}")
    whoosh_data.search_index(field, search)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Whoosh Indexing and Searching")
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
    