# Overseas  部署文档
[toc]

## 环境需求


| 类型 | 环境 | 版本 | 说明 |
| :--------: |
| 主要语言 | Python | 大于3.5.0 | 执行程序 |
| 数据库 | Mysql | 5.7 | 用于存储后台数据 |
| 数据库 | Redis | 3.6.0 | 用于存储定时任务（celery task）以及存储cache |
| 主要框架 | Django | 1.10.0 | WEB框架 |
| 网络代理服务 | Nginx | 1.10.2 | HTTP和反向代理服务器 |
| 主要进程托管程序 | supervisor | 3.3.1 | 用于WEB进程启动以及管理 |
| 代码管理 | Git | 无 | 代码托管 |


## 环境安装
### 安装Python3.5(Ubuntu自带)，Centos可能需要自行安装

```
wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
tar xf Python-3.5.0.tgz
cd Python-3.5.0
./configure --prefix=/usr/python3.5--enable-shared
make
make install
ln –s /usr/python3.5/bin/python3 /usr/bin/python3
ln –s /usr/python3.5/bin/pip3 /usr/bin/pip3
```

### 安装Mysqld
Ubuntu `sudo apt-get install mysql-server` 
Centos `yum install mysql-server` 
启动Mysql服务`service mysqld start`
进入mysql `mysql -uroot -p`
输入密码后新增必要的表空间
`CREATE DATABASE overseas DEFAULT CHARACTER SET utf8`

### 安装Redis 
Ubuntu `sudo apt-get install redis-server` 
Centos `yum install redis-server`



### 安装Supervisor 
`pip install supervisor` 

### 安装Git
Ubuntu `sudo apt-get install git`
Centos `yum install git`

>DJANGO可以在安装python第三方库时一并安装

## 获取代码 并安装相应的python第三方库
获取代码`git clone git@github.com:nevermoreluo/privateoverseas.git` 
`cd privateoverseas`
安装所需的第三方库`pip3 install -r requirements.txt`
软连接supervisor配置文件`ln -s etc/overseas.ini /etc/supervisord/overseas.ini`
启动supervisor `supervisord`

## 根据需求修改配置文件
配置文件在privateoverseas/etc内

```
默认情况下仅需要修改aliyun.ini文件内的mysql配置，以及def.ini内的LEVEL3_APIKEY，LEVEL3_SECRET即可。
以下是对配置文件的简介：

privateoverseas/etc
		aliyun.ini 用于线上的mysql数据库配置（user, password,host,port等）线上部署DEBUG必须为False
		def.ini 默认配置，DEBUG为True用于开启一些debug工具，例如django-debug-tool和django自带的debug，线上项目必须为False，防止信息泄露，以及性能损耗。LEVEL3_APIKEY，LEVEL3_SECRET用于设置level3的apikey和secret
		nevermore.ini 用于本地debug时设置的数据库
		overseas.ini supervisor配置文件
		overseas_uwsgi.ini uwsgi协议配置文件
		supervisord.conf 仅用于备份，防止无配置文件而无法启动supervisor的情况
```

## 使用django migrate 创建数据库
`python3 manage.py migrate`

## 创建django后台的superuser
`python3 manage.py createsuperuser`
根据提示依次输入账号，邮箱，密码以及重复密码即可。

## 进入supervisorctl开启服务
开启服务之前请务必确保建立日志服务必须的日志文件已被创建。
他们分别是：
/var/log/overseas/django.log 用于存储django运行日志的文件
/var/log/rsync_level3/ 用于提供level3日志服务的主目录
/var/log/rsync_level3/maichuang/ 用于rsync同步level3日志文件夹
/var/log/rsync_level3/daily_log/ 用于存储每日打包后的日志文件的文件夹
/var/log/celery_stdout.log 用于存储supervisor celery日志的文件
/var/log/privateoverseas_stdout.log 用于存储supervisor privateoverseas日志的文件
/var/log/flower.log 用于存储supervisor flower日志的文件
```
supervisorctl
>start all
```

## HTTPS证书获取

根据系统的不同可以上[certbot](https://certbot.eff.org/)获取免费HTTPS证书服务。
下面例举centos7的获取示例：

```
sudo yum install certbot
certbot certonly --standalone -d api.infquick.com -d portal.infquick.com
```
根据提示创建证书，成功后会在`/etc/letsencrypt/live/api.infquick.com/`目录内生成key和cert
cert ----> fullchain.pem
key ----> privkey.pem

nginx进行如下配置即可
```
/etc/nginx/conf.d/api.infquick.conf

server {
    listen 80;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/api.infquick.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.infquick.com/privkey.pem;
    server_name api.infquick.com;

    # for Level3 portal API
    location ~ ^/(level3) {
        proxy_pass http://127.0.0.1:8300;
    }

    location / {
        proxy_pass http://127.0.0.1:8300;
    }

    # for Level3 admin static
    location /static/ {
        alias /home/overseas/privateoverseas/static/;
    }
}
```
重启Nginx`nginx -s reload`
即可访问https://api.infuqick.com页面,使用上面生成的后台superuser账号即可登录管理
