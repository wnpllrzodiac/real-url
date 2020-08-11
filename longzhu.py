# 获取龙珠直播的真实流媒体地址，默认最高码率。

import requests
import re
from lxml import etree

def get_real_url(rid):
    try:
        response = requests.get('http://m.longzhu.com/' + str(rid)).text
        roomId = re.findall(r'roomId = (\d*);', response)[0]
        response = requests.get('http://livestream.longzhu.com/live/getlivePlayurl?roomId={}&hostPullType=2&isAdvanced=true&playUrlsType=1'.format(roomId)).json()
        real_url = response.get('playLines')[0].get('urls')[-1].get('securityUrl')
    except:
        real_url = '直播间不存在或未开播'
    return real_url

def get_longzhu_room_id():
    rids = []
    
    url = 'http://longzhu.com/channels/all'
    try:
        html = requests.get(url).text
        selector = etree.HTML(html)
        urls = selector.xpath("//a[@class='livecard']/@href")
        for l in urls:
            # //star.longzhu.com/2440233?from=challcontent
            match = re.search(r'/(\d+)\?', l)
            if match:
                rid = match.group(1)
                rids.append(rid)
        return rids
    except Exception as e:
        print(expr(e))
    return None
        
rids = get_longzhu_room_id()
for rid in rids:
    real_url = get_real_url(rid)
    print('%s: %s' % (rid, real_url))

#rid = input('请输入龙珠直播房间号：\n')
#real_url = get_real_url(rid)
#print('该直播间源地址为：')
#print(real_url)
