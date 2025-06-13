import requests
import simplejson as json

def searchTC(entity, search):
    url = "https://b569se0rc3.execute-api.us-east-1.amazonaws.com/alpha/search"
    headers = {
        'Content-Type': 'application/json',
    }
    body={
        'search': search,
        'entity': entity
    }
    response = requests.post(url, data=json.dumps(body), headers=headers)
    if response.status_code == 200:
        print(f"Search successful for {entity} with term '{search}'.")
        fullresponse = response.json()
        print([key for key, value in fullresponse.items()])
        print(f"Response: {fullresponse}")
        if entity == 'userprofile':
            fields = ['name', 'userBio']
            for field in fields:
                print(f"Exact Matches: {len(fullresponse['results'][field]['exactMatches'])}, Partial Matches: {len(fullresponse['results'][field]['partialMatches'])}")
                print(f"Total Results: {fullresponse['results'][field]['totalResultCount']}")
        else:
            print(f"Response: {fullresponse}")
            print(f"Exact Matches: {len(fullresponse['results']['exactMatches'])}, Partial Matches: {len(fullresponse['results']['partialMatches'])}")
            print(f"Total Results: {fullresponse['results']['totalResultCount']}")
            # for match in fullresponse['exactMatches']:
        #     print(f"Exact Match: {match}")
        return response.json()
    else:
        raise Exception(f"Error searching {entity} for {search}: {response.status_code} - {response.text}")

searchTC('post', 'the trump administration')
searchTC('userprofile', 'ducks rule')
searchTC('userprofile', 'Fin Apps')
