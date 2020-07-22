# downloadTMS

> 下载TMS规则的地图瓦片

## 项目简介

``` bash
	downloadTMS.py 主程序
    config.json 配置文件（配置下载相关参数）
```

## config.json 说明

```bash

    {
        "baseUrl":"http://mt1.google.cn/vt/lyrs=y&hl=zh-CN&gl=CN&src=app&x={x}&y={y}&z={z}&s=G",//TMS地图服务地址
        "pictureType":".png",//下载后的图片格式
        "zoomMin":10,//地图缩放级别
        "zoomMax":12,//地图缩放级别
        "southEdge":25.9161,//地图范围
        "northEdge":26.1852,//地图范围
        "westEdge":119.079,//地图范围
        "eastEdge":119.528//地图范围
    }

```

## 项目构建

    直接使用Python3启动