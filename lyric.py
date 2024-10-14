import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import SEARCH_URL, COOKIES, LYRIC_URL

# 配置日志
logging.basicConfig(level=logging.INFO)

# 获取音乐ID并发送歌词
async def lyric(update: Update, context: ContextTypes.DEFAULT_TYPE):
    music_name = context.args[0] if context.args else None
    if not context.args:
        await update.effective_message.reply_text('/lyric [歌曲关键词或id]\n 只能一个一个获取')
        return
    
    # 提示用户正在搜索音乐信息
    loading_message = await update.effective_message.reply_text(f'正在搜索歌曲 "{music_name}" 的信息，请稍候...')
    
    # 发送搜索请求
    search_response = requests.get(SEARCH_URL.format(music_name), cookies=COOKIES)
    search_data = search_response.json()
    
    if search_data['code'] == 200 and search_data['result']['songs']:
        music_title = search_data['result']['songs'][0]['name']
        music_id = search_data['result']['songs'][0]['id']
        
        # 删除加载中的消息
        await context.bot.delete_message(chat_id=loading_message.chat_id, message_id=loading_message.message_id)
        loading_message = await update.effective_message.reply_text(f'已搜索到 "{music_title}" 的歌词，请稍候...')
        
        # 获取歌词数据
        search_lyric = requests.get(LYRIC_URL.format(music_id), cookies=COOKIES)
        lyric_data = search_lyric.json()
        
        # 初始化按钮列表
        lyric_buttons = []
        original_lrc = lyric_data.get('lrc', {}).get('lyric', None)
        korean_klyric = lyric_data.get('klyric', {}).get('lyric', None)
        chinese_tlyric = lyric_data.get('tlyric', {}).get('lyric', None)
        romanized_romalrc = lyric_data.get('romalrc', {}).get('lyric', None)
        
        # 动态创建按钮
        if original_lrc:
            lyric_buttons.append([InlineKeyboardButton(text="原文歌词", callback_data="original_lrc")])
        if korean_klyric:
            lyric_buttons.append([InlineKeyboardButton(text="韩文歌词", callback_data="korean_klyric")])
        if chinese_tlyric:
            lyric_buttons.append([InlineKeyboardButton(text="中文歌词", callback_data="chinese_tlyric")])
        if romanized_romalrc:
            lyric_buttons.append([InlineKeyboardButton(text="罗马歌词", callback_data="romanized_romalrc")])
        
        # 如果没有歌词数据
        if not lyric_buttons:
            await update.effective_message.reply_text("没有找到任何歌词。")
            return
        
        # 创建键盘
        reply_markup = InlineKeyboardMarkup(lyric_buttons) 
        
        # 发送消息并附带按钮
        await update.effective_message.reply_text(f'请选择 "{music_title}" 的歌词版本:', reply_markup=reply_markup)
        
        # 删除加载消息
        await context.bot.delete_message(chat_id=loading_message.chat_id, message_id=loading_message.message_id)
        
        # 保存歌词数据以便在回调中使用
        context.user_data['lyrics'] = {
            'original': original_lrc,
            'korean': korean_klyric,
            'chinese': chinese_tlyric,
            'romanized': romanized_romalrc
        }
    else:
        await update.effective_message.reply_text(f'音乐名称: {music_name} 未找到相关音乐或失败。')
        await context.bot.delete_message(chat_id=loading_message.chat_id, message_id=loading_message.message_id)

# 处理按钮点击的回调函数
async def lyric_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, music_name):
    query = update.callback_query
    await query.answer()  # 响应回调
    
    # 获取用户点击的按钮数据
    data = query.data
    lyrics = context.user_data.get('lyrics', {})
    
    # 根据按钮数据发送相应的歌词
    if data == "original_lrc" and lyrics.get('original'):
        await query.edit_message_text(text=f"<blockquote expandable>{music_name}原文歌词:\n\n{lyrics['original']}</blockquote>", parse_mode='HTML')
    elif data == "korean_klyric" and lyrics.get('korean'):
        await query.edit_message_text(text=f"<blockquote expandable>{music_name}韩文歌词:\n\n{lyrics['korean']}</blockquote>", parse_mode='HTML')
    elif data == "chinese_tlyric" and lyrics.get('chinese'):
        await query.edit_message_text(text=f"<blockquote expandable>{music_name}中文歌词:\n\n{lyrics['chinese']}</blockquote>", parse_mode='HTML')
    elif data == "romanized_romalrc" and lyrics.get('romanized'):
        await query.edit_message_text(text=f"<blockquote expandable>{music_name}罗马歌词:\n\n{lyrics['romanized']}</blockquote>", parse_mode='HTML')
    else:
        await query.edit_message_text(text="未找到对应的歌词。")