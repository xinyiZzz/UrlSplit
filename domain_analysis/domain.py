#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Name: 对URL进行分割，基于urlparse, publicsuffix, urllib编写
Author：XinYi 609610350@qq.com
Time：2015.9.3

域名解释：例如www.baidu.com，其中baidu.com，是网站真正的域名，www是所用的万维网服务名。
        其中服务名可由网站自定义，例如除www外，还有bbs、news等常见服务名，或者
        自定义的isis.astrogeology，其长度自定。
        域名中第一个字段为主机域名，余下的字段为顶级域名，主机域名只能为一个字符串，
        所以只能占用一个字段，顶级域名的种类有限，并不断更新
# from tld import get_tld # 准确度太低
# domain = get_tld(url)
'''
from urlparse import urlparse
import codecs
from publicsuffix import PublicSuffixList
from urllib import splitport
from os.path import join as pjoin
import re

PSL_FILE = ''
PSL = ''

def open_public_suffix_list(file_dir=''):
    global PSL_FILE
    global PSL
    PSL_FILE = codecs.open(pjoin(file_dir, 'public_suffix_list.dat'), encoding='utf8')
    PSL = PublicSuffixList(PSL_FILE)

def geturlip(url):
    '''
    判断URL中是否包含IP
    '''   
    match = re.search(r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))', url)
    if match:
        return 1
    else:
        return 0

def domain_split(server_domain):
    '''
    server_domain为网站所用服务名+域名
    分割域名, 得到前缀(服务名)、主机域名、后缀(顶级域名)
        输入www.baidu.com，输出'www', 'baidu', 'com'
        输入isis.astrogeology.usgs.gov，输出'isis.astrogeology', 'usgs', 'gov'
        输入172.31.137.240，输出'', '172.31.137.240', ''
    '''
    if PSL_FILE == '':
        open_public_suffix_list()
    domain = PSL.get_public_suffix(server_domain)
    # 取域名的第一个字段，即第一个'.'之前的为主机域名, 后面为顶级域名，前面为所使用的服务
    if '.' in domain:
        server = server_domain[:-len(domain)]
        host = domain[:domain.index('.')]
        top = domain[domain.index('.'):]
    else:  # 说明域名分割失败，此时全部当作主机域名
        server = ''
        host = server_domain
        top = ''
    return server, host, top

def url_split(url):
    '''
    url分割
    例如: 输入'http://isis.astrogeology.usgs.gov/counterfeit_web/0cur.com/'
    输出：{'host': 'usgs',                       # 主机域名
        'params': '',                            # 参数
        'domain': 'usgs.gov',                    # 完整域名，主机域名+顶级域名
        'query': '',                             # 查询
        'fragment': '',                          # 片段
        'path': '/counterfeit_web/0cur.com/',    # 路径
        'top': '.gov',                           # 顶级域名
        'scheme': 'http',                        # 协议
        'port': '',                              # 端口
        'server': 'isis.astrogeology.'}          # 所用服务，例如www

    '''
    if not url.startswith('http'):  # 补全协议，否则urlparse出错
        url = 'http://' + url
    parts = urlparse(url)
    path = parts.path
    server_domain, port = splitport(parts.netloc)
    if port == None: port = ''
    if geturlip(server_domain):
        # 把IP作为主机域名返回
        server, host, top = '', server_domain, ''
    else:
        # 服务+域名'www.baidu.api.com.cn'切分
        server, host, top = domain_split(server_domain)
        if top == '':
            path = host + path
            host = ''
    return {'scheme': parts.scheme, 'server': server, 'host': host,
            'port': port, 'top': top, 'path': path, 'domain': host + top,
            'params': parts.params, 'query': parts.query, 'fragment': parts.fragment}

if __name__ == '__main__':
    print url_split('http://isis.astrogeology.usgs.gov:8080/counterfeit_web/0cur.com/')
    print url_split('details.php?bulilding+fef=23fsda234fasdfzxcvafasdfasdf')
    print url_split('www.baidu.fffffffffff/fwefsaf/fhewaofdzxcv/erasfasd')
    print url_split('172.31.154.5555/asf/sdfewr/fasfd')
    print url_split('/asf/sdfewr/fasfd/ffff')

