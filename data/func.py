import requests

TOKEN1 = ''


def translate(words):
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"
    headers = {
        'x-rapidapi-key': TOKEN1,
        'x-rapidapi-host': "translated-mymemory---translation-memory.p.rapidapi.com"
    }
    querystring = {"langpair": "en|ru", "q": words, "mt": "1", "onlyprivate": "0", "de": "a@b.c"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    content = response.json()
    result = content['responseData']['translatedText']
    return result