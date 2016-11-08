# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# Date: 2016-08-30
# auth: nevermore


import hmac
import json
import time
import hashlib
import base64
import urllib
import xmltodict
import urllib.request
import urllib.parse
from xml.dom import minidom
from datetime import datetime
from django.conf import settings
from bs4 import BeautifulSoup


class ForbiddenException(Exception):
    pass


def _convert(val):
    if isinstance(val, basestring):
        if val.isdigit():
            return int(val)
        try:
            return float(val)
        except:
            pass
    return val


class NodeTraverser(object):

    def __init__(self, node):
        self.node = node

    def keys(self):
        return self.node._attrs.keys()

    def children_keys(self):
        result = []
        for child in self.node.childNodes:
            result.append(child.tagName)
        return result

    @property
    def children(self):
        return [NodeTraverser(n) for n in self.node.childNodes]

    def getattribute(self, name):
        return self.node.getAttribute(name)

    def getnode(self, name):
        for child in self.node.childNodes:
            if child.tagName == name:
                return NodeTraverser(child)

    def __getattr__(self, name):
        if type(name) == int or name.isdigit():
            return self.children[int(name)]
        if self.node.hasAttribute(name):
            return self.getattribute(name)
        return self.getnode(name)
    __getitem__ = __getattr__

    @property
    def val(self):
        if self.node.nodeType == self.node.TEXT_NODE:
            return _convert(self.node.data)
        for node in self.node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                return _convert(node.wholeText)
        return None

    def html(self):
        return self.node.toxml()


class XMLWrapper(object):

    def __init__(self, xml):
        self.xml = xml
        self.dom = minidom.parseString(xml)
        setattr(self, self.dom.documentElement.tagName,
                NodeTraverser(self.dom.documentElement))


class Level3Service(object):

    """
    Parameters :
        key_id(required)
        secret(required)
        service_url : optional that defaults to https://mediaportal.level3.com:443
        content_type : optional that defaults to text/xml
        resource : optional that defaults to /api/v1.0
        method : optional that defaults to GET
        wrap : optional that defaults to True. Will wrap the results in a friendly
            class that allows you to easily retrieve the values from the xml(see example).

    Example Usages:

    >>> from level3 import Level3Service
    >>> service = Level3Service('<key id>', '<secret>')
    >>> result = service('rtm/<access group>', {'serviceType' : 'caching', 'accessGroupChildren' : 'false', 'geo' : 'none' })
    >>> result.accessGroup.missPerSecond.val
    50.67
    >>> result.accessGroup.metros[0].name
    Atlanta, GA
    >>> result.accessGroup.metros[0].region
    North America
    >>> result.accessGroup.metros[0].requestsPerSecond.val
    600.45
    """

    def __init__(self, service_url="",
                 content_type='text/json', resource="/key/v1.0", method="GET",
                 wrap=False, json=False, bs4=True):
        self.key_id = settings.LEVEL3_APIKEY
        self.secret = settings.LEVEL3_SECRET
        self.service_url = service_url
        self.content_type = content_type
        self.resource = resource
        self.method = method
        self.json = json
        self.bs4 = bs4

        self.current_date = datetime.utcnow()
        self.wrap = wrap

    def gen_new_date(self):
        self.current_date = datetime.utcnow()

    @property
    def formatted_date(self):
        return self.current_date.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def generate_auth_string(self, method):
        authstring = "%s\n%s/%s/%s\n%s\n%s\n" % (
            self.formatted_date,
            self.service_url.rstrip('/'),
            self.resource.strip('/'),
            method.strip('/'),
            self.content_type,
            self.method
        )
        hash = hmac.new(
            self.secret.encode(), authstring.encode(), hashlib.sha1).digest()
        return "MPA %s:%s" % (self.key_id, base64.b64encode(hash).decode())

    def __call__(self, active, options={}, body={}):
        self.gen_new_date()
        url = "https://ws.level3.com" + \
            self.service_url.rstrip('/') + '/' + self.resource.strip('/')
        url = url + '/' + active.strip('/')
        headers = {
            'Date': self.formatted_date,
            'Authorization': self.generate_auth_string(active),
            'Content-Type': self.content_type,
            'Accept': self.content_type
        }
        req_opts = {'headers': headers}

        if options:
            encoded = urllib.parse.urlencode(options)
            if self.method.upper() == 'GET':
                url += '?' + encoded
            else:
                req_opts['data'] = encoded
        if body:
            req_opts['data'] = json.dumps(body).encode()

        req = urllib.request.Request(url, **req_opts)
        try:
            result = urllib.request.urlopen(req)
        except urllib.request.HTTPError as ex:
            if ex.getcode() == 403:
                raise ForbiddenException(
                    "something went wrong authorizing this request. %s" % str(ex.readlines()))
            else:
                e = ex.readlines()
                if 'No usage data was found for specified criteria.' in str(e):
                    raise RuntimeError(str(e))
                else:
                    return {'message': str(e)}
        data = result.read()
        if self.bs4:
            soup = BeautifulSoup(data, "html.parser")
            return soup
        if self.content_type == 'text/json':
            return json.loads(data.decode())
        if self.wrap:
            data = XMLWrapper(data)
            if self.json:
                return xmltodict.parse(data.xml)
        elif self.json:
            return xmltodict.parse(data)
        else:
            return data


