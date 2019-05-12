import requests, hashlib, time

from pathlib import Path

baseUrl='https://konachan.net/post.json'

def errorReporting(errorCode):
    if errorCode == 403:
        return 'Error 403 received Access Denied Ending Script'
    elif errorCode == 404:
        return 'Error 404 received Not Found Ending Script'
    elif errorCode == 421:
        return 'Error 421 received User Throttled Ending Script'
    elif errorCode == 422:
        return 'Error 422 The resource is locked and cannot be modified'
    elif errorCode == 423:
        return 'Eror 423 Resource already exists'
    elif errorCode == 424:
        return 'Error 424 received Invalid Parameters Ending Script'
    elif errorCode == 500:
        return 'Error 500 received An Unknown Error Occured on the Remote Server Ending Script'
    elif errorCode == 503:
        return 'Error 503 received Remote Service Cannot Handle the Request Ending Script'
    else:
        return 'Error {0} Received Ending Script'.format(errorCode)

def konachanMd5(localMd5):
    konaRequest = requests.get('{0}?tags=md5:{1}'.format(baseUrl, localMd5))
    return(konaRequest)

def search(tags,page):
    baseTags='?tags='+'%20'.join(tags)

    searchRequest = requests.get('{0}{1}&page={2}&limit=100'.format(baseUrl,baseTags,page))

    if searchRequest.status_code != 200:
        return errorReporting(searchRequest.status_code)
    elif len(searchRequest.json()) <= 0:
        return searchRequest
    
    return searchRequest

def downloadBulk(tags, page, downloadDir, ratings, banned_tags):
    s = requests.session()
    result = search(tags,page)
    while type(result) != str and len(result.json()) > 0:
        print('[Konachan.net]Processing page: {0}'.format(page))
        for image in result.json():
            if 'file_url' in image:
                downloadFile = Path('{0}/{1}.{2}'.format(downloadDir,image['id'],(image['file_url'].split('.')[-1])))
                if (downloadFile.exists() == False 
                        and image['rating'] in ratings 
                        and any(x in banned_tags for x in image['tags'].split(' ')) == False):
                    imageBuff = s.get(image['file_url'])
                    downloadFile.write_bytes(imageBuff.content)
        page += 1
        result = search(tags,page)