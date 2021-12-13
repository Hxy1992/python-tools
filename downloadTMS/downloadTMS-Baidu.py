#coding=utf-8
import urllib.request
import os
import socket
import zlib
import math
import json

# python版本3.7

import math
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率
# 百度墨卡托投影纠正矩阵
LLBAND = [75, 60, 45, 30, 15, 0]
LL2MC = [
    [-0.0015702102444, 111320.7020616939, 1704480524535203, -10338987376042340, 26112667856603880, -35149669176653700,
     26595700718403920, -10725012454188240, 1800819912950474, 82.5],
    [0.0008277824516172526, 111320.7020463578, 647795574.6671607, -4082003173.641316, 10774905663.51142,
     -15171875531.51559, 12053065338.62167, -5124939663.577472, 913311935.9512032, 67.5],
    [0.00337398766765, 111320.7020202162, 4481351.045890365, -23393751.19931662, 79682215.47186455, -115964993.2797253,
     97236711.15602145, -43661946.33752821, 8477230.501135234, 52.5],
    [0.00220636496208, 111320.7020209128, 51751.86112841131, 3796837.749470245, 992013.7397791013, -1221952.21711287,
     1340652.697009075, -620943.6990984312, 144416.9293806241, 37.5],
    [-0.0003441963504368392, 111320.7020576856, 278.2353980772752, 2485758.690035394, 6070.750963243378,
     54821.18345352118, 9540.606633304236, -2710.55326746645, 1405.483844121726, 22.5],
    [-0.0003218135878613132, 111320.7020701615, 0.00369383431289, 823725.6402795718, 0.46104986909093,
     2351.343141331292, 1.58060784298199, 8.77738589078284, 0.37238884252424, 7.45]]
