import requests
import simplejson as json

def searchTC(entity, field, search):
    url = "https://b569se0rc3.execute-api.us-east-1.amazonaws.com/alpha/search"
    headers = {
        'Content-Type': 'application/json',
    }
    body={
        'search': search,
        'field': field,
        'entity': entity
    }
    response = requests.post(url, data=json.dumps(body), headers=headers)
    if response.status_code == 200:
        print(f"Search successful for {entity} with term '{search}' in field '{field}'.")
        fullresponse = response.json()
        if 'entity' == 'post':
            print([key for key, value in fullresponse.items()])
            print(f"Response: {fullresponse}")
            print(f"Exact Matches: {len(fullresponse['results']['exactMatches'])}, Partial Matches: {len(fullresponse['results']['partialMatches'])}")
            print(f"Total Results: {fullresponse['results']['totalResultCount']}")
        else:
            print(f"Response: {fullresponse}")
            # for match in fullresponse['exactMatches']:
        #     print(f"Exact Match: {match}")
        return response.json()
    else:
        raise Exception(f"Error searching {entity} for {search}: {response.status_code} - {response.text}")

searchTC('post', 'postText', 'the trump administration')
searchTC('userprofile', 'userBio', 'ducks rule')