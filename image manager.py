import requests, json, time, urllib, hashlib, sys, argparse, csv, booru
from pathlib import Path, PurePath
from booru import danboard, konachan, gelbooru

def nameImages(localHashes):
    for key in localHashes:
        print('Processing: {0}'.format(localHashes[key]))
        print('Checking Konachan')
        request = booru.konachan.konachanMd5(key)
        print('\tStatus Code: {0}'.format(request.status_code))
        print('\tContent Length: {0}'.format(len(request.json())))
        if request.status_code != 200 or len(request.json()) <= 0:
            print('Checking Danbooru')
            request = booru.danboard.danboMd5(key)
            print('\tStatus Code: {0}'.format(request.status_code))
            print('\tContent Length: {0}'.format(len(request.content)))
            if request.status_code != 200 or request.content == b'null':
                print('Checking Gelbooru')
                request = booru.gelbooru.gelbooruMd5(key)
                print('\tStatus Code: {0}'.format(request.status_code))
                print('\tContent Length: {0}'.format(len(request.content)))
                if request.status_code != 200 or request.content == b'':
                    continue
                else:
                    print('Success')
                    gelPayload = request.json()
                    fileName = '{0}/{1}.{2}'.format(localHashes[key].parent,gelPayload[0]["id"],gelPayload[0]['file_url'].split('.')[-1])
                    localHashes[key].rename(fileName)
            else:
                print('Success')
                danboPayload = request.json()
                fileName = '{0}/{1}.{2}'.format(localHashes[key].parent,danboPayload['id'],danboPayload['file_ext'])
                localHashes[key].rename(fileName) 
        else:
            print('Success')
            konaPayload = request.json()
            fileName = '{0}/{1}.{2}'.format(localHashes[key].parent,konaPayload[0]['id'],konaPayload[0]['file_url'].split('.')[-1])
            localHashes[key].rename(fileName)   
        
def generateDB(hashDBloc,sourceDir):
    newHashes = {}
    dbPath = Path(hashDBloc)
    if dbPath.exists():
        print('\tDatabase File Already Exists')
        hashDB = loadDB(hashDBloc)
        print('Database Loaded Getting New Hashes')
        updateHashes(sourceDir, hashDB ,newHashes)

        with open(dbPath, 'a') as hashDBFile:
            loopCon=1
            for key in newHashes:
                if loopCon != len(newHashes):
                    hashDBFile.write('{0},{1}\n'.format(key,newHashes[key]))
                else:
                    hashDBFile.write('{0},{1}'.format(key,newHashes[key]))
                loopCon += 1
        
    else:
        genHashes(sourceDir, newHashes)
        with open(dbPath, 'a') as hashDBFile:
            loopCon=1
            hashDBFile.write('md5,file path\n')
            for key in newHashes:
                if loopCon != len(newHashes):
                    hashDBFile.write('{0},{1}\n'.format(key,newHashes[key]))
                else:
                    hashDBFile.write('{0},{1}'.format(key,newHashes[key]))
                loopCon += 1

def genHashes (sourceDir, localHashes):
    for item in Path(sourceDir).iterdir():
        if item.is_dir() == False:
            with open(item, 'rb') as localImage:
                imageHash = hashlib.md5(localImage.read()).hexdigest()
                localHashes[imageHash] = item
        elif item.is_dir() == True and item.name != 'dupes':
            genHashes(item, localHashes)

def dedupeHashes (sourceDir, existingHashes, dupeHashes):
    for item in Path(sourceDir).iterdir():
        imageHash = None
        if item.is_dir() == False:
            if item not in existingHashes.values():
                with open(item, 'rb') as localImage:
                    imageHash = hashlib.md5(localImage.read()).hexdigest()
                if imageHash in existingHashes:
                    dupeHashes[item] = imageHash
        elif item.is_dir() == True and item.name != 'dupes':
            dedupeHashes(item, existingHashes, dupeHashes)

def updateHashes(sourceDir, localHashes, newHashes):
    for item in Path(sourceDir).iterdir():
        if item.is_dir() == False and item not in localHashes.values():
            with open(item, 'rb') as localImage:
                imageHash = hashlib.md5(localImage.read()).hexdigest()
                newHashes[imageHash] = item
        elif item.is_dir() == True and item.name != 'dupes':
            updateHashes(item, localHashes, newHashes)

