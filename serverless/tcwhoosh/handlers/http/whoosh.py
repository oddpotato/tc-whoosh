from utils import response

class Whoosh:
    def __init__(self):
        self.response = response.Response()

    def search(self, event, context):
        return self.response.standard({"success": True, "message": "Go Serverless v4.0! Your function executed successfully!"}, "success")


searching = Whoosh()

def lookup(event, context):
    return searching.search(event, context)

if __name__ == "__main__":
    event = {}
    context = {}
    print(lookup(event, context))