# 获取虎牙直播的真实流媒体地址。
# 现在虎牙直播链接需要密钥和时间戳了


import requests
import re
import base64
import urllib.parse
import hashlib
import time
import json

def get_rooms():
    url = 'https://www.huya.com/cache.php?m=LiveList&do=getLiveListByPage&tagAll=0&page=2'
    
    rooms = []
    response = requests.get(url)
    response.encoding = 'utf-8'
    assert response.status_code == 200  # 断言一下状态码是200
    json_dict = json.loads(response.text)  # 把响应的json数据转换成python的字典
    infos = json_dict['data']['datas']   # 每一页的直播间数据全在这里面，一共120个
    for info in infos:
        item = {}
        item['标题'] = info['introduction']
        item['类型'] = info['gameFullName']
        item['主播'] = info['nick']
        item['网址'] = 'https://www.huya.com/' + info['profileRoom']
        item['人气'] = info['totalCount']
        item['rid']  = info['profileRoom']
        
        #print(item)
        rooms.append(item)
        
    return rooms
    
def live(e):
    i, b = e.split('?')
    r = i.split('/')
    s = re.sub(r'.(flv|m3u8)', '', r[-1])
    c = b.split('&', 3)
    c = [i for i in c if i != '']
    n = {i.split('=')[0]: i.split('=')[1] for i in c}
    fm = urllib.parse.unquote(n['fm'])
    u = base64.b64decode(fm).decode('utf-8')
    p = u.split('_')[0]
    f = str(int(time.time() * 1e7))
    l = n['wsTime']
    t = '0'
    h = '_'.join([p, t, s, f, l])
    m = hashlib.md5(h.encode('utf-8')).hexdigest()
    y = c[-1]
    url = "{}?wsSecret={}&wsTime={}&u={}&seqid={}&{}".format(i, m, l, t, f, y)
    return url


def get_real_url(room_id):
    try:
        room_url = 'https://m.huya.com/' + str(room_id)
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/75.0.3770.100 Mobile Safari/537.36 '
        }
        response = requests.get(url=room_url, headers=header).text
        liveLineUrl = re.findall(r'liveLineUrl = "([\s\S]*?)";', response)[0]
        if liveLineUrl:
            if 'replay' in liveLineUrl:
                return '直播录像：https:' + liveLineUrl
            else:
                liveLineUrl = live(liveLineUrl)
                real_url = ["https:" + liveLineUrl, "https:" + re.sub(r'_\d{4}.m3u8', '.m3u8', liveLineUrl)]
        else:
            real_url = '未开播或直播间不存在'
    except:
        real_url = '未开播或直播间不存在'
    return real_url

rooms = get_rooms()
if rooms != None and len(rooms) > 0:
    for i in range(0,5):
        if i < len(rooms):
            r = rooms[i]
            rid = r['rid']
            real_url = get_real_url(rid)
            print('room #%s, %s, url: %s' % (r['标题'], rid, real_url[0]))
        else:
            break
            
#rid = input('请输入虎牙房间号：\n')
#real_url = get_real_url(rid)
#print('该直播间源地址为：')
#print(real_url)
