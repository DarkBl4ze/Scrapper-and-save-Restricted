import os
import json
import time
import threading
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# Load configuration from file or environment variables
with open('config.json', 'r') as f:
    DATA = json.load(f)

def getenv(var): return os.environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN") 
api_hash = getenv("HASH") 
api_id = getenv("ID")

bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = getenv("STRING")
if ss is not None:
    acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()
else:
    acc = None

REQUIRED_CHANNELS = ["@EliteSentinals", "@blackbaldex"]

def save_user_id(user_id):
    with open('user_ids.txt', 'a') as f:
        f.write(f"{user_id}\n")

def check_user_id(user_id):
    if not os.path.exists('user_ids.txt'):
        return False
    with open('user_ids.txt', 'r') as f:
        user_ids = f.read().splitlines()
    return str(user_id) in user_ids

def check_membership(user_id):
    if check_user_id(user_id):
        return True
    for channel in REQUIRED_CHANNELS:
        member = bot.get_chat_member(channel, user_id)
        if not (member and member.status in ["member", "administrator", "creator"]):
            return False
    save_user_id(user_id)
    return True

@bot.on_message(filters.command(["start"]))
def send_start(client: Client, message: Message):
    if check_membership(message.from_user.id):
        bot.send_message(
            message.chat.id, 
            f"👋 Hi **{message.from_user.mention}**, you have access to use the bot.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("OWNER ✅", url="https://t.me/bl44ze")]]),
            reply_to_message_id=message.id
        )
    else:
        bot.send_message(
            message.chat.id, 
            "You must join the following channels to use this bot:",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("EliteSentinals", url="https://t.me/EliteSentinals"),
                  InlineKeyboardButton("blackbaldex", url="https://t.me/blackbaldex")],
                 [InlineKeyboardButton("Check Membership", callback_data="check_membership")]]
            ),
            reply_to_message_id=message.id
        )

@bot.on_callback_query(filters.regex("check_membership"))
def callback_check_membership(client: Client, callback_query):
    user_id = callback_query.from_user.id
    if check_membership(user_id):
        bot.send_message(
            callback_query.message.chat.id, 
            f"👋 Hi **{callback_query.from_user.mention}**, you now have access to use the bot."
        )
        bot.delete_messages(callback_query.message.chat.id, [callback_query.message.id])
    else:
        bot.answer_callback_query(callback_query.id, "You have not joined all the required channels.", show_alert=True)

# download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
    time.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
    time.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