# 百度墨卡托转回到百度经纬度纠正矩阵
MCBAND = [12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0]
MC2LL = [[1.410526172116255e-8, 0.00000898305509648872, -1.9939833816331, 200.9824383106796, -187.2403703815547,
          91.6087516669843, -23.38765649603339, 2.57121317296198, -0.03801003308653, 17337981.2],
         [-7.435856389565537e-9, 0.000008983055097726239, -0.78625201886289, 96.32687599759846, -1.85204757529826,
          -59.36935905485877, 47.40033549296737, -16.50741931063887, 2.28786674699375, 10260144.86],
         [-3.030883460898826e-8, 0.00000898305509983578, 0.30071316287616, 59.74293618442277, 7.357984074871,
          -25.38371002664745, 13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
         [-1.981981304930552e-8, 0.000008983055099779535, 0.03278182852591, 40.31678527705744, 0.65659298677277,
          -4.44255534477492, 0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
         [3.09191371068437e-9, 0.000008983055096812155, 0.00006995724062, 23.10934304144901, -0.00023663490511,
          -0.6321817810242, -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
         [2.890871144776878e-9, 0.000008983055095805407, -3.068298e-8, 7.47137025468032, -0.00000353937994,
          -0.02145144861037, -0.00001234426596, 0.00010322952773, -0.00000323890364, 826088.5]]
 
 
def gcj02tobd09(lng, lat):
    """
    火星坐标系(GCJ02)转百度坐标系(BD09)
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]
 
 
def bd09togcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD09)转火星坐标系(GCJ02)
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]
 
 
def wgs84togcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]
 
 
def gcj02towgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]
 
 
def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret
 
 
def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret
 
 
def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False
 
 
def wgs84tomercator(lng, lat):
    """
    wgs84投影到墨卡托
    :param lng:
    :param lat:
    :return:
    """
    x = lng * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180) * 20037508.34 / 180
    return x, y
 
 
def mercatortowgs84(x, y):
    """
    墨卡托投影坐标转回wgs84
    :param x:
    :param y:
    :return:
    """
    lng = x / 20037508.34 * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(y / 20037508.34 * 180 * math.pi / 180)) - math.pi / 2)
    return lng, lat
 
 
def getRange(cC, cB, T):
    if (cB != None):
        cC = max(cC, cB)
    if (T != None):
        cC = min(cC, T)
    return cC
 
 
def getLoop(cC, cB, T):
    while (cC > T):
        cC -= T - cB
    while (cC < cB):
        cC += T - cB
    return cC
 
 
def convertor(cC, cD):
    if (cC == None or cD == None):
        print('null')
        return None
    T = cD[0] + cD[1] * abs(cC.x)
    cB = abs(cC.y) / cD[9]
    cE = cD[2] + cD[3] * cB + cD[4] * cB * cB + cD[5] * cB * cB * cB + cD[6] * cB * cB * cB * cB + cD[
        7] * cB * cB * cB * cB * cB + cD[8] * cB * cB * cB * cB * cB * cB
    if (cC.x < 0):
        T = T * -1
    else:
        T = T
    if (cC.y < 0):
        cE = cE * -1
    else:
        cE = cE
    return [T, cE]
 
 
def convertLL2MC(T):
    cD = None
    T.x = getLoop(T.x, -180, 180)
    T.y = getRange(T.y, -74, 74)
    cB = T
    for cC in range(0, len(LLBAND), 1):
        if (cB.y >= LLBAND[cC]):
            cD = LL2MC[cC]
            break
    if (cD != None):
        for cC in range(len(LLBAND) - 1, -1, -1):
            if (cB.y <= -LLBAND[cC]):
                cD = LL2MC[cC]
                break
    cE = convertor(T, cD)
    return cE
 
 
def convertMC2LL(cB):
    cC = LLT(abs(cB.x), abs(cB.y))
    cE = None
    for cD in range(0, len(MCBAND), 1):
        if (cC.y >= MCBAND[cD]):
            cE = MC2LL[cD]
            break
    T = convertor(cB, cE)
    return T
 
 
def bd09tomercator(lng, lat):
    """
    bd09投影到百度墨卡托
    :param lng:
    :param lat:
    :return:
    """
    baidut = LLT(lng, lat)
    return convertLL2MC(baidut)
 
 
def mercatortobd09(x, y):
    """
    墨卡托投影坐标转回bd09
    :param x:
    :param y:
    :return:
    """
    baidut = LLT(x, y)
    return convertMC2LL(baidut)
class LLT:
    def __init__(self, x, y):
        self.x = x
        self.y = y
# 百度地图18级时的像素分辨率为1m/pixel
def getResolution(level):
    return math.pow(2,(level-18))
def getResolutionLat(lat,level):
    return math.pow(2, (18 - level)) * math.cos(lat)
def lngToTileX(lng, level):
    point = bd09tomercator(lng,0)
    return math.floor(point[0] * getResolution(level) / 256)
def latToTileY(lat, level):
    point = bd09tomercator(0, lat)
    return math.floor(point[1] * getResolution(level) / 256)
# 经纬度转瓦片坐标
def lnglatToTile(lng, lat, level):
    tileX = lngToTileX(lng,level)
    tileY = latToTileY(lat,level)
    return tileX,tileY
def lngToPixelX(lng, level):
    tileX = lngToTileX(lng,level)
    point = bd09tomercator(lng, 0)
    return math.floor(point[0] * getResolution(level) - tileX * 256)
def latToPixelY(lat, level):
    tileY = latToTileY(lat, level)
    point = bd09tomercator(0, lat)
    return math.floor(point[1] * getResolution(level) - tileY * 256)
# 经纬度转像素坐标
def lnglatToPixel(lng, lat, level):
    pixelX = lngToPixelX(lng, level)
    pixelY = latToPixelY(lat, level)
    return pixelX,pixelY
def pixelXToLng(pixelX, tileX, level):
    pointX = (tileX * 256 + pixelX) / getResolution(level)
    lnglat = mercatortobd09(pointX, 0)
    return lnglat[0]
def pixelYToLat(pixelY, tileY, level):
    pointY = (tileY * 256 + pixelY) / getResolution(level)
    lnglat = mercatortobd09(0, pointY)
    return lnglat[1]
# 像素坐标和瓦片坐标转经纬度
def pixelToLnglat(pixelX, pixelY, tileX, tileY, level):
    pointX = (tileX * 256 + pixelX) / getResolution(level)
    pointY = (tileY * 256 + pixelY) / getResolution(level)
    return mercatortobd09(pointX, pointY)
 


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

#下载瓦片
def downloadUrl():
    # 当前绝对路径
    mkpath=os.path.abspath(os.path.dirname(__file__)) + '\\'
    downloadPath = mkpath + 'download\\'
    # 读取配置文件
    filejson=open(mkpath+'config.json',encoding='utf-8')    #打开文件 
    config=json.load(filejson) #把json串变成python的数据类型

    # 下载范围
    # TODO 经纬度为负数时，计算瓦片有问题
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
    for z in range(zmin,zmax + 1):
        top_tile = latToTileY(north_edge, z)
        left_tile = lngToTileX(west_edge, z)
        bottom_tile = latToTileY(south_edge, z)
        right_tile = lngToTileX(east_edge, z)
        minLong = min(left_tile, right_tile)
        maxLong = max(left_tile, right_tile)
        minLat = min(bottom_tile, top_tile)
        maxLat = max(bottom_tile, top_tile)
        temp_sum = (maxLong-minLong)*(maxLat-minLat)
        print('正在下载瓦片层级：'+ str(z) + '/' + str(zmax))
        for x in range(minLong,maxLong+1):
                path=str(z)+"\\"+str(x)
                temppath=downloadPath+path
                mkdir(temppath)
                for y in range(minLat,maxLat+1):
                    imgRealUrl = baseUrl.replace("{z}",str(z)).replace("{x}",str(x)).replace("{y}",str(y))
                    path2 = temppath+'\\'+str(y)+pictureType
                    img_count = img_count + 1
                    try:
                        urllib.request.urlretrieve(imgRealUrl,path2)
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



