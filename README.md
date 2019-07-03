职位信息可视化
===========
搜集智联招聘上2W个职位并进行分析。

运行平台
-------
Windows 10, python 3.7.2, MongoDB 4.0.6。(其他平台应该也能运行，未经过测试)

1.安装依赖
-------
    (在代码根目录下) pip install -r requirements.txt -i https://pypi.doubanio.com/simple

2.爬取数据
--------
    cd zhaopin
    (在zhaopin目录下) python run.py

等待程序运行结束

3.启动网站
--------
    cd ../
    (在flask_movie目录下) set FLASK_APP=app.py
    (在flask_movie目录下) flask run

4.访问网站
---------
在 http://localhost:5000 访问网站


关于Scrapy在Windows下的安装
------------------------
Scrapy依赖的Twisted在没有安装vc++开发工具的windows上使用默认是安装不成功,解决方法请参考官方文档。




