# AcFun直播：https://live.acfun.cn/
# 默认最高画质
import requests
import json
import re
from lxml import etree

def acfun(rid):
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': '_did=H5_',
        'referer': 'https://m.acfun.cn/'
    }
    url = 'https://id.app.acfun.cn/rest/app/visitor/login'
    data = 'sid=acfun.api.visitor'
    with requests.Session() as s:
        res = s.post(url, data=data, headers=headers).json()
    userid = res['userId']
    visitor_st = res['acfun.api.visitor_st']

    url = 'https://api.kuaishouzt.com/rest/zt/live/web/startPlay'
    params = {
        'subBiz': 'mainApp',
        'kpn': 'ACFUN_APP',
        'kpf': 'PC_WEB',
        'userId': userid,
        'did': 'H5_',
        'acfun.api.visitor_st': visitor_st
    }
    data = 'authorId={}&pullStreamType=FLV'.format(rid)
    res = s.post(url, params=params, data=data, headers=headers).json()
    if res['result'] == 1:
        data = res['data']
        videoplayres = json.loads(data['videoPlayRes'])
        liveadaptivemanifest, = videoplayres['liveAdaptiveManifest']
        adaptationset = liveadaptivemanifest['adaptationSet']
        representation = adaptationset['representation'][-1]
        real_url = representation['url']
        return real_url
    else:
        raise Exception('直播已关闭')


if __name__ == '__main__':
    url = 'https://live.acfun.cn/?ft=1&fi=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'
    }
    html = requests.get(url=url, headers=headers).text
    
    selector = etree.HTML(html)
    upinfos = selector.xpath("//div[@class='up-info']//h1[@class='list-content-title']/a")
    for upinfo in upinfos:
        url = upinfo.xpath("./@href")[0]
        title = upinfo.xpath("./@title")[0]
        
        # /live/36172619
        match = re.match(r'/live/(\d+)', url)
        if match:
            rid = match.group(1)
            play_url = acfun(rid)
            print(url, rid, title, play_url)
    
    #r = input('输入AcFun直播间号：\n')
    #print(acfun(r))
