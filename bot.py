import telebot
from telebot import types
import requests

# ===== CONFIG =====
BOT_TOKEN = "8292529209:AAFe-6M9GV27_nGLBeCWQazAjHXiKVt1n_c"  # এখানে তোমার বট টোকেন দাও
RAPIDAPI_KEY = "1582fcb55bmshfb63e25ebc040dfp13a868jsn65fda8150920"
API_URL = "https://chatgpt-42.p.rapidapi.com/texttoimage"

bot = telebot.TeleBot(BOT_TOKEN)

# প্রতিটি ইউজারের জন্য জেনারেটেড মেসেজ ID ট্র্যাক
user_messages = {}

# ===== /start Command =====
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🖼 Create Image")
    markup.add(btn1)
    bot.send_message(
        message.chat.id,
        "👋 **Welcome!**\n\n"
        "This is an AI Image Generator Bot.\n"
        "Just click **Create Image** and enter your prompt.\n"
        "The bot will generate a high-quality image for you.\n\n"
        "💡 Powered by Hasan Islam",
        parse_mode="Markdown",
        reply_markup=markup
    )
    user_messages[message.chat.id] = []

# ===== Handle Menu Buttons =====
@bot.message_handler(func=lambda msg: msg.text == "🖼 Create Image")
def ask_prompt(message):
    bot.send_message(message.chat.id, "✏️ Enter your prompt:")
    bot.register_next_step_handler(message, generate_image)

def generate_image(message):
    prompt = message.text.strip()

    wait_msg = bot.send_message(message.chat.id, "⏳ Generating image, please wait...")
    user_messages.setdefault(message.chat.id, []).append(wait_msg.message_id)

    payload = {
        "text": prompt,
        "width": 512,
        "height": 512
    }
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
        data = response.json()

        if "generated_image" in data:
            img_url = data["generated_image"]

            # Remove waiting message
            bot.delete_message(message.chat.id, wait_msg.message_id)

            sent_img = bot.send_photo(message.chat.id, img_url, caption=f"🖼 Prompt: `{prompt}`", parse_mode="Markdown")
            user_messages[message.chat.id].append(sent_img.message_id)

            # Add Delete Images button
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("🖼 Create Image")
            btn2 = types.KeyboardButton("🗑 Delete Images")
            markup.add(btn1, btn2)
            bot.send_message(message.chat.id, "✅ Image generated!", reply_markup=markup)

        else:
            bot.send_message(message.chat.id, "❌ Failed to generate image. Try again.")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {e}")

# ===== Delete Images Feature =====
@bot.message_handler(func=lambda msg: msg.text == "🗑 Delete Images")
def confirm_delete(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Yes", callback_data="delete_yes"),
        types.InlineKeyboardButton("❌ No", callback_data="delete_no")
    )
    bot.send_message(message.chat.id, "Are you sure you want to delete all generated images?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_images(call):
    if call.data == "delete_yes":
        if call.message.chat.id in user_messages:
            for msg_id in user_messages[call.message.chat.id]:
                try:
                    bot.delete_message(call.message.chat.id, msg_id)
                except:
                    pass
            user_messages[call.message.chat.id] = []
            bot.send_message(call.message.chat.id, "🗑 All images and messages deleted.")
        else:
            bot.send_message(call.message.chat.id, "ℹ️ No images to delete.")
    elif call.data == "delete_no":
        bot.send_message(call.message.chat.id, "❌ Cancelled.")

# ===== Run Bot =====
bot.polling(none_stop=True)e_stop=True)