import os

class Config():
    # Koyeb Environment Variable Checker
    ENV = bool(os.environ.get('ENV', True))
    
    # Koyeb Environment Variables থেকে নিরাপদ তথ্য গ্রহণ
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    
    # Neon.tech ডাটাবেজের SQLAlchemy সাপোর্টেড Connection String ফরম্যাট
    DATABASE_URL = os.environ.get("DATABASE_URL", None)
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    APP_ID = int(os.environ.get("APP_ID", 0))
    API_HASH = os.environ.get("API_HASH", None)
    
    # SUDO_USERS (Multiple Admin IDs Space-separated)
    sudo_input = os.environ.get("SUDO_USERS", "")
    SUDO_USERS = list(set(int(x) for x in sudo_input.split())) if sudo_input else []


class Messages():
    HELP_MSG = [
        ".",
        "**Force Subscribe Bot**\n__গ্রুপের মেম্বারদের নির্দিষ্ট চ্যানেলে জয়েন করানো নিশ্চিত করতে এই বটটি ব্যবহার করুন। জয়েন না থাকলে বট মেম্বারকে মিউট করে দেবে।__",
        
        "**Setup Guide**\n__১. বটকে আপনার গ্রুপে Admin করুন (Ban/Mute Users পারমিশন দিন)।\n২. নির্দিষ্ট চ্যানেলটিতেও বটকে Admin করুন।__",
        
        "**Commands**\n__/ForceSubscribe - বর্তমান সেটিংস দেখতে।\n/ForceSubscribe disable - ফোর্সবট বন্ধ করতে।\n/ForceSubscribe {channel username} - চ্যানেল সেটআপ করতে।\n/ForceSubscribe clear - বটের মিউট করা সবাইকে একসাথে আনমিউট করতে।\n\nAlias: /FSub__",
        
        "**Sudo Commands**\n__/broadcast - বটের প্রাইভেট ইউজারদের ব্রডকাস্ট পাঠাতে।\n/gcast - বটের সব গ্রুপে ব্রডকাস্ট পাঠাতে।\n/stats - ডাটাবেজ স্ট্যাটাস দেখতে।__"
    ]

    START_MSG = "**হে [{}](tg://user?id={})!**\n__আমি একটি Force Subscribe Bot। গ্রুপে নিয়ম বজায় রাখতে সাহায্য করি। আরও জানতে /help লিখুন।__"
    
    # ইন-গ্রুপ অ্যালার্ট ও পপ-আপ মেসেজসমূহ
    UNMUTED_ALERT = "🎉 অভিনন্দন! আপনি সফলভাবে চ্যানেলে জয়েন করেছেন। গ্রুপে আপনার মিউট তুলে নেওয়া হয়েছে।"
    NOT_JOINED_ALERT = "⚠️ আপনি এখনও আমাদের চ্যানেলে জয়েন করেননি! দয়া করে আগে চ্যানেলে জয়েন করুন, তারপর এই বোতামে চাপ দিন।"
    ADMIN_PERM_ERROR = "❌ এই কমান্ডটি কেবল গ্রুপের ওনার বা অ্যাডমিন ব্যবহার করতে পারবেন।"
