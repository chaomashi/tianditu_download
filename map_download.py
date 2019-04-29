# 异步爬取切片地图
from urllib import request
import os
import math
import asyncio
import time
import random
import functools

agents = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1']

def create_image_path(rootpath, level, x):
    path = './%s/%d/%d' % (rootpath, level, x)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def create_image_url(minzoom, maxzoom, basetileurl, rootpath):
    imagelists_all = []
    for zoom in range(minzoom, maxzoom + 1):

        for row in range(int(math.pow(2, zoom))):
            create_image_path(rootpath, zoom, row)

        imagelists = []
        if zoom > 0:
            for x in range(int(math.pow(2, zoom))):
                for y in range(int(math.pow(2, zoom))):
                    savepath = './%s/%d/%d/%d.png' % (rootpath, zoom, x, y)
                    tileurl = basetileurl + '&TileMatrix=%d&TileRow=%d&TileCol=%d' % (zoom, x, y)
                    imagelists.append((tileurl, savepath))
        else:
            savepath = './%s/%d/%d/%d.png' % (rootpath, zoom, 0, 0)
            tileurl = basetileurl + '&TileMatrix=%d&TileRow=%d&TileCol=%d' % (zoom, 0, 0)
            imagelists.append((tileurl, savepath))
        imagelists_all.append(imagelists)
    return imagelists_all


async def save_image(url):
    tileurl, savepath = url[0], url[1]
    loop = asyncio.get_event_loop()


    try:
        req = request.Request(tileurl)
        req.add_header('User-Agent', random.choice(agents))  # 换用随机的请求头
        time.sleep(0.5)
        await loop.run_in_executor(None, functools.partial(request.urlretrieve, tileurl, savepath))
        print('---- PID:', os.getpid(), tileurl)
    except Exception as e:
        print(e)


def main():
    # minlon, minlat = -179.9999999, -89.9999999  # 矩形区域左下角坐标
    # maxlon, maxlat = 180, 90  # 矩形区域右上角坐标
    minzoom, maxzoom = 6, 6
    basetileurl = 'http://t5.tianditu.com/vec_w/wmts?' \
                  'service=wmts&' \
                  'request=GetTile&' \
                  'version=1.0.0&' \
                  'LAYER=vec&' \
                  'tileMatrixSet=w&' \
                  'style=default&' \
                  'format=tiles&' \
                  'tk=4a00a1dc5387b8ed8adba3374bd87e5e'
    rootpath = './tiles'

    imagelists = create_image_url( minzoom, maxzoom, basetileurl, rootpath)
    for img in imagelists:
        tasks = [asyncio.ensure_future(save_image(url)) for url in img]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == '__main__':
    main_start = time.time()
    print('---Start downloading the map----')
    main()
    print('---- All time: ', time.time() - main_start)
