import requests

def konachanMd5(localMd5):
    baseUrl='https://konachan.com/post.json?tags=md5:{0}'.format(localMd5)
    konaRequest = requests.get('{0}'.format(baseUrl))
    return(konaRequest)