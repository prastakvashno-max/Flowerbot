import time
import logging
import telebot
from telebot import types

from config import BOT_TOKEN, ADMIN_IDS, FLOWERS_CATALOG
from database import DatabaseManager
from keyboards import KeyboardManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("FlowerBot")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
db = DatabaseManager()

user_sessions = {}

def clear_user_state(chat_id):
    bot.clear_step_handler_by_chat_id(chat_id)
    if chat_id in user_sessions:
        del user_sessions[chat_id]

@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    try:
        chat_id = message.chat.id
        clear_user_state(chat_id)
        
        db.add_user(
            user_id=chat_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username
        )
        
        is_admin = chat_id in ADMIN_IDS
        welcome_text = (
            f"🌸 *Assalomu alaykum, {message.from_user.first_name}!*\n\n"
            f"Gullar do'konimizning rasmiy botiga xush kelibsiz.\n"
            f"Bu yerda siz yangi va nafis gullarni osongina buyurtma qilishingiz mumkin.\n\n"
            f"Tanlov qilish uchun quyidagi menyudan foydalaning 👇"
        )
        
        bot.send_message(chat_id, welcome_text, reply_markup=KeyboardManager.main_menu(is_admin))
    except Exception as e:
        logger.error(f"Start funksiyasida xatolik: {e}")

@bot.message_handler(func=lambda msg: msg.text == "💐 Gullar katalogi")
def handle_catalog(message):
    try:
        chat_id = message.chat.id
        clear_user_state(chat_id)
        
        bot.send_message(
            chat_id,
            "💐 *Bizning gullar katalogimiz:*\n\nO'zingizga yoqqan gulni tanlang:",
            reply_markup=KeyboardManager.catalog_inline()
        )
    except Exception as e:
        logger.error(f"Katalog ko'rsatishda xatolik: {e}")

@bot.message_handler(func=lambda msg: msg.text == "📦 Buyurtmalarim")
def handle_my_orders(message):
    try:
        chat_id = message.chat.id
        clear_user_state(chat_id)
        
        orders = db.get_user_orders(chat_id)
        if not orders:
            bot.send_message(chat_id, "Sizda hali hech qanday buyurtmalar mavjud emas.")
            return

        response = "📦 *Sizning oxirgi buyurtmalaringiz:*\n\n"
        for ord_id, flower, color, qty, price, status, date in orders:
            response += (
                f"🔹 *Buyurtma №{ord_id}*\n"
                f"🌸 Gul: {flower} ({color})\n"
                f"🔢 Miqdori: {qty} dona\n"
                f"💰 Summa: {price:,} so'm\n"
                f"📌 Holati: {status}\n"
                f"📅 Vaqti: {date}\n"
                f"----------------------------\n"
            )
        bot.send_message(chat_id, response)
    except Exception as e:
        logger.error(f"Buyurtmalarni olishda xatolik: {e}")

@bot.message_handler(func=lambda msg: msg.text == "📞 Biz bilan bog'lanish")
def handle_contact(message):
    try:
        chat_id = message.chat.id
        clear_user_state(chat_id)
        
        text = (
            "📞 *Biz bilan bog'lanish:*\n\n"
            "📱 Telefon: +998 90 123 45 67\n"
            "📍 Manzil: Toshkent shahri, Gullar ko'chasi, 1-uy.\n"
            "⏰ Ish vaqti: 08:00 - 22:00 (Hamma vaqt ochiq)\n\n"
            "Savol va takliflaringiz bo'lsa, telefon raqamingizni qoldiring:"
        )
        bot.send_message(chat_id, text, reply_markup=KeyboardManager.contact_keyboard())
    except Exception as e:
        logger.error(f"Kontakt menyusida xatolik: {e}")

@bot.message_handler(func=lambda msg: msg.text == "ℹ️️ Yordam va Ma'lumot")
def handle_info(message):
    try:
        chat_id = message.chat.id
        clear_user_state(chat_id)
        
        text = (
            "ℹ️ *Botdan foydalanish bo'yicha yo'riqnoma:*\n\n"
            "1. *💐 Gullar katalogi* tugmasini bosing.\n"
            "2. O'zingizga ma'qul gul va uning rangini tanlang.\n"
            "3. Kerakli miqdorni (donada) kiritasiz.\n"
            "4. Telefon raqamingizni ulashib, buyurtmani tasdiqlaysiz.\n\n"
            "Operatorlarimiz tez orada siz bilan bog'lanishadi!"
        )
        bot.send_message(chat_id, text)
    except Exception as e:
        logger.error(f"Ma'lumot berishda xatolik: {e}")

