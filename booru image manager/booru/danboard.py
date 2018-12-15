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

def downloadBulk(rootDir, ratings, tags, localHashes):
    s = requests.session()
    baseTags='?tags='+'%20'.join(tags)
    page=1

    while True:
        danboRequest = requests.get('{0}{1}&page={2}'.format(baseUrl,baseTags,page))
        if danboRequest.status_code != 200:
            return errorReporting(danboRequest.status_code)
        elif len(danboRequest.json()) <= 0:
            return "Download Complete"
        print('Processing Page: {0}'.format(page))
        
        for danboImage in danboRequest.json():
            if danboImage['rating'] in ratings and danboImage['is_banned'] != True and 'file_url' in danboImage:
                localFile = Path('{0}/{1}.{2}'.format(rootDir,danboImage['id'],danboImage['file_ext']))
                localMd5 = None
                if danboImage['md5'] not in localHashes.keys():
                    print('\tFile not in DB')
                    if localFile.exists() == True:
                        with open(localFile, 'rb') as localImage:
                            localMd5 = hashlib.md5(localImage.read()).hexdigest()
                        if danboImage['md5'] != localMd5:
                            print('\tMoving Existing File: MD5 Mismatch')
                            newFile = Path('{0}/{1}'.format(localFile.parent,localFile.name+'.backup'))
                            print('\tBackup File Location: {0}'.format(newFile))
                            localFile.replace(newFile)
                            print('\tdownloading new file {0} rating: {1}'.format(localFile,danboImage['rating']))
                            something = s.get(danboImage['file_url'])
                            localFile.write_bytes(something.content)
                            time.sleep(1)
                        else:
                            print('\tFile Already Exists')
                    else:
                        print('\tdownloading new file {0} rating: {1}'.format(localFile,danboImage['rating']))
                        something = s.get(danboImage['file_url'])
                        localFile.write_bytes(something.content)
        page += 1