# 获取斗鱼直播间的真实流媒体地址，默认最高画质。
import requests
import re
import execjs
import time
import hashlib


class DouYu:

    def __init__(self, rid):
        # 房间号通常为1~7位纯数字，浏览器地址栏中看到的房间号不一定是真实rid.
        self.did = '10000000000000000000000000001501'
        self.t10 = str(int(time.time()))
        self.t13 = str(int((time.time() * 1000)))

        self.s = requests.Session()
        self.res = self.s.get('https://m.douyu.com/' + str(rid)).text
        result = re.search(r'rid":(\d{1,7}),"vipId', self.res)

        if result:
            self.rid = result.group(1)
        else:
            raise Exception('房间号错误')

    @staticmethod
    def md5(data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def get_pre(self):
        url = 'https://playweb.douyucdn.cn/lapi/live/hlsH5Preview/' + self.rid
        data = {
            'rid': self.rid,
            'did': self.did
        }
        auth = DouYu.md5(self.rid + self.t13)
        headers = {
            'rid': self.rid,
            'time': self.t13,
            'auth': auth
        }
        res = self.s.post(url, headers=headers, data=data).json()
        error = res['error']
        data = res['data']
        key = ''
        if data:
            rtmp_live = data['rtmp_live']
            key = re.search(r'(\d{1,7}[0-9a-zA-Z]+)_?\d{0,4}(/playlist|.m3u8)', rtmp_live).group(1)
        return error, key

    def get_js(self):
        result = re.search(r'(function ub98484234.*)\s(var.*)', self.res).group()
        func_ub9 = re.sub(r'eval.*;}', 'strc;}', result)
        js = execjs.compile(func_ub9)
        res = js.call('ub98484234')

        v = re.search(r'v=(\d+)', res).group(1)
        rb = DouYu.md5(self.rid + self.did + self.t10 + v)

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace('CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        js = execjs.compile(func_sign)
        params = js.call('sign', self.rid, self.did, self.t10)
        params += '&ver=219032101&rid={}&rate=-1'.format(self.rid)

        url = 'https://m.douyu.com/api/room/ratestream'
        res = self.s.post(url, params=params).text
        key = re.search(r'(\d{1,7}[0-9a-zA-Z]+)_?\d{0,4}(.m3u8|/playlist)', res).group(1)

        return key

    def get_real_url(self):
        error, key = self.get_pre()
        if error == 0:
            pass
        elif error == 102:
            raise Exception('房间不存在')
        elif error == 104:
            raise Exception('房间未开播')
        else:
            key = self.get_js()

        return "http://tx2play1.douyucdn.cn/live/{}.flv?uuid=".format(key)


if __name__ == '__main__':
    while True:
        try:
            res_f = requests.get(url='https://www.douyu.com/gapi/rkc/directory/0_0/1', timeout=5).json()
            live_page = res_f.get('data').get('pgcnt')
            print('page count: %d' % live_page)
            
            code = res_f.get('code')
            msg = res_f.get('msg')
            if code == 0:
                rl = res_f.get('data').get('rl') # room list
                show_cnt = 10
                for room in rl:
                    room_id = room.get('rid')
                    room_name = room.get('rn')
                    s = DouYu(room_id)
                    play_url = s.get_real_url()
                    if '直播间未开播或不存在' in play_url:
                        continue
                        
                    print('%d %s %s' % (room_id, room_name, play_url))
                    show_cnt -= 1
                    
                    if show_cnt < 0:
                        break
                #res_l = requests.get(url='https://www.douyu.com/gapi/rkc/directory/0_0/' + str(live_page), timeout=5).json()
                break
                
            print('failed to get room info: %s' % msg)
        except requests.exceptions.RequestException:
            print(get_tt() + ' DOUYU HTTP ERROR AND RETRY')
