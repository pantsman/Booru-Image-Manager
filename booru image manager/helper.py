import hashlib, sqlite3, os, platform
from pathlib import Path
from booru import danboard

def clearScreen():
    if platform.system():
        os.system('cls')
    else:
        os.system('clear')

def getMd5 (filePath):
    with open(filePath, 'rb') as localImage:
        imageHash = hashlib.md5(localImage.read()).hexdigest()
    return imageHash

def genPaths(sourceDir, pathList):
    for item in Path(sourceDir).iterdir():
        if item.is_dir() == False:
            pathList.append(item)
        elif item.is_dir() == True:
            genPaths(item, pathList)

def updatePaths(database):
    try:
        conn = sqlite3.connect(database)
    except:
        print('Failed to connect to database')
        exit()
    cur = conn.cursor()

    print(database)

    cur.execute("SELECT path FROM images")

    paths = cur.fetchall()

    for root in paths:
        print(Path(root[0]).parent)

def tagSort(database):
    sourceDir = Path(input('Enter Directory to Sort:'))
    try:
        conn = sqlite3.connect(database)
    except:
        print('Failed to connect to database')
        exit()
    cur = conn.cursor()

    for item in sourceDir.iterdir():
        if item.is_dir() == False:
            cur.execute("SELECT hash FROM images where path=?", ('{0}'.format(item),))
            md5Hash = cur.fetchone()[0]
            search = danboard.danboMd5(md5Hash)
            print(search.json())
            input()
    