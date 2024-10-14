# 该项目为tg网易云音乐获取bot
项目使用的网易云api为[NeteaseCloudMusicApi](https://gitlab.com/Binaryify/neteasecloudmusicapi)  
项目制作由chatgpt-4o-mini加小白优化.  

# 安装

```python
git clone https://github.com/mhdy2233/tg_music_bot.git && cd tg_music_bot
pip install -r requirements.txt
python main.py
```

打开config.py修改参数
```
API_TOKEN = '填写你的TG_BOT_TOKEN'
MUSIC_ID_URL = 'http://127.0.0.1:3000/song/url/v1?id={}&level={}'  # 根据你的网易云api进行填写
SEARCH_URL = 'http://127.0.0.1:3000/search?limit=1&type=1&keywords={}'
PLAYLIST_URL = "http://127.0.0.1:3000/playlist/track/all?id={}&limit={}&offset={}"
LYRIC_URL = "http://127.0.0.1:3000/lyric?id={}"
COVER_URL = "http://127.0.0.1:3000/song/dynamic/cover?id={}"
COOKIES = {
    '__remember_me': 'true',
    'NMTID': '',
    '__csrf': '',
    'MUSIC_U': '',
    'os': 'pc'
} # 填写你的网易云cookie, 可以是官网的也可以是网易云api的

```

# 使用说明
默认命令为:  
/music 509728841, 33682739, ...[^使用id下载网易云音乐(支持等级切换,最多10个)]  
/musicname 恋爱循环或者461011[^通过id或者关键词下载网易云音乐(支持等级切换)]  
/playlist 801764896 0 10[^通过歌单id进行下载(一次最多10个)]  
/lyric 恋爱循环或者461011[^通过id或者关键词获取歌词]  

# 我部署的api
https://music.mhdy.shop  

# 推广
**[我的发布页](https://mohuangdiyu.com)**  

# 赞助
![赞助](https://fj.mhdyapp.buzz/2024-08-05-04-23-46.jpg)