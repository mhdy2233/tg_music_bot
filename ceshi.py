from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import API_TOKEN
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def send_button(update, context):
    chat_id = update.message.chat_id

    # 创建按钮
    button = InlineKeyboardButton(text="点击我", callback_data="button_clicked")
    
    # 创建包含按钮的键盘
    keyboard = [[button]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 发送消息并附带按钮
    await context.bot.send_message(chat_id=chat_id, text="选择一个按钮:", reply_markup=reply_markup)

# 回调处理函数
async def button_callback(update, context):
    query = update.callback_query
    query.answer()
    
    # 响应按钮点击
    await query.edit_message_text(text=f"你点击了: {query.data}")


def main():
    app = ApplicationBuilder().token(API_TOKEN).build()

    app.add_handler(CommandHandler('start', send_button))
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling()

if __name__ == '__main__':
    main()
# 添加到你的命令处理器中

