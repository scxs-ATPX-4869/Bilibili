import time
import json
import re
import requests




class videoParse():
    '''
    This is a class that parses a bilibili video html
    '''
    def __init__(self, video_url:str, headers:dict=None) -> None:
        self.url = video_url
        response = requests.get(url=video_url, headers=headers)
        if response.status_code == requests.codes.ok:
            window_playinfo = re.findall("<script>window.__playinfo__=(.*?)</script>", response.text)[0] # str 获得playinfo的源码
            self.window_playinfo_data = json.loads(window_playinfo) # dict

            window_initial_state = re.findall('''<script>window.__INITIAL_STATE__=(.*?),"ugc_season''', response.text)[0] + "}}" # str 记得对{进行封口 获得INITIAL_STATE中argue_info之前的源码
            self.window_initial_state_data = json.loads(window_initial_state) # dict

    def video_supportFormats(self) -> dict: # 视频支持的清晰度信息
        '''
        获得当前登录状态下的视频清晰度\n
        返回一个字典 {"清晰度ID": "清晰度"}
        '''
        window_playinfo_data = self.window_playinfo_data
        video_supportFormats = window_playinfo_data['data']['support_formats'] # list 每种清晰度及对应的ID和其他信息
        data, supportFormat = dict(), dict()
        for format in video_supportFormats:
            data[format['quality']] = format['new_description']
        for support in self.video_informationOfDifferentDefinition().keys():
            supportFormat[support] = data[support]

        return supportFormat

    def video_duration(self) -> int: # 视频时长，单位：秒（s）
        '''
        获得该视频的时长，单位：秒（s）
        '''
        window_playinfo_data = self.window_playinfo_data
        video_duration = window_playinfo_data['data']['dash']['duration']

        return video_duration

    def video_informationOfDifferentDefinition(self) -> dict: # 该视频的视频资源信息
        '''
        获得该视频的B站视频资源信息\n
        返回一个字典：\n
        {
            'id':{
                'mimeType': Value,
                'baseUrl': Value,
                'backupUrl': Value,
                'bandwidth': Value,
                'width': Value,
                'height': Value,
                'frameRate': Value,
                'codecs': Value
                }
        }
        '''
        data = dict()
        video_informationOfDifferentDefinition = self.window_playinfo_data['data']['dash']['video']
        for versionOfVideo in video_informationOfDifferentDefinition:
            id = versionOfVideo['id']
            if id in data.keys():
                data[id]['backupUrl'].append(versionOfVideo['baseUrl'])
                data[id]['backupUrl'] += versionOfVideo['backupUrl']
            else:
                subData = dict()
                subData['mimeType'] = versionOfVideo['mimeType']
                subData['baseUrl'] = versionOfVideo['baseUrl']
                subData['backupUrl'] = versionOfVideo['backupUrl']
                subData['bandwidth'] = versionOfVideo['bandwidth']
                subData['width'] = versionOfVideo['width']
                subData['height'] = versionOfVideo['height']
                subData['frameRate'] = versionOfVideo['frameRate']
                subData['codecs'] = versionOfVideo['codecs']
                data[id] = subData
        
        return data

    def audio_informationOfDifferentBandwidth(self) -> dict: # 该视频的音频资源信息
        '''
        获得该视频的B站音频资源信息\n
        :return 返回一个字典:
        {\n
            'id':{\n
                'mimeType': Value,\n
                'bandwidth': Value,\n
                'codecs': Value,\n
                'baseUrl': Value,\n
                'backupUrl': Value\n
            }\n
        }
        '''
        audio_informationOfDifferentBandwidth = self.window_playinfo_data['data']['dash']['audio']
        data = dict()
        for versionOfAudio in audio_informationOfDifferentBandwidth:
            id = versionOfAudio['id']
            if id in data.keys():
                continue
            else:
                subData = dict()
                subData['mimeType'] = versionOfAudio['mimeType']
                subData['bandwidth'] = versionOfAudio['bandwidth']
                subData['codecs'] = versionOfAudio['codecs']
                subData['baseUrl'] = versionOfAudio['baseUrl']
                subData['backupUrl'] = versionOfAudio['backupUrl']
                data[id] = subData
        
        return data

    def audio_supportFormats(self) -> dict: # 视频支持的音频信息
        '''
        :return dict:
        {audio_id: bandwidth}
        '''
        data = dict()
        for key in self.audio_informationOfDifferentBandwidth().keys():
            data[key] = self.audio_informationOfDifferentBandwidth()[key]['bandwidth']

        return data

    def audio_dolbyInformation(self) -> dict: # 杜比音效信息（待加工）
        '''
        获得该视频的杜比音效信息
        '''
        window_playinfo_data = self.window_playinfo_data
        audio_dolbyInformation = window_playinfo_data['data']['dash']['dolby']

        return audio_dolbyInformation

    def video_title(self) -> str: # 标题
        '''
        获得该视频的标题
        '''
        window_initial_state_data = self.window_initial_state_data
        video_title = window_initial_state_data['videoData']['title']

        return video_title

    def video_cover(self) -> str: # 视频的封面图片链接
        '''
        获得该视频的封面\n
        返回封面的链接
        '''
        window_initial_state_data = self.window_initial_state_data
        video_cover = window_initial_state_data['videoData']['pic']

        return video_cover

    def video_state(self) -> dict: # 播放量、弹幕数量、评论数量、收藏量、投币数、分享数、点赞数
        '''
        获得该视频的当前情况\n
        返回一个字典：\n
        {
            'aid': Value,
            'view': Value, 播放量
            'danmaku': Value, 弹幕数量
            'reply': Value, 评论数量
            'favorite': Value, 收藏量
            'coin': Value, 投币数
            'share': Value, 分享数
            'now_rank': Value,
            'his_rank': Value,
            'like': Value, 点赞数
            'dislike': Value,
            'evaluation': Value,
            'vt': Value,
            'viewseo': Value
        }
        '''
        window_initial_state_data = self.window_initial_state_data
        video_state = window_initial_state_data['videoData']['stat']
        
        return video_state

    def video_bvid(self) -> str: # bvid
        '''
        获得该视频的bvid
        '''
        window_initial_state_data = self.window_initial_state_data
        video_bvid = window_initial_state_data['bvid']

        return video_bvid
    
    def video_abstract(self) -> str: # 视频简介
        '''
        获得该视频简介
        '''
        window_initial_state_data = self.window_initial_state_data
        video_abstract = window_initial_state_data['videoData']['desc']

        return video_abstract
    
    def video_owner(self) -> dict: # up主ID、名字、头像图片链接
        '''
        获得该视频UP主的信息\n
        :return a dict:
        {
            'mid': up主ID,\n
            'name': up主名字,\n
            'face': up主头像\n
        }
        '''
        window_initial_state_data = self.window_initial_state_data
        video_owner = window_initial_state_data['videoData']['owner']

        return video_owner

    def video_url(self) -> str: # 视频的URL
        return self.url
    
    def video_publicate_date(self) -> str: # 视频的发布时间
        '''
        :return date: weekday, year-month-day hour:minute:second
        '''
        window_initial_state_data = self.window_initial_state_data
        publicate_date = window_initial_state_data['videoData']['pubdate']

        return time.strftime("%A, %Y-%m-%d %H:%M:%S", time.gmtime(publicate_date))

    def video_aid(self) -> str: # 视频的aid
        '''
        Get the aid of video
        '''
        window_initial_state_data = self.window_initial_state_data
        aid = window_initial_state_data['aid']

        return aid

    def video_seasonID(self) -> str: # 视频的合集ID，待加工（如果不存在合集如何处理）
        '''
        Get the season_id of video if it exists
        '''
        window_initial_state_data = self.window_initial_state_data
        seasonID = window_initial_state_data['videoData']['season_id']

        return seasonID


video_url = "https://www.bilibili.com/video/BV1PcpeeDEoW/" # 视频的B站链接
with open('Bilibili_scrape/data/Cookies/Cookies.json', 'r') as f:
        cookie = json.loads(f.read())
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
    
headers = {
    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Cookie": load_Cookies(cookies=cookie)
}


video = videoParse(video_url=video_url, headers=headers)
styles = video.audio_supportFormats()
print(json.dumps(styles, indent='\t'))