@bot.message_handler(func=lambda msg: msg.text == "📊 Admin Panel" and msg.chat.id in ADMIN_IDS)
def handle_admin(message):
    try:
        chat_id = message.chat.id
        clear_user_state(chat_id)
        
        total_users, total_orders, total_revenue = db.get_stats()
        text = (
            "📊 *Boshqaruv Paneli (Admin):*\n\n"
            f"👤 Jami foydalanuvchilar: *{total_users} ta*\n"
            f"📦 Jami buyurtmalar: *{total_orders} ta*\n"
            f"💰 Jami tushum: *{total_revenue:,} so'm*"
        )
        bot.send_message(chat_id, text, reply_markup=KeyboardManager.admin_menu())
    except Exception as e:
        logger.error(f"Admin panelda xatolik: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    try:
        chat_id = call.message.chat.id
        data = call.data
        
        bot.answer_callback_query(call.id)

        if data == "back_to_catalog":
            bot.edit_message_text(
                "💐 *Bizning gullar katalogimiz:*\n\nO'zingizga yoqqan gulni tanlang:",
                chat_id,
                call.message.message_id,
                reply_markup=KeyboardManager.catalog_inline()
            )
            return

        if data.startswith("select_flw_"):
            idx = int(data.replace("select_flw_", ""))
            flower_name = list(FLOWERS_CATALOG.keys())[idx]
            flower_data = FLOWERS_CATALOG[flower_name]
            
            user_sessions[chat_id] = {
                "flower": flower_name,
                "unit_price": flower_data["price"]
            }
            
            text = (
                f"🌸 *Gul:* {flower_name}\n"
                f"📝 *Tavsif:* {flower_data['description']}\n"
                f"💰 *Narxi:* {flower_data['price']:,} so'm\n\n"
                f"Iltimos, kerakli gul rangini tanlang:"
            )
            bot.edit_message_text(
                text,
                chat_id,
                call.message.message_id,
                reply_markup=KeyboardManager.colors_inline(flower_name)
            )

        elif data.startswith("select_clr_"):
            if chat_id not in user_sessions:
                bot.send_message(chat_id, "Sessiya vaqti tugadi. Qaytadan katalogdan tanlang.", reply_markup=KeyboardManager.main_menu())
                return

            flower_name = user_sessions[chat_id]["flower"]
            color_idx = int(data.replace("select_clr_", ""))
            color_name = FLOWERS_CATALOG[flower_name]["colors"][color_idx]
            
            user_sessions[chat_id]["color"] = color_name
            
            msg = bot.send_message(
                chat_id,
                f"🎨 Rang: *{color_name}*\n\nNechta dona xarid qilmoqchisiz? (Raqamda kiritasiz, masalan: 5, 10, 25):"
            )
            bot.clear_step_handler_by_chat_id(chat_id)
            bot.register_next_step_handler(msg, process_quantity_step)

        elif data == "order_confirm":
            if chat_id in user_sessions and "quantity" in user_sessions[chat_id]:
                msg = bot.send_message(
                    chat_id,
                    "📱 Buyurtmani rasmiylashtirish uchun telefon raqamingizni yuboring:",
                    reply_markup=KeyboardManager.contact_keyboard()
                )
            else:
                bot.send_message(chat_id, "Buyurtma topilmadi. Qaytadan urinib ko'ring.", reply_markup=KeyboardManager.main_menu())

        elif data == "order_cancel":
            clear_user_state(chat_id)
            bot.send_message(chat_id, "❌ Buyurtma bekor qilindi.", reply_markup=KeyboardManager.main_menu())

        elif data == "admin_stats":
            total_users, total_orders, total_revenue = db.get_stats()
            bot.send_message(
                chat_id,
                f"📈 *Hozirgi statistika:*\n\nFoydalanuvchilar: {total_users}\nBuyurtmalar: {total_orders}\nTushum: {total_revenue:,} so'm"
            )

        elif data == "admin_close":
            bot.delete_message(chat_id, call.message.message_id)

    except Exception as e:
        logger.error(f"Callback queryda xatolik: {e}")

def process_quantity_step(message):
    try:
        chat_id = message.chat.id
        text = message.text

        if text in ["💐 Gullar katalogi", "📦 Buyurtmalarim", "📞 Biz bilan bog'lanish", "ℹ️ Yordam va Ma'lumot", "/start"]:
            clear_user_state(chat_id)
            if text == "/start":
                cmd_start(message)
            return

        if not text or not text.isdigit() or int(text) <= 0:
            msg = bot.send_message(chat_id, "⚠️ Noto'g'ri miqdor! Iltimos, faqat musbat raqam yozing (masalan: 10):")
            bot.clear_step_handler_by_chat_id(chat_id)
            bot.register_next_step_handler(msg, process_quantity_step)
            return

        quantity = int(text)
        if chat_id in user_sessions:
            session = user_sessions[chat_id]
            session["quantity"] = quantity
            total_price = quantity * session["unit_price"]
            session["total_price"] = total_price
            
            summary_text = (
                f"📋 *Buyurtma ma'lumotlari:*\n\n"
                f"🌸 *Gul:* {session['flower']}\n"
                f"🎨 *Rang:* {session['color']}\n"
                f"🔢 *Miqdor:* {quantity} dona\n"
                f"💰 *Jami summa:* {total_price:,} so'm\n\n"
                f"Buyurtmani tasdiqlaysizmi?"
            )
            bot.clear_step_handler_by_chat_id(chat_id)
            bot.send_message(chat_id, summary_text, reply_markup=KeyboardManager.confirm_inline())
    except Exception as e:
        logger.error(f"Miqdor kiritishda xatolik: {e}")

@bot.message_handler(content_types=['contact'])
def handle_contact_received(message):
    try:
        chat_id = message.chat.id
        phone_number = message.contact.phone_number
        
        bot.clear_step_handler_by_chat_id(chat_id)
        
        db.add_user(
            user_id=chat_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username,
            phone=phone_number
        )
        
        if chat_id in user_sessions and "total_price" in user_sessions[chat_id]:
            session = user_sessions[chat_id]
            
            order_id = db.add_order(
                user_id=chat_id,
                flower_name=session["flower"],
                color=session["color"],
                quantity=session["quantity"],
                total_price=session["total_price"]
            )
            
            bot.send_message(
                chat_id,
                f"✅ *Buyurtmangiz qabul qilindi!*\n\nBuyurtma raqami: *№{order_id}*\nTez orada siz bilan bog'lanamiz.",
                reply_markup=KeyboardManager.main_menu(chat_id in ADMIN_IDS)
            )
            
            admin_msg = (
                f"🚨 *YANGI BUYURTMA №{order_id}!*\n\n"
                f"👤 *Mijoz:* {message.from_user.first_name} (@{message.from_user.username})\n"
                f"📞 *Tel:* +{phone_number}\n"
                f"🌸 *Gul:* {session['flower']}\n"
                f"🎨 *Rang:* {session['color']}\n"
                f"🔢 *Miqdor:* {session['quantity']} dona\n"
                f"💰 *Summa:* {session['total_price']:,} so'm"
            )
            
            for admin_id in ADMIN_IDS:
                try:
                    bot.send_message(admin_id, admin_msg)
                except Exception as admin_err:
                    logger.error(f"Adminga yuborishda xatolik ({admin_id}): {admin_err}")
            
            del user_sessions[chat_id]
        else:
            bot.send_message(
                chat_id,
                f"Raqamingiz saqlandi: +{phone_number}",
                reply_markup=KeyboardManager.main_menu(chat_id in ADMIN_IDS)
            )
    except Exception as e:
        logger.error(f"Kontakt qabul qilishda xatolik: {e}")

if __name__ == "__main__":
    logger.info("Bot serveri tayyorlanmoqda...")
    try:
        bot.remove_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Webhook o'chirishda ogohlantirish: {e}")

    logger.info("Bot muvaffaqiyatli ishga tushirildi va uzluksiz rejimda ishlamoqda.")
    
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=5, skip_pending=True)
        except Exception as err:
            logger.error(f"Polling zanjirida uzilish yuz berdi: {err}")
            time.sleep(3)

