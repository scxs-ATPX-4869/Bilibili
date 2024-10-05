import time
import random
import struct
import io
import hmac
import hashlib
import requests
import json

# ------------------------------ generate _uuid -----------------------------
def generate_uuid() -> str:
    '''
    generate the _uuid of Cookies
    '''
    t = int(time.time() * 1000) % 100000
    mp = list("123456789ABCDEF") + ["10"]
    pck = [8, 4, 4, 4, 12]
    gen_part = lambda x: "".join([random.choice(mp) for _ in range(x)])

    return "-".join([gen_part(l) for l in pck]) + str(t).ljust(5, "0") + "infoc"

# ------------------------------ generate buvid_fp -----------------------------
MOD = 1 << 64

def rotate_left(x: int, k: int) -> int:
    '''
    You don't need to use this method, this mehtod is used in generate_buvid_fp()
    '''
    bin_str = bin(x)[2:].rjust(64, "0")
    return int(bin_str[k:] + bin_str[:k], base=2)

def fmix64(k: int) -> int:
    '''
    You don't need to use this method, this mehtod is used in generate_buvid_fp()
    '''
    C1 = 0xFF51_AFD7_ED55_8CCD
    C2 = 0xC4CE_B9FE_1A85_EC53
    R = 33
    tmp = k
    tmp ^= tmp >> R
    tmp = tmp * C1 % MOD
    tmp ^= tmp >> R
    tmp = tmp * C2 % MOD
    tmp ^= tmp >> R
    return tmp

def murmur3_x64_128(source: io.BufferedIOBase, seed: int) -> str:
    '''
    You don't need to use this method, this mehtod is used in generate_buvid_fp()
    '''
    C1 = 0x87C3_7B91_1142_53D5
    C2 = 0x4CF5_AD43_2745_937F
    C3 = 0x52DC_E729
    C4 = 0x3849_5AB5
    R1, R2, R3, M = 27, 31, 33, 5
    h1, h2 = seed, seed
    processed = 0
    while 1:
        read = source.read(16)
        processed += len(read)
        if len(read) == 16:
            k1 = struct.unpack("<q", read[:8])[0]
            k2 = struct.unpack("<q", read[8:])[0]
            h1 ^= (rotate_left(k1 * C1 % MOD, R2) * C2 % MOD)
            h1 = ((rotate_left(h1, R1) + h2) * M + C3) % MOD
            h2 ^= rotate_left(k2 * C2 % MOD, R3) * C1 % MOD
            h2 = ((rotate_left(h2, R2) + h1) * M + C4) % MOD
        elif len(read) == 0:
            h1 ^= processed
            h2 ^= processed
            h1 = (h1 + h2) % MOD
            h2 = (h2 + h1) % MOD
            h1 = fmix64(h1)
            h2 = fmix64(h2)
            h1 = (h1 + h2) % MOD
            h2 = (h2 + h1) % MOD
            return (h2 << 64) | h1
        else:
            k1 = 0
            k2 = 0
            if len(read) >= 15:
                k2 ^= int(read[14]) << 48
            if len(read) >= 14:
                k2 ^= int(read[13]) << 40
            if len(read) >= 13:
                k2 ^= int(read[12]) << 32
            if len(read) >= 12:
                k2 ^= int(read[11]) << 24
            if len(read) >= 11:
                k2 ^= int(read[10]) << 16
            if len(read) >= 10:
                k2 ^= int(read[9]) << 8
            if len(read) >= 9:
                k2 ^= int(read[8])
                k2 = rotate_left(k2 * C2 % MOD, R3) * C1 % MOD
                h2 ^= k2
            if len(read) >= 8:
                k1 ^= int(read[7]) << 56
            if len(read) >= 7:
                k1 ^= int(read[6]) << 48
            if len(read) >= 6:
                k1 ^= int(read[5]) << 40
            if len(read) >= 5:
                k1 ^= int(read[4]) << 32
            if len(read) >= 4:
                k1 ^= int(read[3]) << 24
            if len(read) >= 3:
                k1 ^= int(read[2]) << 16
            if len(read) >= 2:
                k1 ^= int(read[1]) << 8
            if len(read) >= 1:
                k1 ^= int(read[0])
            k1 = rotate_left(k1 * C1 % MOD, R2) * C2 % MOD
            h1 ^= k1

