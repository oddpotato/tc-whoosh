from utils import response

class GoodbyeWorld:
    def __init__(self):
        self.response = response.Response()

    def goodbye(self, event, context):
        return self.response.standard({"success": True, "message": "Well this one worked just fine. Go Serverless v4.0! Your function executed successfully!"}, "success")


sayGoodbye = GoodbyeWorld()

def goodbye(event, context):
    return sayGoodbye.goodbye(event, context)

if __name__ == "__main__":
    event = {}
    context = {}
    print(goodbye(event, context))