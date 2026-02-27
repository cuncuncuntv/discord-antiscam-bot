import discord
from discord.ext import commands
import re
import os
from datetime import timedelta

TOKEN = os.getenv("TOKEN")

# ===== SCAM DATA =====
SCAM_KEYWORDS = [
    "free nitro",
    "steam gift",
    "claim reward",
    "airdrop",
    "free steam",
    "nitro free",
    "50$ gift",
    "LAUNCH casewin"
]

SCAM_DOMAINS = [
    "discordnitro",
    "free-nitro",
    "steamgift",
    "nitrofree",
    "airdrop-crypto",
    "LAUNCH casewin"
]

SHORT_LINKS = [
    "bit.ly",
    "tinyurl",
    "cutt.ly",
    "shorturl",
    "steamcommunity.com/105389195"
]

LINK_REGEX = r"(https?:\/\/[^\s]+)"

# ===== BOT SETUP =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

violations = {}

# ===== READY =====
@bot.event
async def on_ready():
    print(f"✅ Anti-Scam Active: {bot.user}")

# ===== SCAM CHECK =====
def detect_scam(content: str):
    text = content.lower()

    # keyword
    for word in SCAM_KEYWORDS:
        if word in text:
            return True

    # links
    links = re.findall(LINK_REGEX, text)

    for link in links:
        for domain in SCAM_DOMAINS:
            if domain in link:
                return True

        for short in SHORT_LINKS:
            if short in link:
                return True

    return False

# ===== AUTO SCAN MESSAGE =====
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if not message.guild:
        return

    if detect_scam(message.content):

        user = message.author

        # delete message
        try:
            await message.delete()
        except:
            pass

        # warning message
        warn = await message.channel.send(
            f"⚠️ {user.mention} tin nhắn nghi scam đã bị xoá!"
        )
        await warn.delete(delay=5)

        # count violations
        violations[user.id] = violations.get(user.id, 0) + 1

        print(f"SCAM removed from {user}")

        # timeout sau 2 lần
        if violations[user.id] >= 2:
            try:
                await user.timeout(
                    timedelta(minutes=10),
                    reason="Sending scam links"
                )

                await message.channel.send(
                    f"🔇 {user.mention} đã bị timeout 10 phút vì spam scam.",
                    delete_after=5
                )
            except Exception as e:
                print("Timeout error:", e)

    await bot.process_commands(message)

print("TOKEN =", TOKEN)
bot.run(TOKEN)







