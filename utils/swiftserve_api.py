# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# Date: 2016-08-30
# auth: nevermore

import requests
from django.conf import settings


class Swiftserve:
    session = requests.Session()
    session.headers['User-Agent'] = 'Maichuang'
    session.headers['Content-Type'] = 'application/json'
    auth = (settings.SWIFTSERVE_USER, settings.SWIFTSERVE_PASSWORD)
    method_mapping = {
        'GET': session.get,
        'POST': session.post,
        'PUT': session.put,
        'DELETE': session.delete,
    }
    property_types = ['livestream', 'videoondemand',
                      'filedownload', 'websiteacceleration']

    invalidation_type = ['videoondemand', 'filedownload',
                         'websiteacceleration', 'entity']

    @staticmethod
    def _request(active, method='GET', **data):
        _opener = Swiftserve.method_mapping[method]
        resp = _opener(''.join([settings.SWIFTSERVE_BASE, active]),
                       auth=Swiftserve.auth, data=data)
        if resp.status_code == 404:
            return {'error_detail': '404 Not Found'}
        try:
            return resp.json()
        except ValueError:
            return {'error_detail': resp.text}

    @staticmethod
    def get_entity_list():
        '''
        return info of entities
        allow GET method only
        '''
        return Swiftserve._request('/api/entity/')

    @staticmethod
    def entity_details(**data):
        '''
        GET: return entity details info
        POST: create an entity
        DELETE: delete an entity with entity_id
        '''
        method = data.pop('method', 'GET')
        entity_id = data.pop('entity_id', None)

        if method == 'PUT':
            return {'error_detail': u'该方法不接受PUT请求'}
        elif method == 'POST':
            if data.get('name') is None:
                return {'error_detail': u'name必选，请指定一个名称'}
            if data.get('short_name') is None:
                return {'error_detail': u'short_name必选，请指定一个简称'}
            if data.get('parent') is None:
                return {'error_detail': u'parent必选，请指定一个parent'}
            active = '/api/entity/'
        elif entity_id:
            active = '/api/entity/%s/' % entity_id
        else:
            return {'error_detail': u'{}方法需要entity_id参数'.format(method)}

        return Swiftserve._request(active, method=method, **data)

    @staticmethod
    def _type_check(_type, types):
        if _type in types:
            return True

    @staticmethod
    def get_property_list(_type):
        '''
        return info of properties
        allow GET method only
        allow args:livestream,videoondemand,filedownload,websiteacceleration
        '''
        if not Swiftserve._type_check(_type, Swiftserve.property_types):
            return {'error_detail': u'无法识别的type:{}'.format(_type)}
        return Swiftserve._request('/api/%s/' % _type)

    @staticmethod
    def property_details(_type, **data):
        '''
        GET: return property details info
        POST: create an property
        DELETE: delete an property with property_id
        '''
        method = data.pop('method', 'GET')
        property_id = data.pop('property_id', None)

        if method == 'PUT':
            return {'error_detail': u'该方法不接受PUT请求'}
        elif method == 'POST':
            if data.get('name') is None:
                return {'error_detail': u'name必选，请指定一个名称'}
            if data.get('entity') is None:
                return {'error_detail': u'entity必选，请指定一个entity'}
            if data.get('origin_url') is None:
                return {'error_detail': u'origin_url必选，请指定一个origin_url'}
            active = '/api/{}/'.format(_type)
        elif property_id:
            active = '/api/{_type}/{id}/'.format(_type=_type, id=property_id)
        else:
            return {'error_detail': u'{}方法需要property_id参数'.format(method)}
        if not Swiftserve._type_check(_type,  Swiftserve.property_types):
            return {'error_detail': u'无法识别的type:{}'.format(_type)}
        return Swiftserve._request(active, method=method, **data)

    @staticmethod
    def livestream_delivery_urls():
        pass

    @staticmethod
    def video_on_demand_delivery_urls():
        pass

    @staticmethod
    def date_check_pre_request(acitve, _id, **data):
        year = data.pop('year', None)
        month = data.pop('month', None)
        tag = data.pop('tag', '')
        all_data_check = data.pop('all_data_check', True)

        if all_data_check:
            if not (year and month):
                return {'error_detail': u'缺失year或者month参数'}
        if year:
            year = str(year)
            if not (year.isdigit() and len(year) == 4):
                return {'error_detail': u'错误的year参数，{} 需要满足YYYY'.format(year)}
        if month:
            month = str(month)
            if not (month.isdigit() and len(month) == 2):
                return {'error_detail': u'错误的month参数，{} 需要满足MM'.format(month)}
        format_list = filter(bool, (acitve, str(_id), tag, year, month))
        return Swiftserve._request('/'.join(format_list) + '/', **data)

    @staticmethod
    def log_list(reporting_id, **data):
        '''
        allow GET method only
        return list of log's download urls
        '''
        return Swiftserve.date_check_pre_request('/api/logs',
                                                 reporting_id, all_data_check=False, **data)

    @staticmethod
    def traffic_usage_info(entity_id, entity_only=False, **data):
        '''
        allow GET method only
        '''
        resp = Swiftserve.date_check_pre_request('/api/entity', entity_id,
                                                 tag='traffic', **data)
        if entity_only:
            entity_traffic = [record for record in resp
                              if record.get('is_entity') == 'true']
            return entity_traffic or resp
        else:
            return resp

    @staticmethod
    def daily_per_property_traffic_stats(property_id, **data):
        return Swiftserve.date_check_pre_request('/api/leaf', property_id,
                                                 tag='traffic', **data)

    @staticmethod
    def daily_per_FTP_account_disk_usage_stats(origin_account_id, **data):
        return Swiftserve.date_check_pre_request('/api/du_history',
                                                 origin_account_id, **data)

    @staticmethod
    def invalidations(_type, _id, **data):
        if not Swiftserve._type_check(_type, Swiftserve.invalidation_type):
            return {'error_detail': u'无法识别的type:{}'.format(_type)}
        method = data.get('method', 'GET')
        if method not in ['GET', 'POST']:
            return {'error_detail': u'该方法不接受{}请求'.format(method)}

        return Swiftserve._request('/api/{_type}/{_id}/invalidations'.format(_type=_type, _id=_id), **data)
