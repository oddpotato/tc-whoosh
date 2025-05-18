from utils import response

class HelloWorld:
    def __init__(self):
        self.response = response.Response()

    def hello(self, event, context):
        return self.response.standard({"success": True, "message": "Go Serverless v4.0! Your function executed successfully!"}, "success")


sayHello = HelloWorld()

def hello(event, context):
    return sayHello.hello(event, context)

if __name__ == "__main__":
    event = {}
    context = {}
    print(hello(event, context))