from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import Update
from music import music
from musicname import musicname
from playlist import playlist
from config import API_TOKEN
from lyric import lyric, lyric_button_callback
from playlist_ import new_playlist, add_playlist, my_playlist, playlist_button

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "欢迎使用网易云音乐bot!\n"
        "该bot由魔皇地狱通过gpt制作, 所以更新缓慢甚至有可能不更新\n"
        "单独输入指令获取帮助\n"
    )

def main():
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("music", music))
    app.add_handler(CommandHandler("musicname", musicname))
    app.add_handler(CommandHandler("playlist", playlist))
    app.add_handler(CommandHandler("new_playlist", new_playlist))
    app.add_handler(CommandHandler("add_playlist", add_playlist))
    app.add_handler(CommandHandler("my_playlist", my_playlist))

    # 确保歌单按钮使用的是 CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(playlist_button, pattern=r'playlist_.*'))

    # 注册歌词按钮处理器
    app.add_handler(CommandHandler('lyric', lyric))
    app.add_handler(CallbackQueryHandler(lyric_button_callback))
    app.run_polling()

if __name__ == '__main__':
    main()