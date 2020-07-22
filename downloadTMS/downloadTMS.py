#coding=utf-8
import urllib.request
import os
import socket
import zlib
import math
import json

# python版本3.7

# 设置超时
socket.setdefaulttimeout(60)

# 创建目录函数
def mkdir(path):
    
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path) 
 
        # print('path create success!')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        # print('path already exist!')
        return False

# 经纬度转瓦片行列号
def long2tile(lon, zoom) :
    return (math.floor((lon + 180) / 360 * math.pow(2, zoom)))

# 经纬度转瓦片行列号
def lat2tile(lat, zoom):
    return (math.floor((1 - math.log(math.tan(lat * math.pi / 180) + 1 / math.cos(lat * math.pi / 180)) / math.pi) / 2 * math.pow(2, zoom)))

#下载瓦片
def downloadUrl():
    # 当前绝对路径
    mkpath=os.path.abspath(os.path.dirname(__file__)) + '\\'
    downloadPath = mkpath + 'download\\'
    # 读取配置文件
    filejson=open(mkpath+'config.json',encoding='utf-8')    #打开文件 
    config=json.load(filejson) #把json串变成python的数据类型

    # 下载范围
    zmin = config['zoomMin']
    zmax = config['zoomMax']
    south_edge = config['southEdge']
    north_edge = config['northEdge']
    west_edge = config['westEdge']
    east_edge = config['eastEdge']
    # 下载地址
    baseUrl = config['baseUrl']
    pictureType = config['pictureType']
    # 下载统计
    img_count = 0
    img_success = 0
    img_error = 0
    # 遍历URL，获取数据
    for z in range(zmin,zmax):
        top_tile = lat2tile(north_edge, z)
        left_tile = long2tile(west_edge, z)
        bottom_tile = lat2tile(south_edge, z)
        right_tile = long2tile(east_edge, z)
        minLong = min(left_tile, right_tile)
        maxLong = max(left_tile, right_tile)
        minLat = min(bottom_tile, top_tile)
        maxLat = max(bottom_tile, top_tile)
        for x in range(minLong,maxLong):
                path=str(z)+"\\"+str(x)
                temppath=downloadPath+path
                mkdir(temppath)
                for y in range(minLat,maxLat):
                    str3=baseUrl.replace("{z}",str(z))
                    str3=str3.replace("{x}",str(x))
                    str3=str3.replace("{y}",str(y))
                    path2=temppath+'\\'+str(y)+pictureType
                    img_count = img_count + 1
                    try:
                        urllib.request.urlretrieve(str3,path2)
                    except Exception as e:
                        img_error = img_error + 1
                        print(e)
    
    img_success = img_count - img_error
    
    print('***********************************')
    print('下载完成:')
    print('瓦片总数：'+ str(img_count))
    print('下载成功：'+ str(img_success))
    print('下载失败：'+ str(img_error))
    print('***********************************')

if __name__ == '__main__':
    downloadUrl()#开始下载



