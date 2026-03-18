import discord
from discord.ext import commands
from flask import Flask, request, redirect
import requests
import threading
# ===== 設定 =====
import os
TOKEN = os.environ.get("TOKEN")
CLIENT_ID = 1483597829502140656
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = "https://discord-aura-bot-h98b.onrender.com/callback"
GUILD_ID = 1483503974085558386  # サーバーID
ROLE_NAME = "Member"

# ===== Bot設定 =====
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== Flask設定 =====
import urllib.parse

app = Flask(__name__)

@app.route('/')
def home():
    return '<a href="/login">認証する</a>'

# 👇 外に出す！！
@app.route('/login')
def login():
    redirect_encoded = urllib.parse.quote(REDIRECT_URI, safe="")
    
    oauth_url = (
        f"https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={redirect_encoded}"
        f"&scope=identify%20guilds.join"
    )

    return redirect(oauth_url)

@app.route('/callback')
def callback():
try:
    print("🔥 CALLBACK HIT")

    code = request.args.get("code")
    print("CODE:", code)

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_res = requests.post(
        "https://discord.com/api/oauth2/token",
        data=data,
        headers=headers
    )

    print("STATUS:", token_res.status_code)
    print("BODY:", token_res.text)

    token_json = token_res.json()
    access_token = token_json.get("access_token")

    if not access_token:
        return "アクセストークン取得失敗"

except Exception as e:
    print("ERROR:", e)
    return "ERROR"

# 👇 ここから安全に実行
user_res = requests.get(
    "https://discord.com/api/users/@me",
    headers={"Authorization": f"Bearer {access_token}"}
)

user_json = user_res.json()
user_id = int(user_json["id"])

guild = bot.get_guild(GUILD_ID)
member = guild.get_member(user_id)
role = discord.utils.get(guild.roles, name=ROLE_NAME)

if member and role:
    bot.loop.create_task(member.add_roles(role))

return "認証完了！Discordに戻ってください"

# ===== Bot起動 =====
import threading

def run_bot():
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("BOT ERROR:", e)

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=10000)
