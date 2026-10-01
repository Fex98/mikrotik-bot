import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# متغيرات مؤقتة لتخزين حالة المودمات
modems_data = {
    "active": [],
    "disconnected": []
}

@app.route('/')
def home():
    return "Bot is running!"

# استقبال التحديثات من تليجرام عبر Webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook_listener():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# مسار استقبال بيانات المودمات من المايكروتك (محدث ومحصن ضد الأخطاء)
@app.route('/update_modems', methods=['POST'])
def update_modems():
    try:
        # محاولة قراءة البيانات كـ JSON أو كبيانات نصية عادية
        data = request.get_json(silent=True)
        if not data:
            data = request.form
            
        print(f"--- Received Data from Mikrotik ---: {data}")
        
        if data:
            modems_data['active'] = data.get('active', [])
            modems_data['disconnected'] = data.get('disconnected', [])
            return "Updated successfully", 200
            
        return "No data received", 400
    except Exception as e:
        print(f"Error in update_modems: {str(e)}")
        return str(e), 500

# دوال الاستجابة لأوامر والأزرار في تليجرام
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("حالة الشبكة العامة")
    markup.row("المودمات المنقطعة", "المودمات الشغالة")
    bot.send_message(message.chat.id, "🚀 أهلاً بك في لوحة تحكم شبكة SKY_NET\nاختر من الأزرار أدناه لعرض التقارير اللحظية:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text_buttons(message):
    text = message.text
    if "المودمات المنقطعة" in text:
        disc = modems_data.get('disconnected', [])
        if not disc:
            bot.send_message(message.chat.id, "⚠️ لا توجد مودمات منقطعة حالياً في القائمة الحية.")
        else:
            bot.send_message(message.chat.id, "🔴 المودمات المنقطعة:\n" + "\n".join(disc))
            
    elif "المودمات الشغالة" in text:
        act = modems_data.get('active', [])
        if not act:
            bot.send_message(message.chat.id, "⚠️ لا توجد مودمات شغالة حالياً في القائمة.")
        else:
            bot.send_message(message.chat.id, "🟢 المودمات الشغالة:\n" + "\n".join(act))
            
    elif "حالة الشبكة العامة" in text:
        act_count = len(modems_data.get('active', []))
        disc_count = len(modems_data.get('disconnected', []))
        bot.send_message(message.chat.id, f"📊 تقرير حالة الشبكة العامة:\n🟢 الشغالة: {act_count}\n🔴 المنقطعة: {disc_count}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://mikrotik-bot-m7ui.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
