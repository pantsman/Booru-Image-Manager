import hashlib
from pathlib import Path
from booru import danboard, konachan, yandere, konachannet, sakugabooru

def getMd5 (filePath):
    with open(filePath, 'rb') as localImage:
        imageHash = hashlib.md5(localImage.read()).hexdigest()
    return imageHash

def download(banned_tags,ratings,tags,downloadDir, booru, page):
    print('Finding New Images')

    if booru == 'danbooru':
        danboard.downloadBulk(tags, page, downloadDir, ratings, banned_tags)
    elif booru == 'konachan':
        konachan.downloadBulk(tags, page, downloadDir, ratings, banned_tags)
    elif booru == 'yandere':
        yandere.downloadBulk(tags, page, downloadDir, ratings, banned_tags)
    elif booru == 'konachannet':
        konachannet.downloadBulk(tags, page, downloadDir, ratings, banned_tags)
    elif booru == 'sakugabooru':
        sakugabooru.downloadBulk(tags, page, downloadDir, ratings, banned_tags)