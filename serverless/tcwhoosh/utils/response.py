import simplejson as json

class Response:

    def standard(self, message, response):
        response = {
            'statusCode': self.get_status_code(response),
            'body': "",
            'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
            },
        }
        try:
            response['body'] = json.dumps(message)
        except:
            raise Exception('Decoding JSON has failed, response contents: ', message)
        return response

    def get_status_code(self, value):
        match value:
            case "success":
                return 200
            case "nocontent":
                return 204
            case "invalid":
                return 400
            case "unauthorized":
                return 401
            case "forbidden":
                return 403
            case "notfound":
                return 404
            case "conflict":
                return 409
            case "error":
                return 500
            case _:
                return 500