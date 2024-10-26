from Login import login
import videoParse
import requests
import json
import os
from tqdm import tqdm
import asyncio

def load_Cookies(cookies:dict, keys:list=None) -> str:
    """
    This method will connect cookie with "keys"
    """
    string = ""
    if keys == None:
        for key, value in cookies.items():
            string += f"{key}={value};"
    else:
        for key in keys:
            string += f"{key}={cookies[key]};"
    
    return string

def download_streamMedia(response, fileName:str, MediaStyle:str): # Download stream media with process bar
    with open(f"{fileName}/{fileName}.{MediaStyle}", 'wb') as f:
        with tqdm(total=int(response.headers.get('content-length', 0)), unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=f"{fileName}.{MediaStyle}:") as bar:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)
                bar.update(len(chunk))

def judge_fileType(mimeType:str) -> str:
    '''
    Judge the file type by mimeType
    '''
    if 'video' in mimeType:
        return 'mp4'
    elif 'audio' in mimeType:
        return 'mp3'

def confirm_id_to_download(source:dict, supportFormats:dict, choose:bool=False):
    '''
    Confirm the id that user wants to download
    '''
    if choose == False:
        id = tuple(supportFormats.keys())[0]
    else:
        while True:
            print("客官可以选择的音频清晰度编号：", supportFormats)
            id = input("请客官输入想下载的音频编号：")
            if id in supportFormats.keys():
                break
            else:
                print("没有客官需要的音频清晰度编号，请重新输入(-3-)")
    urlToDownload = source[id]['baseUrl']

    return urlToDownload, id

# with open('Bilibili_scrape/data/Cookies/Cookies.json', 'r') as f: # Get login cookie if cookie is saved in Bilibili_scrape/data/Cookies/Cookies.json
    # cookie = json.loads(f.read())
headers = {
    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
}
    # "Cookie": load_Cookies(cookies=cookie)
"""
url_checkLoginState = "https://api.bilibili.com/x/space/user/setting/list"
while True: # Check login state. If not logged in, login by scaning login QR code
    response = requests.get(url=url_checkLoginState, headers=headers)
    login_code = json.loads(response.text)['code']
    if login_code == -101:
        login()
    elif login_code == 0:
        headers = {
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Cookie": load_Cookies(cookies=cookie)
        }
        print("登录成功")
        break
"""
video_url = "https://www.bilibili.com/video/BV11zyfY4EVy/" # 视频的B站链接
info_path = videoParse.get_information(video_url)
with open(info_path, 'r') as f:
    info = json.loads(f.read())

fileName = info['title']

try:
    os.mkdir(fileName)
except FileExistsError:
    print("文件夹已存在")

# ========================= video =============================
video_supportFormats = info['video']['supportFormats']
video_source = info['video']['source']

sourceChose = input('客官是否需要选择视频质量，默认为可下载的最高质量（y/n）：').lower()
ifIDChoosed = sourceChose == 'y'

urlToDownload, idChoosed = confirm_id_to_download(source=video_source, supportFormats=video_supportFormats, choose=ifIDChoosed) # Confirm the url of source and id of file formate
fileStyle = judge_fileType(info['video']['source'][idChoosed]['mimeType']) # Confirm the file formate
video_response = requests.get(url=urlToDownload, headers=headers, stream=True) # Try to get a response of audio
if video_response.status_code != requests.codes.ok: # Choose backupUrl to download audio if baseUrl raise error
    backupUrl = iter(video_source[idChoosed]['backupUrl'])
    while video_response.status_code != requests.codes.ok:
        try:
            urlToDownload = next(backupUrl)
            video_response = requests.get(url=urlToDownload, headers=headers, stream=True)
        except StopIteration:
            break

download_streamMedia(response=video_response, fileName=fileName, MediaStyle=fileStyle)

# ========================= audio =============================
audio_supportFormats = info['audio']['supportFormats']
audio_source = info['audio']['source']

sourceChose = input('客官是否需要选择视频质量，默认为可下载的最高质量（y/n）：').lower()
ifIDChoosed = sourceChose == 'y'

urlToDownload, idChoosed = confirm_id_to_download(source=audio_source, supportFormats=audio_supportFormats, choose=ifIDChoosed) # Confirm the url of source and id of file formate
fileStyle = judge_fileType(info['audio']['source'][idChoosed]['mimeType']) # Confirm the file formate
audio_response = requests.get(url=urlToDownload, headers=headers, stream=True) # Try to get a response of audio

if audio_response.status_code != requests.codes.ok: # Choose backupUrl to download audio if baseUrl raise error
    backupUrl = iter(audio_source[idChoosed]['backupUrl'])
    while audio_response.status_code != requests.codes.ok:
        try:
            urlToDownload = next(backupUrl)
            audio_response = requests.get(url=urlToDownload, headers=headers, stream=True)
        except StopIteration:
            break
if audio_response.status_code == requests.codes.ok: # Start to download audio
    download_streamMedia(response=audio_response, fileName=fileName, MediaStyle=fileStyle)
else:
    print('下载失败', 'audio_response code:', audio_response.status_code)




