import requests

def gelbooruMd5(localMd5):
    baseUrl='https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=md5:{0}'.format(localMd5)
    gelRequest = requests.get('{0}'.format(baseUrl))
    return(gelRequest)
