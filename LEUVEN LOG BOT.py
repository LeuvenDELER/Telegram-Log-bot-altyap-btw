import requests
import telebot
import time
import os
import json
from datetime import datetime
from telebot import types

token = "8994720146:AAFDZK34VWVD6W77VDW1fonvbjc1iRlngWs"
bot = telebot.TeleBot(token)


KANALLAR = [CHAT KANALI IDLERINI YAZ]
ADMIN_ID = İDINI YAZ

#bukısmatokunmayoksacalısmaz
API_BASE = "APININİ YAZ"
API_TOKEN = "ELUVENPY"


USERS_FILE = "stone_users.json"
STARTS_FILE = "stone_starts.txt"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def log_start(user_id, username, first_name):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "username": username,
            "first_name": first_name,
            "first_start": datetime.now().isoformat(),
            "total_requests": 0
        }
        try:
            bot.send_message(ADMIN_ID, 
                f"🆕 Yeni Kullanıcı!\n"
                f"👤 İsim: {first_name}\n"
                f"🆔 ID: `{user_id}`\n"
                f"📛 Username: @{username if username else 'Yok'}\n"
                f"⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode="Markdown")
        except:
            pass
    users[str(user_id)]["last_active"] = datetime.now().isoformat()
    save_users(users)
    with open(STARTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{user_id}|{username}|{first_name}|{datetime.now().isoformat()}\n")

def increment_request(user_id):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)]["total_requests"] = users[str(user_id)].get("total_requests", 0) + 1
        save_users(users)

def get_stats():
    users = load_users()
    return len(users), sum(u.get("total_requests", 0) for u in users.values())

def kanal_check(user_id):
    try:
        for kanal_id in KANALLAR:
            uyemi = bot.get_chat_member(kanal_id, user_id)
            if uyemi.status not in ["member", "administrator", "creator"]:
                return False
        return True
    except:
        return False

def clean_url_lines(lines):
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(":")
        if len(parts) >= 3:
            cleaned.append(":".join(parts[-2:]))
        elif len(parts) == 2:
            cleaned.append(line)
    return cleaned

