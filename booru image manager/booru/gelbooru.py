import requests

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
        return 'Error {0} Received Ending Script'.format(errorCode)

def gelbooruMd5(localMd5):
    baseUrl='https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=md5:{0}'.format(localMd5)
    gelRequest = requests.get('{0}'.format(baseUrl))
    return(gelRequest)
