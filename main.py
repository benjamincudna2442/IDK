from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from pymongo import MongoClient

API_ID = 26512884
API_HASH = "c3f491cd59af263cfc249d3f93342ef8"
BOT_TOKEN = "8131788185:AAGo6vuX5GHPOaxoL-zUhhTzNSmmppEbM-c"
BOT_USERNAME = "abirxdhackz_bot"  # replace with your bot username

MONGO_URI = "mongodb+srv://ytpremium4434360:zxx1VPDzGW96Nxm3@itssmarttoolbot.dhsl4.mongodb.net/?retryWrites=true&w=majority&appName=ItsSmartToolBot"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["SangmataBot"]
history_collection = db["user_history"]

app = Client("sangmata_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_timestamp():
    return datetime.now().strftime("%d/%m/%y %H:%M:%S")

def get_last_entry(user_id):
    return history_collection.find_one({"user_id": user_id}, sort=[("timestamp", -1)])

def save_user_entry(user_id, name, username):
    history_collection.insert_one({
        "user_id": user_id,
        "timestamp": get_timestamp(),
        "name": name,
        "username": username or "None"
    })

def get_history(user_id):
    entries = list(history_collection.find({"user_id": user_id}))
    names, usernames = [], []
    for entry in entries:
        if entry['name'] not in [n.split("] ", 1)[-1] for n in names]:
            names.append(f"[{entry['timestamp']}] {entry['name']}")
        if entry['username'] != "None" and entry['username'] not in [u.split("] @", 1)[-1] for u in usernames]:
            usernames.append(f"[{entry['timestamp']}] @{entry['username']}")
    return names, usernames

@app.on_message(filters.private & filters.text)
async def handle_private(client: Client, message: Message):
    text = message.text.strip().lower()

    if text in ["start", "/start"]:
        msg = (
            "Hello!\n\n"
            "If you're a group admin:\n"
            "You can add this bot by clicking the button below. "
            "Make sure that you add the SangMata bot as ADMIN with Manage Group permission so that it can work properly!\n\n"
            "If you want to query a user history:\n"
            "There are 3 ways,\n"
            "1. Forward the user's message here\n"
            "2. Type and send their ID or username (donators only)\n"
            "3. Use history or allhistory commands. Send help for more info.\n\n"
            "If you need help:\n"
            "Just type help or join our support group @TheSmartDev to ask for help."
        )
        return await client.send_message(
            message.chat.id,
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Add Sangmata to my Group", url=f"https://t.me/{BOT_USERNAME}?startgroup")
            ]])
        )

    if text in ["help", "/help"]:
        return await client.send_message(
            message.chat.id,
            "Type history as a reply to a user or just send their user ID here to see past name/username logs.\nYou can also forward their message here."
        )

    if text.isdigit():
        user_id = int(text)
        names, usernames = get_history(user_id)
        if not names and not usernames:
            return await client.send_message(message.chat.id, "No history found.")
        msg = f"History for `{user_id}`\n\n"
        msg += "Names:\n" + "\n".join([f"{i+1:02d}. {n}" for i, n in enumerate(names)]) + "\n\n"
        msg += "Usernames:\n" + "\n".join([f"{i+1:02d}. {u}" for i, u in enumerate(usernames)])
        return await client.send_message(message.chat.id, msg)

@app.on_message(filters.group & ~filters.service)
async def group_activity(client: Client, message: Message):
    user = message.from_user
    if not user:
        return

    try:
        await client.set_chat_protected_content(message.chat.id, True)
    except Exception:
        pass

    user_id = user.id
    name = user.first_name + (f" {user.last_name}" if user.last_name else "")
    username = user.username
    last = get_last_entry(user_id)

    if not last or last['name'] != name or last['username'] != (username or "None"):
        save_user_entry(user_id, name, username)

        if last:
            if last['username'] != (username or "None"):
                await client.send_message(
                    message.chat.id,
                    f"**User `{user_id}` changed username from `@{last['username']}` to `@{username or 'None'}` **"
                )
            if last['name'] != name:
                await client.send_message(
                    message.chat.id,
                    f"** User `{user_id}` changed name from \"{last['name']}\" to \"{name}\"**"
                )

app.run()