def main_menu(user_id, first_name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🔍 Log Ara", callback_data="menu_search"))
    markup.add(
        types.InlineKeyboardButton("🗑️ URL Temizle", callback_data="menu_clean"),
        types.InlineKeyboardButton("📊 İstatistikler", callback_data="menu_stats")
    )
    if user_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel"))
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    log_start(user_id, username, first_name)

    if not kanal_check(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🔗 Kanal 1", url=KANAL_LINK_KANAL),
            types.InlineKeyboardButton("🔗 Kanal 2", url=KANAL_LINK_CHAT)
        )
        markup.add(types.InlineKeyboardButton("🔄 Kontrol Et", callback_data="check_join"))
        bot.reply_to(message, 
            "⚠️ *Botu kullanmak için 2 kanala da katılmanız gerekiyor!*\n\n"
            "☑️ Katıldıktan sonra tekrar /start yazın.",
            parse_mode="Markdown", reply_markup=markup)
        return

    markup = main_menu(user_id, first_name)
    bot.reply_to(message,
        f"👤 *Selamün aleyküm {first_name}!*\n\n"
        f"🎯 *leuven Log Bot*'a hoş geldin!\n"
        f"📁 *50 farklı kaynaktan* log arayabilirsin.\n"
        f"⚡ *Sınırsız* sonuç çekebilirsin.\n\n"
        f"👉 Aşağıdaki butonlardan işlem seç.",
        parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    first_name = call.from_user.first_name

    if call.data == "check_join":
        if kanal_check(user_id):
            markup = main_menu(user_id, first_name)
            bot.edit_message_text(
                f"✅ *Kanal kontrolü başarılı!*\n\n"
                f"👤 *Selamün aleyküm {first_name}!*\n\n"
                f"🎯 *leuven Log Bot*'a hoş geldin!\n"
                f"📁 *50 farklı kaynaktan* log arayabilirsin.\n"
                f"⚡ *Sınırsız* sonuç çekebilirsin.\n\n"
                f"👉 Aşağıdaki butonlardan işlem seç.",
                call.message.chat.id, call.message.message_id,
                parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "❌ Hala kanallara katılmamışsın!")
        return

    if call.data == "menu_search":
        markup = types.InlineKeyboardMarkup(row_width=5)
        buttons = [types.InlineKeyboardButton(f"📁 {i}", callback_data=f"search_log{i}") for i in range(1, 51)]
        for i in range(0, len(buttons), 5):
            markup.row(*buttons[i:i+5])
        markup.add(types.InlineKeyboardButton("🔙 Ana Menü", callback_data="back_main"))
        bot.edit_message_text(
            "📁 *Hangi kaynaktan log çekmek istiyorsun?*\n\n"
            "1-50 arası bir kaynak seç.",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup)
        return

    if call.data.startswith("search_log"):
        log_num = int(call.data.replace("search_log", ""))
        msg = bot.edit_message_text(
            f"📁 *Kaynak {log_num} seçildi!*\n\n"
            f"🔍 *Aramak istediğin site/keyword nedir?*",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_search_single, log_num, msg.message_id)
        return

    if call.data == "menu_clean":
        msg = bot.edit_message_text(
            "🗑️ *URL Temizleme*\n\n"
            "`url:email:pass` formatındaki dosyayı gönder.",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_clean_url, msg.message_id)
        return

    if call.data == "menu_stats":
        total_users, total_requests = get_stats()
        bot.edit_message_text(
            f"📊 *İstatistikler*\n\n"
            f"👥 *Toplam Kullanıcı:* `{total_users}`\n"
            f"🔍 *Toplam Sorgu:* `{total_requests}`\n"
            f"📁 *Toplam Kaynak:* `50`\n"
            f"⚡ *Limit:* `Sınırsız`",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown")
        return

    if call.data == "back_main":
        markup = main_menu(user_id, first_name)
        bot.edit_message_text(
            f"👤 *Selamün aleyküm {first_name}!*\n\n"
            f"🎯 *leuven Log Bot*'a hoş geldin!\n"
            f"📁 *50 farklı kaynaktan* log arayabilirsin.\n"
            f"⚡ *Sınırsız* sonuç çekebilirsin.\n\n"
            f"👉 Aşağıdaki butonlardan işlem seç.",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup)
        return


    if call.data == "admin_panel":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Yetkisiz!")
            return
        total_users, total_requests = get_stats()
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📢 Duyuru", callback_data="admin_announce"),
            types.InlineKeyboardButton("👥 Kullanıcılar", callback_data="admin_users")
        )
        markup.add(
            types.InlineKeyboardButton("📊 Detaylı Stats", callback_data="admin_stats"),
            types.InlineKeyboardButton("📁 Starts Dosya", callback_data="admin_starts")
        )
        markup.add(types.InlineKeyboardButton("🔙 Ana Menü", callback_data="back_main"))
        bot.edit_message_text(
            f"⚙️ *Admin Paneli*\n\n"
            f"👤 Admin: `{ADMIN_ID}`\n"
            f"👥 Toplam Kullanıcı: `{total_users}`\n"
            f"🔍 Toplam Sorgu: `{total_requests}`",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup)
        return

    if call.data == "admin_announce":
        if user_id != ADMIN_ID: return
        msg = bot.edit_message_text(
            "📢 *Duyuru mesajını yaz:*",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_announce, msg.message_id)
        return

    if call.data == "admin_users":
        if user_id != ADMIN_ID: return
        users = load_users()
        user_list = []
        for uid, data in list(users.items())[:50]:
            user_list.append(f"🆔 `{uid}` | @{data.get('username', 'Yok')} | {data.get('first_name', 'Bilinmiyor')}")
        text = "👥 *Kullanıcı Listesi (İlk 50)*\n\n" + "\n".join(user_list) if user_list else "Kullanıcı yok."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        return

    if call.data == "admin_starts":
        if user_id != ADMIN_ID: return
        if os.path.exists(STARTS_FILE):
            with open(STARTS_FILE, 'rb') as f:
                bot.send_document(call.message.chat.id, f, caption="📁 Starts kayıtları")
        else:
            bot.edit_message_text("❌ Starts dosyası bulunamadı.", call.message.chat.id, call.message.message_id)
        return


def process_search_single(message, log_num, msg_id):
    query = message.text.strip()
    user_id = message.from_user.id
    if not query:
        bot.reply_to(message, "❌ Geçerli bir arama terimi gir!")
        return
    increment_request(user_id)
    loading_msg = bot.reply_to(message, f"⏳ *Kaynak {log_num} aranıyor...*", parse_mode="Markdown")
    start_time = time.time()

    try:
     
        response = requests.get(
            f"{API_BASE}/log{log_num}",
            params={"query": query, "token": API_TOKEN},
            timeout=60
        )

        elapsed = round(time.time() - start_time, 2)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                bot.edit_message_text(
                    f"❌ *Sonuç bulunamadı!*\n\n"
                    f"🔍 Arama: `{query}`\n"
                    f"📁 Kaynak: `{log_num}`",
                    message.chat.id, loading_msg.message_id,
                    parse_mode="Markdown")
                return

           
            cleaned = clean_url_lines(results)

            temp_file = f"{user_id}_log{log_num}.txt"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("\n".join(cleaned))

            caption = (
                f"✅ *Arama Tamamlandı!*\n\n"
                f"🔍 *Arama:* `{query}`\n"
                f"📁 *Kaynak:* `{log_num}`\n"
                f"📊 *Bulunan:* `{len(cleaned)}`\n"
                f"⏱️ *Süre:* `{elapsed} sn`\n"
                f"🗑️ *URL Temizlendi:* ✅\n\n"
                f"📎 @stonepanel | Stonepy"
            )

            with open(temp_file, "rb") as f:
                bot.send_document(message.chat.id, f, caption=caption, parse_mode="Markdown")

            os.remove(temp_file)
            bot.delete_message(message.chat.id, loading_msg.message_id)
        else:
            bot.edit_message_text(
                f"❌ *API Hatası:* `{response.status_code}`\n"
                f"API çalışıyor mu kontrol et!",
                message.chat.id, loading_msg.message_id,
                parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(
            f"⛔ *Hata:* `{str(e)}`\n"
            f"API bağlantısı kurulamadı!",
            message.chat.id, loading_msg.message_id,
            parse_mode="Markdown")


def process_clean_url(message, msg_id):
    if not message.document:
        bot.reply_to(message, "❌ Dosya göndermelisin!")
        return
    loading_msg = bot.reply_to(message, "🗑️ *URL'ler temizleniyor...*", parse_mode="Markdown")
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        content = downloaded.decode('utf-8', errors='ignore')
        lines = content.split("\n")
        cleaned = clean_url_lines(lines)
        temp_file = f"{message.from_user.id}_cleaned.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned))
        caption = (
            f"✅ *URL Temizleme Tamamlandı!*\n\n"
            f"📊 *Toplam Satır:* `{len(lines)}`\n"
            f"🗑️ *Temizlenen:* `{len(lines) - len(cleaned)}`\n"
            f"✅ *Kalan:* `{len(cleaned)}`\n\n"
            f"📎 @stonepanel | Stonepy"
        )
        with open(temp_file, "rb") as f:
            bot.send_document(message.chat.id, f, caption=caption, parse_mode="Markdown")
        os.remove(temp_file)
        bot.delete_message(message.chat.id, loading_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"⛔ *Hata:* `{str(e)}`", message.chat.id, loading_msg.message_id, parse_mode="Markdown")


def process_announce(message, msg_id):
    if message.from_user.id != ADMIN_ID:
        return
    announce_text = message.text
    users = load_users()
    sent = 0
    failed = 0
    loading_msg = bot.reply_to(message, "📢 *Duyuru gönderiliyor...*", parse_mode="Markdown")
    for user_id in users.keys():
        try:
            bot.send_message(int(user_id), f"📢 *DUYURU*\n\n{announce_text}", parse_mode="Markdown")
            sent += 1
            time.sleep(0.1)
        except:
            failed += 1
    bot.edit_message_text(f"✅ *Duyuru Tamamlandı!*\n\n✅ *Gönderilen:* `{sent}`\n❌ *Başarısız:* `{failed}`", message.chat.id, loading_msg.message_id, parse_mode="Markdown")


if __name__ == '__main__':
    print("=" * 60)
    print("  STONE LOG BOT  - API'li")
    print("=" * 60)
    print(f"API: {API_BASE}")
    print("Bot çalışıyor...")
    print("=" * 60)
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Hata: {e}")
            time.sleep(5)
