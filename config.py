API_TOKEN = '填写你的TG_BOT_TOKEN'
MUSIC_ID_URL = 'http://127.0.0.1:3000/song/url/v1?id={}&level={}'  # 根据你的网易云api进行填写
SEARCH_URL = 'http://127.0.0.1:3000/search?limit=1&type=1&keywords={}'
PLAYLIST_URL = "http://127.0.0.1:3000/playlist/track/all?id={}&limit={}&offset={}"
LYRIC_URL = "http://127.0.0.1:3000/lyric?id={}"
COVER_URL = "http://127.0.0.1:3000/song/dynamic/cover?id={}"
PLAYLIST_FOLDER = './playlist/'
COOKIES = {
    '__remember_me': 'true',
    'NMTID': '',
    '__csrf': '',
    'MUSIC_U': '',
    'os': 'pc'
} # 填写你的网易云cookie, 可以是官网的也可以是网易云api的
