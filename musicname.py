import logging
import requests
import os
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from config import SEARCH_URL, MUSIC_ID_URL, COOKIES
from music_utils import download_music, upload_music  # 导入模块中的函数

# 配置日志
logging.basicConfig(level=logging.INFO)

async def musicname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    music_name = None
    level = 'lossless'
    downloaded_file_name = None  # 用于保存下载的文件名

    if '-l' in context.args:
        level_index = context.args.index('-l') + 1
        level = context.args[level_index] if level_index < len(context.args) else None
        music_name = " ".join(context.args[:level_index - 1])  # 音乐名称
    else:
        music_name = " ".join(context.args)

    if not music_name:
        await update.message.reply_text('请使用正确的格式：/musicname [音乐名称] -l [播放音质等级]\n例如: /musicname 恋愛サーキュレーション -l exhigh\n 播放音质等级, 分为 standard => 标准,higher => 较高, exhigh=>极高, lossless=>无损, hires=>Hi-Res, jyeffect => 高清环绕声, sky => 沉浸环绕声, dolby => 杜比全景声, jymaster => 超清母带\n ps: 杜比全景声几乎100%超过大小, bot-api大小限制为50MB(如果你有闲置api可以给我用).')
        return

    loading_message = await update.message.reply_text('正在搜索音乐...')

    try:
        # 请求音乐搜索，带上 Cookie
        search_response = requests.get(SEARCH_URL.format(music_name), cookies=COOKIES)
        search_data = search_response.json()

        if search_data['code'] != 200 or not search_data['result']['songs']:
            await update.message.reply_text('未找到相关音乐，请检查音乐名称。')
            return

        # 获取第一个有效的搜索结果
        song = search_data['result']['songs'][0]
        music_id = song['id']

        # 请求音乐链接，使用 level 参数
        music_response = requests.get(MUSIC_ID_URL.format(music_id, level), cookies=COOKIES) if level else requests.get(MUSIC_ID_URL.format(music_id), cookies=COOKIES)
        music_data = music_response.json()

        if music_data['code'] != 200 or not music_data['data']:
            await update.message.reply_text('获取音乐链接失败。')
            return
        
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=loading_message.message_id)
        
        loading_message = await update.message.reply_text(f'找到{music_name}, 正在下载上传')

        # 调用模块中定义的 `download_music` 函数下载音乐，传递 music_id 和 music_data
        downloaded_file_name, description = await download_music(music_id, music_data)

        if downloaded_file_name:
            # 调用模块中定义的 `upload_music` 函数上传音乐
            await upload_music(update, downloaded_file_name, description)

            # 删除加载消息
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=loading_message.message_id)
        else:
            await update.message.reply_text('下载音乐失败。')

    except Exception as e:
        logging.error(f'Error: {e}')
        await update.message.reply_text(f'发生错误：{str(e)}。请稍后再试。')

        # 尝试删除下载的文件
        if downloaded_file_name and os.path.exists(downloaded_file_name):
            try:
                await asyncio.sleep(5)  # 等待一秒钟后再尝试删除文件
                os.remove(downloaded_file_name)  # 删除下载的音乐文件
            except PermissionError:
                logging.error(f'无法删除文件 {downloaded_file_name}，可能正在被使用。')