def generate_buvid_fp(key: str, seed:int=31):
    '''
    generate the buvid_fp of Cookies\n
    :param key: your browser's fingerprint
    '''
    source = io.BytesIO(bytes(key, "ascii"))
    m = murmur3_x64_128(source, seed)
    return "{}{}".format(
        hex(m & (MOD - 1))[2:], hex(m >> 64)[2:]
    )

# ------------------------------ get bili_ticket -----------------------------
def hmac_sha256(key, message):
    """
    使用HMAC-SHA256算法对给定的消息进行加密
    :param key: 密钥
    :param message: 要加密的消息
    :return: 加密后的哈希值
    """
    # 将密钥和消息转换为字节串
    key = key.encode('utf-8')
    message = message.encode('utf-8')

    # 创建HMAC对象，使用SHA256哈希算法
    hmac_obj = hmac.new(key, message, hashlib.sha256)

    # 计算哈希值
    hash_value = hmac_obj.digest()

    # 将哈希值转换为十六进制字符串
    hash_hex = hash_value.hex()

    return hash_hex

def get_bili_ticket(bili_jct:str):
    o = hmac_sha256("XgwSnGZ1p",f"ts{int(time.time())}")
    url = "https://api.bilibili.com/bapis/bilibili.api.ticket.v1.Ticket/GenWebTicket"
    params = {
        "key_id":"ec02",
        "hexsign":o,
        "context[ts]":f"{int(time.time())}",
        "csrf": bili_jct
    }
    headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        }
    resp = requests.post(url, params=params,headers=headers).json()
    bili_ticket = resp['data']['ticket']

    return bili_ticket

# ------------------------------ get SESSDATA, bili_jct, DedeUserID, DedeUserID__ckMd5, sid -----------------------------
import qrcode

def generateLoginData(cookies:dict) -> dict:
    '''
    Get the data of generating QRcode and QRcode_key\n
    You need to set Cookies included buvid3, b_nut, b_lsid, _uuid, buvid_fp, buvid4\n
    You can use " data['data']['url'] " to get the url of logining QR code\n
    You can use " QRcode_key = data['data']['qrcode_key'] " to get the qrcode_key
    '''
    headers = {
        "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Cookies" : load_Cookies(cookies=cookies, keys=['buvid3', 'b_nut', 'b_lsid', '_uuid', 'buvid_fp', 'buvid4'])
    }
    urlOfGenerateLoginData = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header&go_url=https:%2F%2Fwww.bilibili.com%2F'
    response = requests.get(url=urlOfGenerateLoginData, headers=headers)
    data = response.json()

    return data

def make_QRcode(content:str):
    '''
    Make a QR code of logining\n
    And save the img as a png file named by time
    '''
    img = qrcode.make(content)
    fileName = str(time.strftime('%Y%m%d_%H_%M_%S')) + '.png'
    img.save(fileName)
    print(f'The QR code of logining is ready. Please check {fileName}')

def checkLoginState(loginingStateCode:str) -> bool:
    '''
    Check the state of logining\n
    You need to set Cookies included buvid3, b_nut, b_lsid, _uuid, buvid_fp, buvid4
    '''
    state = False
    time.sleep(1)
    if loginingStateCode == 86101: # 未扫码
        state = False
        print('未扫码')
    elif loginingStateCode == 86090: # 已扫码但未确认
        state = False
        print('已扫码但未确认')
    elif loginingStateCode == 86038: # 二维码已失效
        state = False
        print("二维码已失效，请重新扫码")
    elif loginingStateCode == 0: # 登录成功
        state = True
        print('登录成功')
    
    return state

