import logging
import requests
import asyncio
import os
from telegram import Update
from telegram.ext import ContextTypes
from config import MUSIC_ID_URL, COOKIES
from music_utils import download_music, upload_music  # 导入新模块中的函数

# 配置日志
logging.basicConfig(level=logging.INFO)

async def music(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text('请使用正确的格式：\n/music [音乐ID1,音乐ID2,...] -v [等级]\n例：/music 461011,33894312 -v higher\n播放音质等级, 分为 standard => 标准,higher => 较高, exhigh=>极高, lossless=>无损, hires=>Hi-Res, jyeffect => 高清环绕声, sky => 沉浸环绕声, dolby => 杜比全景声, jymaster => 超清母带\n ps: 杜比全景声几乎100%超过大小, bot-api大小限制为50MB(如果你有闲置api可以给我用).')
        return

    music_ids = context.args[0].split(',')
    if len(music_ids) > 10:
        await update.message.reply_text('最多一次可以处理10首歌。')
        return

    # 默认音质等级
    level = 'lossless'

    # 获取音质等级
    level_arg_index = context.args.index('-v') if '-v' in context.args else -1
    if level_arg_index != -1 and level_arg_index + 1 < len(context.args):
        level = context.args[level_arg_index + 1]  # 更新为用户提供的等级

    loading_message = await update.message.reply_text('正在获取音乐信息...')

    try:
        # 请求音乐链接，带上 Cookie
        music_response = requests.get(MUSIC_ID_URL.format(','.join(music_ids)), cookies=COOKIES)
        music_data = music_response.json()

        if music_data['code'] != 200 or not music_data['data']:
            await update.message.reply_text('获取音乐链接失败。')
            return
        
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=loading_message.message_id)

        loading_message = await update.message.reply_text('正在下载和上传音乐，请稍候...')

        tasks = []
        for music_id in music_ids:
            tasks.append(download_music(music_id, music_data, level))  # 传递level参数

        for future in asyncio.as_completed(tasks):
            file_name, description = await future
            if file_name:
                try:
                    await upload_music(update, file_name, description)
                except Exception as upload_error:
                    logging.error(f'上传音乐时发生错误: {upload_error}')
                    await update.message.reply_text(f'上传错误: {str(upload_error)}')
                finally:
                    if os.path.exists(file_name):
                        os.remove(file_name)  # 确保删除文件
            else:
                await update.message.reply_text(description)

        # 删除加载消息
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=loading_message.message_id)

    except Exception as e:
        logging.error(f'Error: {e}')
        await update.message.reply_text(f'发生错误：{str(e)}。请稍后再试。')
        if 'file_name' in locals() and os.path.exists(file_name):
            try:
                os.remove(file_name)  # 确保删除文件
            except Exception as delete_error:
                logging.error(f'无法删除文件 {file_name}: {delete_error}')