def loadDB(hashDBloc):
    localHashes = {}
    with open(hashDBloc, 'r') as hashDB:
        for line in hashDB:
            if line != 'md5,file path\n':
                temp = line.strip().split(',')
                localHashes[temp[0]] = Path(temp[1])
    return localHashes

def dedupe(rootDir, hashDBloc):
    existingHashes = loadDB(hashDBloc)
    dupeHashes = {}

    print('Processing: {0}'.format(rootDir))

    startTime = time.time()
    dedupeHashes(rootDir, existingHashes, dupeHashes)
    endTime = time.time()
    
    print('Duplicate Hashes Generated in: {0} seconds'.format(endTime-startTime))

    if len(dupeHashes) > 0:
        for item in dupeHashes.keys():
            if Path('{0}/dupes'.format(item.parent)).exists() != True:
                Path('{0}/dupes'.format(item.parent)).mkdir()
            print('\tDupe Found: {0} is a match for {1}'.format(item,existingHashes[dupeHashes[item]]))
            item.replace(Path('{0}/dupes/{1}'.format(item.parent,item.name)))
    return len(dupeHashes)

def cleanDB(localHashes, hashDBloc):
    keysToDel = []
    rawDB = None
    print('Current entries in DB: {0}'.format(len(localHashes)))
    for entry in localHashes.keys():
        if Path(localHashes[entry]).exists() == False:
            print('{0} no longer exists'.format(localHashes[entry]))
            keysToDel.append(entry)
    print('Before DB Write Keys to Remove: {0}'.format(len(keysToDel)))
    if len(keysToDel) > 0:
        with open(hashDBloc, 'r+') as f:
            print('Opening DB in Read/Write')
            rawDB = f.read()
            loopCon = 1
            numLines = len(rawDB.split('\n'))
            print('\tLines in DB: {0}'.format(numLines))
            f.seek(0)
            for line in rawDB.split('\n'):
                if line.split(',')[0] not in keysToDel:
                    if loopCon != numLines:
                        f.write(line+'\n')
                    else:
                        f.write(line)
                else:
                    print('\tRemoving Key: {0}'.format(line.split(',')[0]))
                loopCon += 1
            f.truncate()
    else:
        print('\tNo Keys Found for Deletion')
    print('Keys Deleted: {0}'.format(len(keysToDel)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='',description='A Command Line Tool for Danbooru Written in Python')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--nameImages', action='store_true')
    group.add_argument('--download', action='store_true')
    group.add_argument('--generateDB', action='store_true')
    group.add_argument('--validateDB', action='store_true')
    group.add_argument('--dedupe', action='store_true')
    group.add_argument('--cleanDB', action='store_true')
    
    parser.add_argument('--tags', metavar='tags', nargs='+',
                        help='Tags to search for seperated by spaces')
    parser.add_argument('--ratings', metavar='ratings', nargs='*', default='[s]',
                        help='Ratings to be allow seperated by spaces. Only safe images allowed by default')
    
    args = parser.parse_args()

    if args.nameImages == True:
        print("not implemented")
    elif args.generateDB == True:
        hashDBloc = input('Please enter the location of the Hash DB:')
        rootDir = input("Please enter a directory to scan:")
        generateDB(hashDBloc,rootDir)
    elif args.validateDB == True:
        hashDBloc = input('Please enter the location of the Hash DB:')
        loadDB(hashDBloc)
    elif args.dedupe == True:
        hashDBloc = input('Please enter the location of the Hash DB:')
        rootDir = input("Please enter a directory to scan:")
        dupes = dedupe(rootDir,hashDBloc)
        print('Dupes Found: {0}'.format(dupes))
    elif args.cleanDB == True:
        hashDBloc = input('Please enter the location of the Hash DB:')
        localHashes = loadDB(hashDBloc)
        cleanDB(localHashes, hashDBloc)
    elif args.download == True:
        hashDBloc = input('Please enter the location of the Hash DB:')
        rootDir = input("Please enter a directory to download to:")
        localHashes = loadDB(hashDBloc)
        danboard.danboDownload(rootDir, args.ratings, args.tags, localHashes)