import requests, json, time, urllib, hashlib, sys, yaml, sqlite3, tqdm, os, platform, helper, argparse, logging, booru

from booru import danboard, gelbooru
from pathlib import Path, PurePath
#from booru import danboard

def startup(configLoc):
    #configLoc=args.configLoc
    if args.verbose == True:
        logging.basicConfig(level=logging.INFO)
        logging.info('Loading App')
        if Path(configLoc).exists() == True:
            logging.info('Config file found')
            with open(configLoc) as configFile:
                try:
                    logging.info('Loading Config')
                    config = yaml.load(configFile)
                except yaml.YAMLError as exc:
                    logging.error(exc)
                    exit()
        
            logging.info('Connecting to DB')
            try:
                conn = sqlite3.connect(config['database'])
            except:
                logging.error('Failed to connect to DB')
                exit()
            cur = conn.cursor()
            logging.info('Creating Image Table if Missing')
            cur.execute('''CREATE TABLE IF NOT EXISTS images (hash,path)''')
            conn.commit()
            conn.close()
            logging.info('Startup Complete\n\n')
            return config
        else:
            logging.error('Configuration File Missing Exiting')
            exit()
    else:
        if Path(configLoc).exists() == True:
            with open(configLoc) as configFile:
                try:
                    config = yaml.load(configFile)
                except yaml.YAMLError as exc:
                    exit()
            try:
                conn = sqlite3.connect(config['database'])
            except:
                exit()
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS images (hash,path)''')
            conn.commit()
            conn.close()
            return config
        else:
            exit()


def loadFolder(imageDB, imageFolder):
    pathList = []
    newPaths = []
    newHashes = []
    #imageFolder = Path(input('Path to Folder:'))

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

def download(database,banned_tags,ratings,tags,downloadDir):
    s = requests.session()
    source = 'danbooru'
    newImages = []
    #tags = [x.strip(' ') for x in str.split(input('Please enter your tags seperated by commas:'),',')]
    #downloadDir = Path(input('Please enter the directory to download to:'))
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

    parser = argparse.ArgumentParser(description='Booru Image Manager')

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Increases Verbosity')
    parser.add_argument('-c', '--config', dest='configLoc', default=Path('{0}/{1}'.format(Path(__file__).parent,'config.yml')), help='Specifies the Location of the Configuration File')
    
    subParsers = parser.add_subparsers(help='Available Commands', title='subcommands')
    
    parserDownload = subParsers.add_parser('download', help='Download Images')
    parserDownload.add_argument('-t', '--tags', dest='tags', help='Tags to Search for', nargs='+', required=True)
    parserDownload.add_argument('-f', '--folder', dest='downloadFolder', help='Folder to Download Images to', required=True)
    parserDownload.add_argument('-b', '--booru', dest='booru', help='Booru Site to Search')
    
    parserLoad = subParsers.add_parser('load', help='Load New Folders/Images')
    parserLoad.add_argument('-f', '--folder', dest='imageFolder', help='Location of Folder to Load', required=True)

    args = parser.parse_args()
    
    config = startup(args.configLoc)

    if args.downloadFolder:
        download(config['database'],config['banned_tags'],config['ratings'],args.tags, args.downloadFolder)
    elif args.imageFolder:
        loadFolder(config['database'], args.imageFolder)