def get_SESSDATA_bili_jct_DedeUserID_DedeUserID__ckMd5_sid(qrcode_key:str, cookies:dict) -> dict:
    '''
    get the cookies of SESSDATA, bili_jct, DedeUserID, DedeUserID__ckMd5 and sid\n
    You need to set Cookies included buvid3, b_nut, b_lsid, _uuid, buvid_fp, buvid4
    '''
    check_url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}&source=main-fe-header'
    headers = {
        "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Cookies" : load_Cookies(cookies=cookies, keys=['buvid3', 'b_nut', 'b_lsid', '_uuid', 'buvid_fp', 'buvid4'])
    }
    while True:
        response = requests.get(url=check_url, headers=headers)
        loginingStateCode = response.json()['data']['code']
        if checkLoginState(loginingStateCode=loginingStateCode) == True:
            cookie = dict(response.cookies)
            break
        else:
            continue

    return cookie

# ------------------------------ get buvid3, b_nut -----------------------------
def get_buvid3_b_nut() -> dict:
    '''
    :return a dictionary contain: {"buvid3": Value, "b_nut": Value}
    '''
    target_url = "https://www.bilibili.com/"
    headers = {
        "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer" : "https://www.bilibili.com/"
    }
    response = requests.get(url=target_url, headers=headers)
    response_cookies = dict(response.cookies)

    return response_cookies

# ------------------------------ generate b_lsid -----------------------------
import math
import random

def s(e, t):
    '''
    You don't need to use this method, it is used in get_b_lsid()
    '''
    r = ""
    if len(e) < t:
        r = "0" * (t - len(e))
    return r + e

def o(e):
    '''
    You don't need to use this method, it is used in get_b_lsid()
    '''
    return format(math.ceil(e), 'X')

def blsid1(e):
    '''
    You don't need to use this method, it is used in get_b_lsid()
    '''
    t = ""
    for _ in range(e):
        t += o(16 * random.random())
    return s(t, e)

def getblsid(e):
    '''
    You don't need to use this method, it is used in get_b_lsid()
    '''
    t = o(e)
    return blsid1(8) + '_' + t

def generate_b_lsid() -> str:
    '''
    get b_lsid
    '''
    tim = int(time.time()*1000)
    return getblsid(tim)

# ------------------------------ get buvid4 -----------------------------
def get_buvid4(cookies:dict) -> str:
    '''
    headers should contain User-Agnet and Cookies\n
    These parameters should be included in Cookies: buvid3, b_nut, b_lsid, _uuid, buvid_fp
    '''
    url_getbuvid4 = "https://api.bilibili.com/x/frontend/finger/spi"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Cookies": load_Cookies(cookies=cookies, keys=['buvid3', 'b_nut', 'b_lsid', '_uuid', 'buvid_fp'])
    }
    response = requests.get(url=url_getbuvid4, headers=headers)
    buvid4 = response.json()['data']['b_4']

    return buvid4
    

def load_Cookies(cookies:dict, keys:list=None) -> str:
    '''
    This method will connect cookie with "keys"
    '''
    string = ""
    if keys == None:
        for key, value in cookies.items():
            string += f"{key}={value};"
    else:
        for key in keys:
            string += f"{key}={cookies[key]};"
    
    return string

def login():
    '''
    The block to login Bilibili by QR code
    '''
    buvid3_b_nut = get_buvid3_b_nut()
    cookies = dict(buvid3_b_nut)

    blsid = generate_b_lsid()
    cookies['b_lsid'] = blsid

    uuid = generate_uuid()
    cookies['_uuid'] = uuid

    buvid_fp = generate_buvid_fp(key="07c8f77d1228f7eeade0b414b8d191b8")
    cookies['buvid_fp'] = buvid_fp

    buvid4 = get_buvid4(cookies=cookies)
    cookies['buvid4'] = buvid4

    # get personal cookies
    data = generateLoginData(cookies=cookies)
    make_QRcode(data['data']['url'])
    personal_cookies = get_SESSDATA_bili_jct_DedeUserID_DedeUserID__ckMd5_sid(qrcode_key=data['data']['qrcode_key'], cookies=cookies)
    cookies = dict(**cookies, **personal_cookies)

    bili_ticket = get_bili_ticket(bili_jct=cookies['bili_jct'])
    cookies['bili_ticket'] = bili_ticket

    with open('Bilibili_scrape/data/Cookies/Cookies.json', 'w') as f:
        f.write(json.dumps(cookies, indent='\t'))
    
    print("Login success!")


