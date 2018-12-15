import requests, json, time, urllib, hashlib, sys, yaml, sqlite3, tqdm, os, platform, helper

from pathlib import Path, PurePath
from booru import danboard

def startup():
    print('Loading App')
    configLoc = Path('{0}/{1}'.format(Path(__file__).parent,'config.yml'))
    if Path(configLoc).exists() == True:
        print('\tConfig file found')
        with open(configLoc) as configFile:
            try:
                print('\tLoading Config')
                config = yaml.load(configFile)
            except yaml.YAMLError as exc:
                print(exc)
                exit()
        
        print('\tConnecting to DB')
        try:
            conn = sqlite3.connect(config['database'])
        except:
            print('Failed to connect to DB')
            exit()

        cur = conn.cursor()

        print('\tValidating Image Table')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS images (hash,path)''')

        conn.commit()
        conn.close()

        print('\tStartup Complete\n\n')
        return config
    else:
        print('Configuration File Missing Exiting')
        exit()

def menu():
    print('Booru Image Manager\n\n'\
            '1. Load/Refresh Folders\n'\
            '2. Database Stats\n'\
            '3. Download Images\n'\
            '4. Tag Sort\n'\
            '5. Exit'\
            )
    try:
        option = int(input('Selection:'))
    except:
        print('Invalid Input Try Again')
        return None

    return option

def loadFolder(imageDB):
    pathList = []
    newPaths = []
    newHashes = []
    imageFolder = Path(input('Path to Folder:'))

    helper.genPaths(imageFolder, pathList)

    print('Paths Found: {0}\n'.format(len(pathList)))
    print('Connecting to DB\n')
    try:
        conn = sqlite3.connect(imageDB)
    except:
        print('Failed to connect to database')
        exit()

    cur = conn.cursor()

    print('Checking for new paths')
    for path in tqdm.tqdm(pathList):
        dbId = ('{0}'.format(path),)
        cur.execute('SELECT path FROM images WHERE path=?', dbId)
        entry = cur.fetchall()
        if len(entry) == 0:
            newPaths.append(path)

    print('Paths to add: {0}\n'.format(len(newPaths)))
    
    if len(newPaths) > 0:
        print('Generating hashes\n')
        for path in tqdm.tqdm(newPaths):
            newHashes.append([helper.getMd5(path),str(path)])
        cur.executemany('INSERT INTO images VALUES (?,?)', newHashes)
        conn.commit()
        conn.close()
    input('Import complete press enter to continue')
    helper.clearScreen()

def download(database,banned_tags,ratings):
    s = requests.session()
    source = 'danbooru'
    newImages = []
    tags = [x.strip(' ') for x in str.split(input('Please enter your tags seperated by commas:'),',')]
    downloadDir = Path(input('Please enter the directory to download to:'))
    page=1
    try:
        conn = sqlite3.connect(database)
    except:
        print('Failed to connect to database')
        exit()
    cur = conn.cursor()

    print('Finding New Images')

    if source == 'danbooru':
        result = danboard.search(tags,page)
        while type(result) != str and len(result.json()) > 0:
            print('Processing page: {0}'.format(page))
            for image in result.json():
                if 'file_url' in image:
                    cur.execute('SELECT path FROM images WHERE hash=?', ('{0}'.format(image['md5']),))
                    entry = cur.fetchall()
                    if len(entry) == 0:
                        newImages.append(image['md5'])
                        downloadFile = Path('{0}/{1}.{2}'.format(downloadDir,image['id'],image['file_ext']))
                        if (downloadFile.exists() == False 
                                and image['rating'] in ratings 
                                and any(x in banned_tags for x in image['tag_string'].split(' ')) == False):
                            imageBuff = s.get(image['file_url'])
                            downloadFile.write_bytes(imageBuff.content)
            page += 1
            result = danboard.search(tags,page)
    print(len(newImages))

if __name__ == "__main__":
    config = startup()

    while (True):
        option = menu()
        helper.clearScreen()
        if option == 1:
            loadFolder(config['database'])
        if option == 3:
            download(config['database'],config['banned_tags'],config['ratings'])
        if option == 4:
            helper.tagSort(config['database'])
        if option == 5:
            exit()
        if option == 6:
            print(config['banned_tags'])