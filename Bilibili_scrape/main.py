from Login import login
from videoParse import videoParse
import requests
import json
import os
from tqdm import tqdm


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

url_checkLoginState = "https://api.bilibili.com/x/space/user/setting/list"
while True: # Check login state. If not logged in, login by scaning login QR code
    with open('Bilibili_scrape/data/Cookies/Cookies.json', 'r') as f:
        cookie = json.loads(f.read())
    headers = {
        "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Cookie": load_Cookies(cookies=cookie)
    }
    response = requests.get(url=url_checkLoginState, headers=headers)
    login_code = json.loads(response.text)['code']
    if login_code == -101:
        login()
    elif login_code == 0:
        print("登录成功")
        break

video_url = "https://www.bilibili.com/video/BV1PcpeeDEoW/" # 视频的B站链接
with open('Bilibili_scrape/data/Cookies/Cookies.json', 'r') as f:
        cookie = json.loads(f.read())
    
headers = {
    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Cookie": load_Cookies(cookies=cookie)
}

video = videoParse(video_url=video_url, headers=headers) # 创建一个分析视频的实例
videoTitle = video.video_title() # 获取视频标题
video_styles = video.video_informationOfDifferentDefinition() # 获取视频的视频资源信息
video_supportFormats = video.video_supportFormats() # 获取该视频可下载的清晰度
try:
    os.mkdir(videoTitle)
except FileExistsError:
    print("文件夹已存在")
# ===================== video ============================
while True: # 确定要下载的视频资源链接
    print("客官可以选择的视频清晰度编号：", video_supportFormats)
    idClientChoosed = int(input("请客官输入想下载的视频清晰度编号："))
    if idClientChoosed in video_styles.keys():
        urlToDownload = video_styles[idClientChoosed]['baseUrl']
        break
    else:
        print("没有客官需要的视频清晰度编号，请重新输入(-3-)")

response = requests.get(url=urlToDownload, headers=headers, stream=True)
# print(response.status_code)
if response.status_code != requests.codes.ok:
    backupUrl = iter(video_styles[idClientChoosed]['backupUrl'])
    while response.status_code != requests.codes.ok:
        try:
            urlToDownload = next(backupUrl)
            response = requests.get(url=urlToDownload, headers=headers, stream=True)
            # print(response.status_code)
        except StopIteration:
            break

with open(f"{videoTitle}/{videoTitle}.mp4", 'wb') as f: # 使用进度条下载视频
    with tqdm(total=int(response.headers.get('content-length', 0)), unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=f"{videoTitle}:") as bar:
        for chunk in response.iter_content(chunk_size=4096):
            f.write(chunk)
            bar.update(len(chunk))

# ===================== audio ============================
audio_styles = video.audio_informationOfDifferentBandwidth()
audio_support = video.audio_supportFormats()
while True: # 确定要下载的音频资源链接
    print("客官可以选择的音频编号：", audio_support)
    idClientChoosed = int(input("请客官输入想下载的音频编号："))
    if idClientChoosed in audio_styles.keys():
        urlToDownload = audio_styles[idClientChoosed]['baseUrl']
        break
    else:
        print("没有客官需要的音频编号，请重新输入(-3-)")

response = requests.get(url=urlToDownload, headers=headers, stream=True)
# print(response.status_code)
if response.status_code != requests.codes.ok:
    backupUrl = iter(audio_styles[idClientChoosed]['backupUrl'])
    while response.status_code != requests.codes.ok:
        try:
            urlToDownload = next(backupUrl)
            response = requests.get(url=urlToDownload, headers=headers, stream=True)
            # print(response.status_code)
        except StopIteration:
            break

with open(f"{videoTitle}/{videoTitle}.mp3", 'wb') as f: # 使用进度条下载音频
    with tqdm(total=int(response.headers.get('content-length', 0)), unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=f"{videoTitle}:") as bar:
        for chunk in response.iter_content(chunk_size=4096):
            f.write(chunk)
            bar.update(len(chunk))