class Level3:

    @staticmethod
    def apikey():
        return Level3Service(resource='key/v1.0')('')

    @staticmethod
    def accessGroups():
        return Level3Service(resource='accessGroups/v1.0', json=True, bs4=False,content_type='text/json')('')

    @staticmethod
    def servicesHierarchy(active, content_type='text/xml', options={}):
        '''
        active: /(AG)/
                or /(AG)/(SCID)/
                or /(AG)/(SCID)/(NI)/
        Example: '268176/BBKN17110/cdn.exrqs.com'
        '''
        return Level3Service(resource='services/cdn/v1.0', content_type=content_type)(active, options=options)

    @staticmethod
    def RTM(active, options={'serviceType': 's'}):
        '''
        options:
            Streaming:
                serviceType: s
                verbose: true | false
            Caching:
                serviceType: c
                property: true
                geo: none|metro|region|clientRegion
        '''
        return Level3Service(resource='rtm/cdn/v1.0')(active, options=options)

    # @staticmethod
    # def CachingRTM(active, options={'serviceType': 'streaming'}):
    #     return Level3Service(resource='rtm/cdn/v1.0')(active, options=options)

    @staticmethod
    def usage_report(active, date_from, date_to, options={}, json=True, bs4=False):
        if int(date_to) > time.time():
            raise Exception('Unexcept time %s' % date_to)
        try:
            date_from = time.strftime(
                "%Y%m%d%H%M", time.localtime(date_from - 8 * 3600))
            date_to = time.strftime("%Y%m%d%H%M", time.localtime(date_to - 8 * 3600))
        except:
            return {'error_detail': 'cannot recognition date,{},{}'.format(date_from, date_to)}
        default_options = {'dateFrom': date_from,
                           'dateTo': date_to,
                           'serviceType': options.get('serviceType', 'caching'),
                           'dataInterval': options.get('dataInterval', '5min'),
                           }
        default_options.update(options)
        # if options['dataInterval'] == '5min':
        # try:
        return Level3Service(resource='usage/cdn/v1.0/',
                             content_type='text/xml', json=json,
                             bs4=bs4)(active, options=default_options)
        # except RuntimeError:
        #     return {}

    @staticmethod
    def invalidations(active, method='POST', options={'force': 0}, body={}):
        '''
        options.update(
            {"paths": ["/fake/test/path/foo.jpg", "/fake/test/path/foo.mpeg"]})
        '''
        return Level3Service(resource='invalidations/v1.0/',
                             method=method, content_type='text/xml',
                             json=True, bs4=False)(active,
                                                   options=options,
                                                   body=body)


# date_from = int(time.mktime(time.strptime(date_from, "%Y%m%d%H%M%S")))
# date_to = int(time.mktime(time.strptime(date_to, "%Y%m%d%H%M%S")))
