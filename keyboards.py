from telebot import types
from config import FLOWERS_CATALOG

class KeyboardManager:
    @staticmethod
    def main_menu(is_admin=False):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_catalog = types.KeyboardButton("💐 Gullar katalogi")
        btn_orders = types.KeyboardButton("📦 Buyurtmalarim")
        btn_contact = types.KeyboardButton("📞 Biz bilan bog'lanish")
        btn_help = types.KeyboardButton("ℹ️ Yordam va Ma'lumot")
        
        markup.add(btn_catalog, btn_orders)
        markup.add(btn_contact, btn_help)
        
        if is_admin:
            btn_admin = types.KeyboardButton("📊 Admin Panel")
            markup.add(btn_admin)
            
        return markup

    @staticmethod
    def contact_keyboard():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn = types.KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)
        markup.add(btn)
        return markup

    @staticmethod
    def catalog_inline():
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for idx, flower in enumerate(FLOWERS_CATALOG.keys()):
            buttons.append(types.InlineKeyboardButton(flower, callback_data=f"select_flw_{idx}"))
        markup.add(*buttons)
        return markup

    @staticmethod
    def colors_inline(flower_key):
        markup = types.InlineKeyboardMarkup(row_width=2)
        colors = FLOWERS_CATALOG[flower_key]["colors"]
        buttons = []
        for idx, color in enumerate(colors):
            buttons.append(types.InlineKeyboardButton(color, callback_data=f"select_clr_{idx}"))
        
        btn_back = types.InlineKeyboardButton("⬅️ Ortga", callback_data="back_to_catalog")
        markup.add(*buttons)
        markup.add(btn_back)
        return markup

    @staticmethod
    def confirm_inline():
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_confirm = types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="order_confirm")
        btn_cancel = types.InlineKeyboardButton("❌ Bekor qilish", callback_data="order_cancel")
        markup.add(btn_confirm, btn_cancel)
        return markup

    @staticmethod
    def admin_menu():
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_stats = types.InlineKeyboardButton("📈 Statistika", callback_data="admin_stats")
        btn_close = types.InlineKeyboardButton("❌ Yopish", callback_data="admin_close")
        markup.add(btn_stats, btn_close)
        return markup
