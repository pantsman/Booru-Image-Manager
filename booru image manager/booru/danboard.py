import requests, hashlib, time

from pathlib import Path

baseUrl='https://danbooru.donmai.us/posts.json/'

def errorReporting(errorCode):
    if errorCode == 403:
        return 'Error 403 received Access Denied Ending Script'
    elif errorCode == 404:
        return 'Error 404 received Not Found Ending Script'
    elif errorCode == 421:
        return 'Error 421 received User Throttled Ending Script'
    elif errorCode == 424:
        return 'Error 424 received Invalid Parameters Ending Script'
    elif errorCode == 500:
        return 'Error 500 received An Unknown Error Occured on the Remote Server Ending Script'
    elif errorCode == 503:
        return 'Error 503 received Remote Service Cannot Handle the Request Ending Script'
    else:
        return 'Error {0} Received'.format(errorCode)

def danboMd5(localMd5):  
    apiBase='?md5={0}'.format(localMd5)
    danboRequest = requests.get('{0}{1}'.format(baseUrl,apiBase))
    return(danboRequest)

def search(tags,page):
    baseTags='?tags='+'%20'.join(tags)

    searchRequest = requests.get('{0}{1}&page={2}&limit=200'.format(baseUrl,baseTags,page))

    if searchRequest.status_code != 200:
        return errorReporting(searchRequest.status_code)
    elif len(searchRequest.json()) <= 0:
        return searchRequest
    
    return searchRequest

def downloadBulk(tags, page, downloadDir, ratings, banned_tags):
    s = requests.session()
    result = search(tags,page)
    while type(result) != str and len(result.json()) > 0:
        print('[Danboard]Processing page: {0}'.format(page))
        for image in result.json():
            if 'file_url' in image:
                downloadFile = Path('{0}/{1}.{2}'.format(downloadDir,image['id'],image['file_ext']))
                if (downloadFile.exists() == False 
                        and image['rating'] in ratings 
                        and any(x in banned_tags for x in image['tag_string'].split(' ')) == False):
                    imageBuff = s.get(image['file_url'])
                    downloadFile.write_bytes(imageBuff.content)
        page += 1
        result = search(tags,page)