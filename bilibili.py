# 获取哔哩哔哩直播的真实流媒体地址。
# 现在B站直播默认画质改为高清了，更高画质需登陆才可获取。


import requests
import re


def get_real_rid(rid):
    room_url = 'https://api.live.bilibili.com/room/v1/Room/room_init?id=' + str(rid)
    response = requests.get(url=room_url).json()
    data = response.get('data', 0)
    if data:
        live_status = data.get('live_status', 0)
        room_id = data.get('room_id', 0)
    else:
        live_status = room_id = 0
    return live_status, room_id


def get_real_url(rid):
    room = get_real_rid(rid)
    live_status = room[0]
    room_id = room[1]
    if live_status:
        try:
            room_url = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getRoomPlayInfo?room_id={}&play_url=1&mask=1&qn=0&platform=web'.format(room_id)
            response = requests.get(url=room_url).json()
            durl = response.get('data').get('play_url').get('durl', 0)
            real_url = durl[-1].get('url')
        except:
            real_url = '疑似部分国外IP无法GET到正确数据，待验证'
    else:
        real_url = '未开播或直播间不存在'
    return real_url

def get_cat():
    # https://api.live.bilibili.com/room/v1/area/getList?parent_id=6
    pass
    
def get_rooms():
    rooms = []
    
    roomlist_url = 'https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=6&cate_id=0&area_id=0&sort_type=sort_type_150&page=1&page_size=30&tag_version=1'
    response = requests.get(url=roomlist_url).json()
    data = response.get('data', 0)
    if data:
        count = data.get('count', 0)
        list = data.get('list', 0)
        if list:
            for r in list:
                roomid = r['roomid']
                uid = r['uid']
                title = r['title']
                uname = r['uname']
                online = r['online']
                
                print('room %d, uid %d, %s(%s) online: %d, url %s' % (roomid, uid, title, uname, online, get_real_url(roomid)))
                
                rooms.append(roomid)
                
    return rooms
    
r = get_rooms()
if len(r) == 0:
    rid = input('请输入bilibili房间号：\n')
    real_url = get_real_url(rid)
    print('该直播间源地址为：\n' + real_url)
