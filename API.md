## 目录
 [1.Domains info](#domains-info) `GET` 查询Domains信息列表  
 [2.Bandwidths data](#bandwidths-data) `GET`  查询带宽接口，按时间  
 [3.Fluxs data](#fluxs-data) `GET` 查询流量接口，按时间  
 [4.Bandwidths area](#bandwidths-area) `GET`  查询流量区域分布接口  
 [5.Fluxs area](#fluxs-area) `GET`  查询流量区域分布接口  
 [6.Refresh](#refresh) `POST`  新增刷新任务  
 [7.Preload](#preload) `POST`  新增预加载任务  
 [8.Refresh list](#refresh-list) `GET` 查询所有刷新任务状态  
 [9.Preload list](#preload-list) `GET` 查询所有预加载任务状态  
 [10.Create User](#create-user)  `POST` 新增用户  
 [11.User Domains](#user-domains) `GET, POST, PUT` 查询，新增，修改用户与域名的映射关系  
 [12.User CDN map](#user-cdn-map) `GET, POST` 查询，新增用户与cdn映射关系  
 [13.Logdownload](#logdownload) `GET` 获取日志下载url列表  
 [14.Login](#login) `POST` 登陸  
 [15.Logout](#logout) `POST` 注銷  
 [16.LoginCheck](#logincheck) `GET` 查詢賬號是否在綫  

`GET, POST, PUT, DELETE`  

-----------------------------------------------

### Domains info 
>查询Domains信息列表  
#### `GET` https://api.infquick.com/level3/domains  

return results  

```
{
    "err": 0,
    "domains": [
        "cdn.exrqs.com"
        ]
}

```

-----------------------------------------------

### Bandwidths data  
>查询带宽接口，按时间  
#### `GET` https://api.infquick.com/level3/bandwidths?domain=cdn.exrqs.com&startTime=1470297000&endTime=1470299400  

> also suppot https://api.infquick.com/level3/bandwidths?domain.0=cdn.exrqs.com&domain.1=cdn.exrqs1.com&startTime=1470297000&endTime=1470299100  

return results  

```
{
    "err": 0,
    "results": [
        {
            "timeStamp": 1470297000,
            "value": 4027
        },
        {
            "timeStamp": 1470297300,
            "value": 2463818
        },
        {
            "timeStamp": 1470297600,
            "value": 5033
        },
        {
            "timeStamp": 1470297900,
            "value": 252
        },
        {
            "timeStamp": 1470298200,
            "value": 0
        },
        {
            "timeStamp": 1470298500,
            "value": 18479097
        },
        {
            "timeStamp": 1470298800,
            "value": 1848765
        },
        {
            "timeStamp": 1470299100,
            "value": 252
        },
        {
            "timeStamp": 1470299400,
            "value": 252
        }
    ]
}
```


-----------------------------------------------
### Fluxs data  
>查询流量接口，按时间  
#### `GET` https://api.infquick.com/level3/fluxs?domain=cdn.exrqs.com&startTime=1470297000&endTime=1470299100   


> also suppot https://api.infquick.com/level3/fluxs?domain.0=cdn.exrqs.com&domain.1=cdn.exrqs1.com&startTime=1470297000&endTime=1470299100  

return results  

```
{
    "err": 0,
    "results": [
        {
            "timeStamp": 1470297000,
            "value": 150995
        },
        {
            "timeStamp": 1470297300,
            "value": 92393177
        },
        {
            "timeStamp": 1470297600,
            "value": 188744
        },
        {
            "timeStamp": 1470297900,
            "value": 9437
        },
        {
            "timeStamp": 1470298200,
            "value": 0
        },
        {
            "timeStamp": 1470298500,
            "value": 692966130
        },
        {
            "timeStamp": 1470298800,
            "value": 69328699
        },
        {
            "timeStamp": 1470299100,
            "value": 9437
        }
    ]
}
```

-----------------------------------------------

### Bandwidths area  
>查询流量区域分布接口  
#### `GET` https://api.infquick.com/level3/bandwidths/area?domain=cdn.exrqs.com&startTime=1470297000&endTime=1470299400  

> also suppot https://api.infquick.com/level3/bandwidths/area?domain.0=cdn.exrqs.com&domain.1=cdn.exrqs1.com&startTime=1470297000&endTime=1470299100   

return results  

```
{
  "err": 0,
  "results": [
    {
      "city": "Miami",
      "city_cn": "迈阿密",
      "value": 785
    },
    {
      "city": "Seoul",
      "city_cn": "首尔",
      "value": 439
    }
  ]
}
```

-----------------------------------------------
### Fluxs area
>查询流量区域分布接口
#### `GET` https://api.infquick.com/level3/fluxs/area?domain=cdn.exrqs.com&startTime=1470297000&endTime=1470299100  


> also suppot https://api.infquick.com/level3/fluxs/area?domain.0=cdn.exrqs.com&domain.1=cdn.exrqs1.com&startTime=1470297000&endTime=1470299100  

return results

```
{
  "err": 0,
  "results": [
    {
      "city": "Miami",
      "city_cn": "迈阿密",
      "value": 29490
    },
    {
      "city": "Seoul",
      "city_cn": "首尔",
      "value": 16513
    }
  ]
}
```


-----------------------------------------------

### Refresh  
>新增刷新任务  
#### `POST` https://api.infquick.com/level3/refresh  


> accept json body  
> ```{
  "login_email": "bao.xu@maichuang.net",
  "path": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html"
}
```
> path: 必选, url, require domain by itself  
>login_email: 必选  

return results  

```
{
  "err": 0,
  "results": [
    {
      "time": "2016/09/13 15:44:07",
      "url": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html",
      "taskid": "AG_268176/277008023@268176-144834-1473672350286",
      "percentComplete": "0"
    },
    {
      "time": "2016/09/13 15:44:07",
      "url": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html",
      "taskid": "AG_268176/277008023@268176-144834-1473673497985",
      "percentComplete": "0"
    }
  ],
  "status": "success"
}
```

-----------------------------------------------

### Preload  
>新增预加载任务  
#### `POST` https://api.infquick.com/level3/preload  


> ```{
  "login_email": "bao.xu@maichuang.net",
  "path": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html"
}
```
> path: 必选, url, require domain by itself
>login_email: 必选


return results

```
{
  "err": 0,
  "results": [
    {
      "time": "2016/09/13 15:44:07",
      "url": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html",
      "taskid": "AG_268176/277008023@268176-144834-1473672350286",
      "percentComplete": "0"
    },
    {
      "time": "2016/09/13 15:44:07",
      "url": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html",
      "taskid": "AG_268176/277008023@268176-144834-1473673497985",
      "percentComplete": "0"
    }
  ],
  "status": "success"
}
```

-----------------------------------------------

### Refresh List  
>查询所有刷新任务状态  
#### `GET` https://api.infquick.com/level3/refresh_list?login_email=bao.xu@maichuang.net  

> also support json body  
> ```{
  "login_email": "bao.xu@maichuang.net",
}
```


> return percentComplete: 0(get ready)~100(finish)  

return results  

```
{
  "err": 0,
  "results": [
    {
      "time": "2016/09/13 15:44:07",
      "url": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html",
      "taskid": "AG_268176/277008023@268176-144834-1473672350286",
      "percentComplete": "0"
    },
    {
      "time": "2016/09/13 15:44:07",
      "url": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html",
      "taskid": "AG_268176/277008023@268176-144834-1473673497985",
      "percentComplete": "100"
    }
  ]
}
```

-----------------------------------------------

### Preload List  
>查询所有预加载任务状态  
#### `GET` https://api.infquick.com/level3/preload_list?login_email=bao.xu@maichuang.net  

> also support json body  
> ```{
  "login_email": "bao.xu@maichuang.net",
}
```

> return: percentComplete: 0(get ready)~100(finish)  

return results  

```
{
  "err": 0,
  "results": [
    {
      "time": "2016/09/13 15:44:07",
      "url": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html",
      "taskid": "AG_268176/277008023@268176-144834-1473672350286",
      "percentComplete": "0"
    },
    {
      "time": "2016/09/13 15:44:07",
      "url": "http://cdn.exrqs.com/test.html|http://cdn.exrqs.com/test1.html",
      "taskid": "AG_268176/277008023@268176-144834-1473673497985",
      "percentComplete": "0"
    }
  ]
}
```

-----------------------------------------------

### Create User  
>新增用户  
#### `POST` https://api.infquick.com/level3/user  

> also support json body  
> ```{
  "login_email":"bao.xu@maichuang.net",
  "password": "123",
}
```

>login_email，必选参数，用户邮箱，必须为ops内已有的帐号  
>password, 必选参数，密码  
>operations，可选参数，设置用户是否可刷新预加载，默认为True，接受false，表示无法刷新预加载  
ex:```
{
  "login_email":"bao.xu@maichuang.net",
  "password": "123",
  "operations": "false"
}
```

return results  
```
{
 'err': 0,
 'user': self.login_email,
 'operate_right': true,
 'cdns':[]
}
```
-----------------------------------------------

### User Domains  
>查询，新增，修改用户与域名的映射关系  
#### `GET` https://api.infquick.com/level3/user_domains?login_email=bao.xu@maichuang.net  

> Needs: login_email: tan14useremail  

return results  

```
{
  "err": 0,
  "user": "bao.xu@maichuang.net",
  "operate_right": true,
  "results": [
    {
      "domains": [
        {
          "domain": "ktest.com",
          "state": "Active"
        },
        {
          "domain": "ctest.com",
          "state": "Active"
        }
              ],
      "cdn": "level3"
    }
  ]
}
```

#### `POST` https://api.infquick.com/level3/user_domains  

> accept json body  
> {
    "login_email": "bao.xu@maichuang.net",
    "cdn": "level3",
    "domains": ["test.com"]
}
> login_email: 必选, tan14useremail  
> cdn: 必选  

return results  

```
{
  "err": 0,
  "results": [
    {
      "domains": [
        "ktest.com",
        "ctest.com"
      ],
      "cdn": "level3"
    }
  ]
}
```


#### `PUT` https://api.infquick.com/level3/user_domains  

> id: 必选, cdn_id  

> accept json body  
> {
    "login_email": "bao.xu@maichuang.net",
    "cdn": "level3",
    "domains": "test.com"
}  
> login_email: 必选, tan14useremail  
> cdns: 必选, 需要数组格式的cdns, 例如:["level3"], ["level3", "qcould"]  

return results  

```
{
  "err": 0,
  "results": [
    {
      "domains": [
        "ktest.com",
        "ctest.com"
      ],
      "cdn": "level3"
    }
  ]
}
```

-----------------------------------------------

### User CDN map  
>查询，新增用户与cdn映射关系  
#### `GET` https://api.infquick.com/level3/user_cdns?login_email=bao.xu@maichuang.net  

return results  

```
{
"err": 0,
"cdns": ['level3']
}
```

#### `POST` https://api.infquick.com/level3/user_cdns  

> accept json body  
> {
    "login_email": "bao.xu@maichuang.net",
    "cdns": ["level3"]
}

return results  

```
{
"err": 0,
"cdns": ['level3']
}
```

-----------------------------------------------

### Logdownload  
#### `GET` https://api.infquick.com/level3/logdownload?domain=cdn.exrqs.com&startDate=20160928&endDate=20160930  

return results  

```
{
  "err": 0,
  "results": [
    {
      "domain": "cdn.exrqs.com",
      "date": "2016-09-28",
      "size": 0,
      "url": ""
    },
    {
      "domain": "cdn.exrqs.com",
      "date": "2016-09-29",
      "size": 1904,
      "url": "https://api.infquick.com/level3/log/2016-09-29-cdn.exrqs.com.log.gz"
    },
    {
      "domain": "cdn.exrqs.com",
      "date": "2016-09-30",
      "size": 0,
      "url": ""
    }
  ]
}
```


-----------------------------------------------

### Login  
登陸  
#### `POST` https://api.infquick.com/level3/login  
> accept json body  
> {
    "login_email": "bao.xu@maichuang.net",
    "password": "123",
}

> login_email: 必选, tan14useremail  
> password: 必选  

 return results

```

```

-----------------------------------------------

### Logout  
注銷  
#### `POST` https://api.infquick.com/level3/logout  

> accept json body  
> {
    "token": "sxkxbzmu72jxm",
}
> token: 必选, 口令  

return results  

```

```



-----------------------------------------------

### LoginCheck  
查詢賬號是否在綫  
#### `GET` https://api.infquick.com/level3/logincheck  
> accept json body  
> {
    "token": "sxkxbzmu72jxm",
}
> token: 必选, 口令  

return results  

```

```

-----------------------------------------------

####  `废弃`

### CDN

#### `GET` https://api.infquick.com/level3/cdn


return results

```
{
  "results": [
    {
      "id": 1,
      "name": "level3"
    },
    {
      "id": 2,
      "name": "qcould"
    }
  ],
  "err": 0
}
```

#### `POST` https://api.infquick.com/level3/cdn

> cdn: 必选, cdn_name

return results

```
{
  "cdn": "maichuang",
  "id": 3,
  "err": 0
}
```

#### `PUT` https://api.infquick.com/level3/cdn

> id: 必选, cdn_id

return results

```
{
  "cdn": "Maichuang",
  "id": 3,
  "err": 0
}
```




-----------------------------------------------

# create user
`POST`
https://if.tan14.cn/level3/user?login_email=
{"login_email":""}

```
need create user and company in ops first
`POST`
https://if.tan14.cn/useful/create/company
{"company_name": "","company_alias": "","owner_name":"", "owner_email":""}
```
# map user and domians
`POST`
https://if.tan14.cn/level3/user_domains
{ "login_email": "", "cdn": "level3", "domains": [""] }


-----------------------------------------------


# Setup

### base requirements
reids
mysql
python3
<br/><br/><br/>

### python package
### if you are working with python3.5.1 remove this pkg-resources==0.0.0
> pip install -r requirements.txt
<br/>

### migrate sql
### frist you need checkout etc/def.ini if you start it
### or create [custom].ini and add [custom] in your environment
### then create database named overseas
<br/><br/>

### just make it sure
> python manage.py makemigrate
### migrate
> python manage.py migrate

### create a superuser if you need
> python manage.py createsuperuser
[default name:never]
[default passwd:overseas]


### need update group info for the very begining
### update ag
> python manage.py sync_ag
### update service
> python manage.py sync_service


### beagin celery task
> celery -A overseas.tasks worker -B -l info


### runserver
> python manage.py runserver


### also can start with supervisor,but you really should read etc/supervisord.conf at first
>确保supervisor配置中的日志文件夹stdout_logfile是存在的


# 部署在10.1.0.4的never的overseas虚拟环境上

>ssh never@10.1.0.4 -p36899

>password：bmw12345

>workon overseas

>cd overseas

>supervisorctl


