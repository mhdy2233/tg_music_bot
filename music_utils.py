import aiohttp
import os
import requests
import logging
from config import SEARCH_URL, COOKIES

# 配置日志
logging.basicConfig(level=logging.INFO)

async def download_music(music_id, music_data):
    """ 下载音乐并返回文件名和描述 """
    search_response = requests.get(SEARCH_URL.format(music_id), cookies=COOKIES)
    search_data = search_response.json()

    if search_data['code'] == 200 and search_data['result']['songs']:
        song = search_data['result']['songs'][0]
        music_title = song['name']
        artist_name = song['artists'][0]['name'] if song['artists'] else '未知'
        album_name = song['album']['name'] if song['album'] else '未知'
        alias = ', '.join(song.get('alias', ['无']))  # 别名
        trans_names = ', '.join(song.get('transNames', ['无']))  # 译名

        # 单个歌曲时的说明
        description = (
            f'音乐id: {music_id}\n'
            f'音乐名称: {music_title}\n'
            f'作曲家: {artist_name}\n'
            f'专辑: {album_name}\n'
            f'别名: {alias}\n'
            f'译名: {trans_names}\n'
            f'#网易云音乐\n'
            f'@mhdy_yinyue_bot'
        )

        # 获取下载链接
        music_url = next((item['url'] for item in music_data['data'] if item['id'] == int(music_id)), None)
        if music_url:
            original_file_name = await download_file(music_url)
            if original_file_name:
                # 重命名文件以保持音乐标题
                original_extension = os.path.splitext(original_file_name)[1]
                new_file_name = f'{music_title}{original_extension}'
                os.rename(original_file_name, new_file_name)
                return new_file_name, description

    return None, f'音乐ID: {music_id} 未找到相关音乐或下载失败。'


async def download_file(url):
    """ 下载文件并返回文件名 """
    # 获取原始文件名
    original_file_name = url.split('/')[-1]  # 假设使用 URL 的最后一部分作为文件名
    original_file_path = os.path.join(os.getcwd(), original_file_name)  # 保存路径

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            
            with open(original_file_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(5 * 1024 * 1024)  # 每次读取5MB
                    if not chunk:
                        break
                    f.write(chunk)
    return original_file_path

async def upload_music(update, file_name, description):
    """ 上传音乐文件 """
    with open(file_name, 'rb') as audio_file:
        await update.message.reply_audio(audio=audio_file, caption=description)
    os.remove(file_name)  # 在退出 with 块后删除文件