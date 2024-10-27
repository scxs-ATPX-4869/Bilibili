from Login import login
import videoParse
import requests
import json
from json.decoder import JSONDecodeError
import os
from tqdm import tqdm


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

def download_streamMedia(response, fileName:str, MediaFormat:str): # Download stream media with process bar
    with open(f"{fileName}/{fileName}.{MediaFormat}", 'wb') as f:
        with tqdm(total=int(response.headers.get('content-length', 0)), unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=f"{fileName}.{MediaFormat}:") as bar:
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

def meida_download(source, supportFormats, mediaType, headers, fileName, info):
    sourceChose = input('客官是否需要选择视频质量，默认为可下载的最高质量（y/n）：').lower()
    ifIDChoosed = sourceChose == 'y'

    urlToDownload, idChoosed = confirm_id_to_download(source=source, supportFormats=supportFormats, choose=ifIDChoosed) # Confirm the url of source and id of file formate
    fileFormat = judge_fileType(info[mediaType]['source'][idChoosed]['mimeType']) # Confirm the file formate
    response = requests.get(url=urlToDownload, headers=headers, stream=True) # Try to get a response of audio
    
    if response.status_code != requests.codes.ok: # Choose backupUrl to download audio if baseUrl raise error
        backupUrl = iter(source[idChoosed]['backupUrl'])
        while response.status_code != requests.codes.ok:
            try:
                urlToDownload = next(backupUrl)
                response = requests.get(url=urlToDownload, headers=headers, stream=True)
            except StopIteration:
                break
    if response.status_code == requests.codes.ok:
        download_streamMedia(response=response, fileName=fileName, MediaFormat=fileFormat)
    else:
        print('下载失败', '\n',
              'response code:', response.status_code, '\n',
              'response body:', response.text,
              )


with open('Bilibili_scrape/data/Cookies/Cookies.json', 'r') as f: # Get login cookie if cookie is saved in Bilibili_scrape/data/Cookies/Cookies.json
    try:
        cookie = json.loads(f.read())
    except JSONDecodeError:
        login()
        cookie = json.loads(f.read())
headers = {
    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Cookie": load_Cookies(cookies=cookie)
}

url_checkLoginState = "https://api.bilibili.com/x/space/user/setting/list"
while True: # Check login state. If not logged in, login by scaning login QR code
    response = requests.get(url=url_checkLoginState, headers=headers)
    login_code = json.loads(response.text)['code']
    if login_code == -101:
        login()
        headers = {
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Cookie": load_Cookies(cookies=cookie)
        }
    elif login_code == 0:
        print("登录成功")
        break

video_url = "https://www.bilibili.com/video/BV16Wy5YfEjb/" # 视频的B站链接
info_path = videoParse.get_information(video_url, headers=headers)
with open(info_path, 'r') as f:
    info = json.loads(f.read())

fileName = info['title']
video_supportFormats = info['video']['supportFormats']
video_source = info['video']['source']
audio_supportFormats = info['audio']['supportFormats']
audio_source = info['audio']['source']

try:
    os.mkdir(fileName)
except FileExistsError:
    print("文件夹已存在")

# ========================= video =============================
meida_download(source=video_source, supportFormats=video_supportFormats, mediaType='video', headers=headers, fileName=fileName, info=info)

# ========================= audio =============================
meida_download(source=audio_source, supportFormats=audio_supportFormats, mediaType='audio', headers=headers, fileName=fileName, info=info)



