import logging
import requests
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from config import SEARCH_URL, PLAYLIST_FOLDER, LYRIC_URL, COOKIES
from lyric import lyric

# 配置日志
logging.basicConfig(level=logging.INFO)

# 创建歌单命令
async def new_playlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if len(context.args) != 1:
        await update.message.reply_text('请使用正确的格式：/new_playlist [歌单名称] (一个歌单最多350首)')
        return
    
    playlist_name = context.args[0]
    file_path = f"{PLAYLIST_FOLDER}{user_id}_{playlist_name}.json"
    
    if not os.path.exists(PLAYLIST_FOLDER):
        os.makedirs(PLAYLIST_FOLDER)
    
    # 创建歌单文件
    if not os.path.exists(file_path):
        playlist_data = {
            "user_id": user_id,
            "playlist_name": playlist_name,
            "songs": []
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, ensure_ascii=False, indent=4)
        await update.message.reply_text(f"歌单 '{playlist_name}' 创建成功！")
    else:
        await update.message.reply_text(f"歌单 '{playlist_name}' 已存在。")

# 添加歌曲到歌单命令
async def add_playlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if len(context.args) != 2:
        await update.message.reply_text('请使用正确的格式：/add_playlist [歌单名称] [歌曲名称] (一个歌单最多350首)')
        return

    playlist_name = context.args[0]
    music_keyword = context.args[1]
    file_path = f"{PLAYLIST_FOLDER}{user_id}_{playlist_name}.json"

    # 检查歌单文件是否存在
    if not os.path.exists(file_path):
        await update.message.reply_text(f"歌单 '{playlist_name}' 不存在，请先创建歌单。")
        return

    # 发送搜索提示消息
    loading_message = await update.message.reply_text(f"正在搜索歌曲 '{music_keyword}'...")
    try:
        # 通过关键词搜索音乐
        search_response = requests.get(SEARCH_URL.format(music_keyword))
        search_response.raise_for_status()  # 检查请求是否成功
        search_data = search_response.json()
        if search_data['code'] != 200 or not search_data['result']['songs']:
            await update.message.reply_text('未找到相关音乐，请检查音乐名称。')
            return

        # 获取第一首匹配的歌曲
        song = search_data['result']['songs'][0]
        music_id = song['id']
        music_name = song['name']

        # 读取现有的歌单
        with open(file_path, 'r', encoding='utf-8') as f:
            playlist_data = json.load(f)

        # 检查歌单中的歌曲数量
        playlist_quantity = playlist_data.get('playlist_quantity', len(playlist_data['songs']))
        if playlist_quantity >= 350:
            await update.message.reply_text(f"歌单 '{playlist_name}' 已达最大歌曲数量限制 (350 首) 。")
            return

        # 添加歌曲到歌单，并更新歌曲数量
        playlist_data['songs'].append({
            "music_name": music_name,
            "music_id": music_id
        })
        playlist_data['playlist_quantity'] = playlist_quantity + 1

        # 保存更新后的歌单
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, ensure_ascii=False, indent=4)

        await update.message.reply_text(f"歌曲 '{music_name}' 已添加到歌单 '{playlist_name}'！")
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=loading_message.message_id)

    except requests.RequestException as e:
        logging.error(f"网络请求错误: {e}")
        await update.message.reply_text("网络请求出现错误，请稍后再试。")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"添加歌曲时出错：{str(e)}")
        

# 处理我的歌单命令
async def my_playlist(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    playlist_files = [f for f in os.listdir(PLAYLIST_FOLDER) if f.startswith(str(user_id))]
    if not playlist_files:
        await update.message.reply_text('您还没有任何歌单。')
        return

    # 创建按钮
    keyboard = []
    for file in playlist_files:
        playlist_name = file.split('_')[1].replace('.json', '')  # 获取歌单名称
        keyboard.append([InlineKeyboardButton(playlist_name, callback_data=f"playlist_{playlist_name}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('选择您的歌单：', reply_markup=reply_markup)

async def playlist_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # 确认按钮点击
    callback_data = query.data

    # 确保回调数据以 "playlist_" 开头
    if callback_data.startswith("playlist_"):
        playlist_name = callback_data.replace("playlist_", "")
        user_id = query.from_user.id
        file_path = os.path.join(PLAYLIST_FOLDER, f"{user_id}_{playlist_name}.json")

        # 读取歌单内容
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                playlist_data = json.load(f)
            songs = playlist_data.get('songs', [])
            if not songs:
                await query.edit_message_text(text=f"歌单 '{playlist_name}' 中没有歌曲。")
                return
            # 显示歌曲列表
            song_list = '\n'.join([f"<blockquote expandable>{i + 1}. {song['music_name']}--{song['music_id']}</blockquote>" for i, song in enumerate(songs)])
            await query.edit_message_text(text=f"歌单 '{playlist_name}' 的歌曲列表：\n{song_list}", parse_mode='HTML')
        else:
            await query.edit_message_text(text='未找到该歌单。')