# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse

import os
import glob
import json
import time
import requests
from urllib.parse import urlparse
from datetime import datetime

from utils.level3_api import Level3
from utils.level3_info import sync_service
from overseas.models.invalidations import Invalidations
from overseas.models.access import NiInfo, NetworkIdentifiers, Tan14User, CDN


@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):

    def json_resp(self, data, add_headers=True):
        '''
        API数据response处理函数
        '''
        status = 200 if data.get('err') == 0 else data.get('err')
        resp = HttpResponse(
            json.dumps(data), content_type="application/json", status=status,)
        if add_headers:
            resp['Access-Control-Allow-Headers'] = 'Content-Type'

        # nginx 内使用add_headers添加请求头，仅为400以下的状态码添加，需要为此添加headers否则前端无法正常返回
        # see:http://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header
        if status > 399:
            resp['Access-Control-Allow-Origin'] = '*'
            resp['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, PATCH, OPTIONS'
            resp['Access-Control-Allow-Credentials'] = 'true'
        return resp

    def get_request_date(self, request):
        '''
        请求数据获取函数
        '''
        # handle an error when request body got ex: ?a=1&b=2
        try:
            data = json.loads(request.body.decode())
        except:
            data = {}
        data.update({k: v for k, v in request.POST.items()})
        data.update({k: v for k, v in request.GET.items()})
        return data

    def options(self, *args, **kw):
        '''
        处理OPTIONS
        '''
        response_data = {'err': 200}
        return self.json_resp(response_data)

    def check_user(self, data):
        login_email = data.get('login_email', '')
        try:
            self.user = Tan14User.objects.get(login_email=login_email,
                                              operate_right=True)
        except ObjectDoesNotExist:
            return False
        return True


class BaseNiInfoView(BaseView):
    '''
    带宽流量查询接口预处理
    '''
    http_method_names = ['options', 'get']

    def get(self, request, attr, key='timeStamp'):
        data = self.get_request_date(request)
        # check domains
        nis = NetworkIdentifiers.all_ni()
        data_domains = [v for k, v in data.items() if 'domain' in k]
        unkonw_domains = list(filter(lambda k: k not in nis, data_domains))
        if unkonw_domains:
            response_data = {'err': 501,
                             'message': 'Unkonw domain %s' % '\n'.join(unkonw_domains)}
            return self.json_resp(response_data)

        # check time format
        try:
            startTime = int(data.get('startTime'))
            endTime = int(data.get('endTime'))
        except ValueError:
            response_data = {
                'err': 400,
                'message': 'Unkonw time format %s, %s' % (startTime, endTime)}
            return self.json_resp(response_data)
        time_span = settings.LEVEL3_TIME_SPAN * 60
        delta = int((endTime - startTime) / time_span)
        if delta <= 0:
            response_data = {'err': 400,
                             'message': 'StartTime comes after endTime'}
            return self.json_resp(response_data)

        results = NiInfo.get_niinfo_date(startTime, endTime, data_domains, attr, key)
        response_data = {'err': 0,
                         'results': results}
        return self.json_resp(response_data)


class BandwidthsView(BaseNiInfoView):
    '''
    查询带宽
    '''

    def get(self, request, key='timeStamp'):
        return super(BandwidthsView, self).get(request, 'bandwidth', key=key)


class FluxsView(BaseNiInfoView):
    '''
    查询流量
    '''

    def get(self, request, key='timeStamp'):
        return super(FluxsView, self).get(request, 'volume', key=key)


class NetworkId(BaseView):
    '''
     查询所有域名
    '''
    http_method_names = ['options', 'get']

    def get(self, request):
        sync_service()
        response_data = {'err': 0,
                         'domains': NetworkIdentifiers.all_ni()}
        return self.json_resp(response_data)


class RefreshView(BaseView):
    '''
    刷新与预加载接口
    force： 默认0刷新，1则为预加载
    '''
    http_method_names = ['options', 'post']

    def post(self, request, force=0):

        data = self.get_request_date(request)
        if not self.check_user(data):
            response_data = {'err': 400,
                             'message': u'需要验证权限'}
            return self.json_resp(response_data)

        post_paths = data.get('path', '').split('|')
        # 过滤相同的path
        paths = {(urlparse(path).scheme, urlparse(path).netloc, urlparse(path).path)
                 for path in post_paths}
        if not all(domain and path and scheme in ['http', 'https', 'ftp'] for scheme, domain, path in paths):
            response_data = {'err': 501,
                             'message': u'无法解析的域名 %s' % '\n'.join(post_paths)}
            return self.json_resp(response_data)
        domains = self.user.level3_domains()

        path_data = []
        for scheme, domain, path in paths:
            if domain not in domains:
                response_data = {'err': 501,
                                 'message': u'域名不在列表内 %s' % domain}
                return self.json_resp(response_data)
            else:
                path_data.append(path)
        taskids_data = []
        options = {'force': force}
        for scheme, domain in set((scheme, domain) for scheme, domain, path in paths):

            try:
                ni = NetworkIdentifiers.objects.get(
                    ni__iendswith=domain, service__isnull=False)
            except ObjectDoesNotExist:
                response_data = {'err': 501,
                                 'message': 'Can not refresh this domain %s, does not exist in level3' % domain}
                return self.json_resp(response_data)
            body = {'paths': path_data}
            resp = Level3.invalidations(str(ni), options=options, body=body)

            try:
                taskids = resp['accessGroup']['services']['service'][
                    'networkIdentifiers']['ni']['invalidations']['invalidation']
                taskids = taskids if isinstance(taskids, list) else [taskids]
            except:  # KeyError  TypeError
                response_data = {'err': 500,
                                 'status': 'fail',
                                 'message': str(resp)}
                return self.json_resp(response_data)
            urls = [taskid.get('@path', '') for taskid in taskids]
            path = '|'.join([scheme + '://' + domain + url for url in urls])
            taskids_data.append({'url': path,
                                 'taskid': taskids[0].get('@id'),
                                 'time': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                                 'percentComplete': '0'})

        response_data = {'err': 0,
                         'status': 'success',
                         'results': taskids_data}
        force = True if force else False
        for options in taskids_data:
            inval = Invalidations(**options)
            inval.force = force
            inval.save()

        return self.json_resp(response_data)


class RefreshListView(BaseView):
    '''
    获取刷新与预加载状态接口
    force： 默认False刷新，True则为预加载
    '''
    http_method_names = ['options', 'get']

    def get(self, request, force=False):

        data = self.get_request_date(request)
        if not self.check_user(data):
            response_data = {'err': 400,
                             'message': u'需要验证权限'}
            return self.json_resp(response_data)

        results = []
        nis = NetworkIdentifiers.objects.all()
        for ni in nis:
            resp = Level3.invalidations(str(ni), method='GET')
            try:
                invalidations = resp['accessGroup']['services']['service']['networkIdentifiers'][
                    'ni']['invalidations']['invalidation']
            except:
                response_data = {'err': 501,
                                 'message': 'Unexcept resp %s' % str(resp)}
                break
            invalidations = invalidations if isinstance(
                invalidations, list) else [invalidations]
            for inval in invalidations:
                urls = inval.get('paths', {}).get('path', [])
                urls = urls if isinstance(urls, list) else [urls]
                results.append({'taskid': inval.get('@id', ''),
                                'percentComplete': inval.get('@percentComplete', '')})
        output = []
        domains = self.user.level3_domains()
        for result in results:
            try:
                inval = Invalidations.objects.get(taskid=result['taskid'])
            except:
                response_data = {'err': 501,
                                 'message': 'Internal error, plase check sync_invalidations. Tips: %s' % result['taskid']}
                return self.json_resp(response_data)
            if urlparse(inval.url).netloc not in domains:
                continue
            if inval.force == force:
                result.update({'url': inval.url,
                               'time': inval.time})
                inval.percentComplete = result.get('percentComplete', '0')
                inval.save()
                output.append(result)
        response_data = {'err': 0,
                         'results': output}
        return self.json_resp(response_data)


class UserView(BaseView):
    '''
    用户新增接口
    '''
    http_method_names = ['options', 'post']

    def post(self, request):
        data = self.get_request_date(request)
        login_email = data.get('login_email', '')
        password = data.get('password', '')
        if not all([login_email, password]):
            response_data = {'err': 400,
                             'message': 'Need a login_email'}
            return self.json_resp(response_data)
        operate_right = False if data.get('operations') else True

        user = Tan14User(login_email=login_email, operate_right=operate_right)
        user.set_password(password)
        response_data = user.cdn_json()

        return self.json_resp(response_data)


class UserCDNView(BaseView):
    '''
    用户与cdn关联接口，增查
    '''
    http_method_names = ['options', 'get', 'post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kw):
        self.data = self.get_request_date(request)
        login_email = self.data.get('login_email', '')
        if not login_email:
            response_data = {'err': 400,
                             'message': 'Need a login_email'}
            return self.json_resp(response_data)
        try:
            self.user = Tan14User.objects.get(login_email=login_email)
        except:
            response_data = {'err': 400,
                             'message': 'User does not exist %s.' % login_email}
            return self.json_resp(response_data)
        return super(UserCDNView, self).dispatch(request, *args, **kw)

    def get(self, request):
        return self.json_resp(self.user.cdn_json())

    def post(self, request):
        cdns = self.data.get('cdns', [])
        if isinstance(cdns, list) and cdns:
            for cdn in cdns:
                c, created = CDN.objects.get_or_create(
                    cdn_name=cdn, tan14_user=self.user, ni=None)
                c.save()
            response_data = self.user.cdn_json()
        else:
            response_data = {'err': 400,
                             'message': 'Need cdn list , get %s' % self.data.get('cdns')}
        return self.json_resp(response_data)

    # def put(self, request):
    #     cdns = self.data.get('cdns', [])
    #     if isinstance(cdns, list) and cdns:
    #         # cdns = CDN.objects.filter(cdn_name__in=cdns).all()
    #         # user.cdn_set = cdns
    #         # user.save()
    #         for cdn in cdns:
    #             c, created = CDN.objects.get_or_create(cdn_name=cdn, tan14_user=self.user, ni=None)
    #             c.save()
    #         response_data = self.user.cdn_json()
    #     else:
    #         response_data = {'err': 401,
    #                          'message': 'Need cdn list , get %s' % self.data.get('cdns')}
    #     return _json_http_response(user.cdn_json())


class UserDomainView(BaseView):
    '''
    用户与域名关联接口，增改查
    '''

    http_method_names = ['options', 'get', 'post', 'put']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kw):
        self.data = self.get_request_date(request)
        login_email = self.data.get('login_email', '')
        if not login_email:
            response_data = {'err': 400,
                             'message': 'Need a login_email'}
            return self.json_resp(response_data)
        try:
            self.user = Tan14User.objects.get(login_email=login_email)
        except ObjectDoesNotExist:
            response_data = {'err': 400,
                             'message': 'User does not exist!'}
            return self.json_resp(response_data)
        return super(UserDomainView, self).dispatch(request, *args, **kw)

    def get(self, request):
        return self.json_resp(self.user._json())

    def post(self, request):
        domains = self.data.get('domains', [])
        cdn = self.data.get('cdn', '')
        if domains:
            for domain in domains:
                ni, created = NetworkIdentifiers.objects.get_or_create(
                    ni=domain)
                # if len(ni.cdn_set.filter(tan14_user=self.user).all()) > 0:
                #     response_data = {'err': 400,
                #                      'message': 'Domain already exist %s' % domain}
                #     return self.json_resp(response_data)
                c, created = CDN.objects.get_or_create(
                    cdn_name=cdn, tan14_user=self.user, ni=None)
                c.ni = ni
                c.save()
            response_data = self.user._json()
        else:
            response_data = {'err': 400,
                             'message': 'Need domains and cdn get %s, %s' % (domains, cdn)}
        return self.json_resp(response_data)

    def put(self, request):
        old_domain = self.data.get('old_domain', '')
        new_domain = self.data.get('new_domain', '')
        cdn = self.data.get('cdn', '')
        if old_domain and new_domain:
            try:
                old_ni = NetworkIdentifiers.objects.get(ni=old_domain)
            except ObjectDoesNotExist:
                response_data = {'err': 400,
                                 'message': 'Domain do not exist %s' % old_domain}
                return self.json_resp(response_data)
            cdn, created = CDN.objects.get_or_create(
                cdn_name=cdn, tan14_user=self.user, ni=None)
            new_ni, created = NetworkIdentifiers.objects.get_or_create(
                ni=new_domain)
        else:
            response_data = {'err': 400,
                             'message': 'Need old_domain, new_domain and cdn get %s, %s, %s' % (old_domain, new_domain, cdn)}
            return self.json_resp(response_data)
        cdn.ni = new_ni
        cdn.save()
        return self.json_resp(self.user._json())


class LogListView(BaseView):

    http_method_names = ['options', 'get']

    def get(self, request):
        data = self.get_request_date(request)
        startDate = data.get('startDate')
        endDate = data.get('endDate')
        domain = data.get('domain')

        # check date
        try:
            start = int(time.mktime(time.strptime(startDate, '%Y%m%d')))
            end = int(time.mktime(time.strptime(endDate, '%Y%m%d')))
        except ValueError:
            response_data = {'err': 400,
                             'message': u'不匹配的日期格式，需要格式YYYYMMDD'}
            return self.json_resp(response_data)
        # check domain
        try:
            NetworkIdentifiers.objects.get(
                ni__iendswith=domain, service__isnull=False)
        except ObjectDoesNotExist:
            response_data = {'err': 501,
                             'message': 'Can not refresh this domain %s, does not exist in level3' % domain}
            return self.json_resp(response_data)

        dates = {'-'.join((time.strftime('%Y-%m-%d', time.localtime(timestamp)), domain)): ['', 0]
                 for timestamp in range(start, end + 1, 24 * 60 * 60)}

        files = {date: ['{}log/{}/{}'.format(settings.LEVEL3_BASEURL, domain, os.path.basename(file)), os.path.getsize(file)] for file in  glob.iglob(
            settings.RSYNC_DAILY_DIR + domain + '/*.gz') for date in dates if os.path.basename(file).startswith(date)}
        dates.update(files)

        response_data = {'err': 0,
                         'results': sorted([{'date': date[:10],
                                             'domain': date[11:],
                                             'size': i[1],
                                             'url': i[0]} for date, i in dates.items()], key=lambda x: x['date'])}
        return self.json_resp(response_data, add_headers=False)


class LogDownloadView(BaseView):

    http_method_names = ['options', 'get']

    def get(self, request, filename):
        abs_filename = ''.join((settings.RSYNC_DAILY_DIR, filename))
        # rb 文件以rb打开否则传输过程中会出现无法解压的情况

        def file_iterator(file_name, chunk_size=512):
            with open(file_name, 'rb') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        response = StreamingHttpResponse(file_iterator(abs_filename))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Length'] = os.path.getsize(''.join((settings.RSYNC_DAILY_DIR, filename)))
        response[
            'Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
        return response


class LoginView(BaseView):
    http_method_names = ['options', 'post']

    def post(self, request):
        self.data = self.get_request_date(request)
        login_email = self.data.get('login_email', '')
        password = self.data.get('password', '')
        if not all([login_email, password]):
            response_data = {'err': 400,
                             'message': u'請輸入賬號和密碼'}
            return self.json_resp(response_data)
        from utils.user_tools import check_passwd
        check, user_obj = check_passwd(login_email, password, reset_token=True)
        resp = user_obj.json()
        resp.update({'login_email': user_obj.login_email})
        return self.json_resp(resp)


class LogoutView(BaseView):
    http_method_names = ['options', 'post']

    def post(self, request):
        self.data = self.get_request_date(request)
        token = self.data.get('token', '')
        if not token:
            response_data = {'err': 400,
                             'message': u'請輸入token'}
            return self.json_resp(response_data)
        try:
            user_obj = Tan14User.objects.get(token=token)
        except ObjectDoesNotExist:
            pass
        user_obj.token = None
        return self.json_resp({'err': 0,
                               'message': u'賬號已注銷'})


class LoginCheckView(BaseView):
    http_method_names = ['options', 'get']

    def get(self, request):
        self.data = self.get_request_date(request)
        login_email = self.data.get('login_email', '')
        if not login_email:
            response_data = {'err': 400,
                             'message': 'Need a login_email'}
            return self.json_resp(response_data)
        try:
            timestamp = int(time.time()) - settings.LOGIN_EXPIRES
            user_obj = Tan14User.objects.get(login_email=login_email,
                                            last_login__gt=timestamp)
            flag = 1
        except ObjectDoesNotExist:
            flag = 0
        return self.json_resp({'err': 0,
                               'alive': flag})


def abtest(request):
    print(request.COOKIES)
    print(request.session)
    print(request.user)
    return HttpResponse('Hello', status=200)