@bot.on_message(filters.text)
def save(client, message):
    print(message.text)

    # joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        if acc is None:
            bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            return

        try:
            try:
                acc.join_chat(message.text)
            except Exception as e:
                bot.send_message(message.chat.id, f"**Response** : {e}", reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, "**Chat Joined**", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "**Chat already Joined**", reply_to_message_id=message.id)
        except InviteHashExpired:
            bot.send_message(message.chat.id, "**Invalid Link**", reply_to_message_id=message.id)

    # getting message
    elif "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return
                handle_private(message, chatid, msgid)
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return
                try:
                    handle_private(message, username, msgid)
                except Exception as e:
                    bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
            # public
            else:
                username = datas[3]
                try:
                    msg = bot.get_messages(username, msgid)
                except UsernameNotOccupied:
                    bot.send_message(message.chat.id, f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
                    return
                try:
                    if '?single' not in message.text:
                        bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                    else:
                        bot.copy_media_group(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    if acc is None:
                        bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                        return
                    try:
                        handle_private(message, username, msgid)
                    except Exception as e:
                        bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
            # wait time
            time.sleep(3)

# handle private
def handle_private(message, chatid, msgid):
    msg = acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)
    if "Text" == msg_type:
        bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        return

    smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
    dosta = threading.Thread(target=lambda: downstatus(f'{message.id}downstatus.txt', smsg), daemon=True)
    dosta.start()
    file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
    os.remove(f'{message.id}downstatus.txt')

    upsta = threading.Thread(target=lambda: upstatus(f'{message.id}upstatus.txt', smsg), daemon=True)
    upsta.start()

    if "Document" == msg_type:
        try:
            thumb = acc.download_media(msg.document.thumbs[0].file_id)
        except:
            thumb = None
        bot.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        os.remove(file)
        try:
            os.remove(thumb)
        except:
            pass
    elif "Video" == msg_type:
        try:
            thumb = acc.download_media(msg.video.thumbs[0].file_id)
        except:
            thumb = None
        bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        os.remove(file)
        try:
            os.remove(thumb)
        except:
            pass
    elif "Animation" == msg_type:
        bot.send_animation(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        os.remove(file)
    elif "Sticker" == msg_type:
        bot.send_sticker(message.chat.id, file, reply_to_message_id=message.id)
        os.remove(file)
    elif "Voice" == msg_type:
        bot.send_voice(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, duration=msg.voice.duration, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        os.remove(file)
    elif "Audio" == msg_type:
        bot.send_audio(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, duration=msg.audio.duration, performer=msg.audio.performer, title=msg.audio.title, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        os.remove(file)
    elif "Photo" == msg_type:
        bot.send_photo(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        os.remove(file)
    elif "VideoNote" == msg_type:
        bot.send_video_note(message.chat.id, file, length=msg.video_note.length, duration=msg.video_note.duration, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        os.remove(file)
    os.remove(f'{message.id}upstatus.txt')

# get message type
def get_message_type(msg):
    if msg.text:
        return "Text"
    elif msg.document:
        return "Document"
    elif msg.video:
        return "Video"
    elif msg.animation:
        return "Animation"
    elif msg.sticker:
        return "Sticker"
    elif msg.voice:
        return "Voice"
    elif msg.audio:
        return "Audio"
    elif msg.photo:
        return "Photo"
    elif msg.video_note:
        return "VideoNote"
    return "Unknown"

USAGE = """                         [ 𝐁𝐋𝟒𝟒𝐙𝐄 𝐒𝐀𝐕𝐄 ]


**FOR PUBLIC CHATS ⚡**

[   ✅ 𝐒𝐢𝐦𝐩𝐥𝐲 𝐬𝐞𝐧𝐝 𝐭𝐡𝐞 𝐥𝐢𝐧𝐤 𝐨𝐟 𝐭𝐡𝐞 𝐩𝐨𝐬𝐭(𝐬).   ]


**FOR PRIVATE CHATS 🔒**

  ✅ 𝐒𝐭𝐞𝐩 𝟏: 𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐢𝐧𝐯𝐢𝐭𝐞 𝐥𝐢𝐧𝐤 𝐟𝐨𝐫 𝐭𝐡𝐞 𝐜𝐡𝐚𝐭. (𝐒𝐤𝐢𝐩 𝐭𝐡𝐢𝐬 𝐬𝐭𝐞𝐩 𝐢𝐟 𝐭𝐡𝐞 𝐚𝐜𝐜𝐨𝐮𝐧𝐭 𝐮𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 𝐬𝐭𝐫𝐢𝐧𝐠 𝐬𝐞𝐬𝐬𝐢𝐨𝐧 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚 𝐦𝐞𝐦𝐛𝐞𝐫).

  ✅ 𝐒𝐭𝐞𝐩 𝟐: 𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐥𝐢𝐧𝐤 𝐭𝐨 𝐭𝐡𝐞 𝐩𝐨𝐬𝐭(𝐬).


**FOR BOT CHATS 🤖**

[  ⚙️ 𝐅𝐨𝐫𝐦𝐚𝐭: 𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐥𝐢𝐧𝐤 𝐰𝐢𝐭𝐡 /𝐛/, 𝐭𝐡𝐞 𝐛𝐨𝐭'𝐬 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞, 𝐚𝐧𝐝 𝐭𝐡𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐈𝐃. 𝐘𝐨𝐮 𝐦𝐢𝐠𝐡𝐭 𝐧𝐞𝐞𝐝 𝐭𝐨 𝐮𝐬𝐞 𝐚𝐧 𝐮𝐧𝐨𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐜𝐥𝐢𝐞𝐧𝐭 𝐭𝐨 𝐠𝐞𝐭 𝐭𝐡𝐞 𝐈𝐃. 𝐄𝐱𝐚𝐦𝐩𝐥𝐞:  ]

```
https://t.me/b/botusername/4321
```

**MULTI POSTS 🔗**

[  𝐅𝐨𝐫𝐦𝐚𝐭 : 𝐒𝐞𝐧𝐝 𝐩𝐮𝐛𝐥𝐢𝐜 / 𝐩𝐫𝐢𝐯𝐚𝐭𝐞 𝐩𝐨𝐬𝐭 𝐥𝐢𝐧𝐤𝐬 𝐚𝐬 𝐞𝐱𝐩𝐥𝐚𝐢𝐧𝐞𝐝 𝐚𝐛𝐨𝐯𝐞 𝐮𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 "𝐟𝐫𝐨𝐦 - 𝐭𝐨" 𝐟𝐨𝐫𝐦𝐚𝐭 𝐭𝐨 𝐬𝐞𝐧𝐝 𝐦𝐮𝐥𝐭𝐢𝐩𝐥𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬. 𝐄𝐱𝐚𝐦𝐩𝐥𝐞𝐬:  ]

```
https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120
```                   
"""


# infinty polling
bot.run()
