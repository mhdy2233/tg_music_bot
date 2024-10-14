import logging
import os
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from config import MUSIC_ID_URL, PLAYLIST_URL, COOKIES

# 配置日志
logging.basicConfig(level=logging.INFO)

async def download_song(session, music_url, music_title):
    """ 分片下载单曲 """
    async with session.get(music_url) as response:
        if response.status != 200:
            return None
        
        file_name = f'{music_title}.flac'
        with open(file_name, 'wb') as f:
            while True:
                chunk = await response.content.read(5 * 1024 * 1024)  # 每次读取5MB
                if not chunk:
                    break
                f.write(chunk)
        return file_name

async def fetch_and_download_song(session, music_id, music_title, level):
    """ 获取音乐下载链接并下载 """
    music_response = await session.get(MUSIC_ID_URL.format(music_id, level=level), cookies=COOKIES)
    music_data = await music_response.json()

    if music_data['code'] == 200 and music_data['data']:
        music_url = music_data['data'][0]['url']
        if music_url:
            return await download_song(session, music_url, music_title)
    return None

async def playlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3 or len(context.args) > 4:
        await update.message.reply_text('请使用正确的格式：\n/playlist [歌单ID] [第几首歌开始] [获取数量] [-v [等级]]\n例：/playlist 12345 0 5 -v higher\n防止堵塞请一次下载数量不要大于10首')
        return

    playlist_id = context.args[0]
    offset = int(context.args[1])
    limit = int(context.args[2])
    level = 'lossless'  # 默认等级

    # 检查是否指定了等级
    if len(context.args) == 4 and context.args[3] == '-v':
        if len(context.args) > 4:
            level = context.args[4]

    if limit - offset > 10:
        await update.message.reply_text('一次最多下载10首歌，请调整获取数量。')
        return

    loading_message = await update.message.reply_text('正在获取歌单信息...')

    try:
        async with aiohttp.ClientSession() as session:
            playlist_response = await session.get(PLAYLIST_URL.format(playlist_id, limit, offset), cookies=COOKIES)
            playlist_data = await playlist_response.json()

            if playlist_data['code'] != 200 or not playlist_data['songs']:
                await update.message.reply_text('获取歌单失败，请检查歌单ID。')
                return

            audio_files = []
            tasks = []

            for song in playlist_data['songs']:
                music_id = song['id']
                music_title = song['name']
                # 异步下载音乐
                tasks.append(fetch_and_download_song(session, music_id, music_title, level))

            audio_files = await asyncio.gather(*tasks)

            # 上传音乐文件
            if audio_files:
                await update.message.reply_text('正在上传音乐，请稍候...')
                for file_name in audio_files:
                    if file_name:
                        await update.message.reply_audio(audio=open(file_name, 'rb'))
                        os.remove(file_name)
                    else:
                        await update.message.reply_text('下载音乐失败。')

                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=loading_message.message_id)
            else:
                await update.message.reply_text('未能下载任何音乐。')

    except Exception as e:
        logging.error(f'Error: {e}')
        await update.message.reply_text('发生错误，请稍后再试。')
