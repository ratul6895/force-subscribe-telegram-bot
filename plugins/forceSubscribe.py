import time
import logging
import asyncio
from Config import Config
from pyrogram import Client, filters
from sql_helpers import fs_settings, add_channel, disapprove
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(lambda _, __, query: query.data == "onUnMuteRequest")

@Client.on_callback_query(static_data_filter)
async def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = fs_settings(chat_id)
    
    if chat_db:
        channel = chat_db.channel
        try:
            # চেক করা ইউজার চ্যানেলে জয়েন করেছে কিনা
            await client.get_chat_member(channel, user_id)
            # আনমিউট করা
            await client.unban_chat_member(chat_id, user_id)
            await cb.answer("🎉 অভিনন্দন! আপনি সফলভাবে চ্যানেলে জয়েন করেছেন। আপনার মিউট তুলে নেওয়া হয়েছে।", show_alert=True)
            try:
                await cb.message.delete()
            except:
                pass
        except UserNotParticipant:
            await cb.answer("❗ আপনি এখনও চ্যানেলে জয়েন করেননি! দয়া করে আগে চ্যানেলে জয়েন করুন, তারপর এই বোতামে চাপ দিন।", show_alert=True)
        except Exception as e:
            await cb.answer(f"❗ সমস্যা: {e}", show_alert=True)

@Client.on_message(filters.group & ~filters.service, group=1)
async def _check_member(client, message):
    if not message.from_user:
        return
        
    chat_id = message.chat.id
    chat_db = fs_settings(chat_id)
    
    if chat_db:
        user_id = message.from_user.id
        
        # অ্যাডমিন বা সুডো ইউজারদের স্কিপ করা
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or user_id in Config.SUDO_USERS:
            return

        channel = chat_db.channel
        try:
            await client.get_chat_member(channel, user_id)
        except UserNotParticipant:
            try:
                # মেম্বারকে মিউট করা
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                
                # সতর্কবার্তা পাঠানো
                sent_message = await message.reply_text(
                    f"হে {message.from_user.mention}, আপনি আমাদের [চ্যানেলে](https://t.me/{channel}) জয়েন করেননি।\nগ্রুপে কথা বলতে প্রথমে চ্যানেলে জয়েন করুন এবং নিচের **UnMute Me** বাটনে চাপ দিন।",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("UnMute Me", callback_data="onUnMuteRequest")]]
                    )
                )
                
                # ৫ মিনিট পর অটো-ডিলিট করার লজিক (গ্রুপ ক্লিন রাখার জন্য)
                await asyncio.sleep(300)
                try:
                    await sent_message.delete()
                    await message.delete()
                except:
                    pass
            except ChatAdminRequired:
                pass
        except ChatAdminRequired:
            pass

@Client.on_message(filters.command(["forcesubscribe", "fsub"]) & filters.group)
async def config(client, message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == ChatMemberStatus.OWNER or message.from_user.id in Config.SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1].replace("@", "")
            
            if input_str.lower() in ("off", "no", "disable"):
                disapprove(chat_id)
                await message.reply_text("❌ **Force Subscribe সফলভাবে বন্ধ করা হয়েছে।**")
            elif input_str.lower() == 'clear':
                sent_message = await message.reply_text('**মিউট করা সব মেম্বারকে আনমিউট করা হচ্ছে...**')
                try:
                    async for chat_member in client.get_chat_members(chat_id, filter="restricted"):
                        await client.unban_chat_member(chat_id, chat_member.user.id)
                        await asyncio.sleep(1)
                    await sent_message.edit('✅ **সবাইকে আনমিউট করা হয়েছে।**')
                except Exception as e:
                    await sent_message.edit(f'❗ **ভুল:** {e}')
            else:
                try:
                    await client.get_chat_member(input_str, "me")
                    add_channel(chat_id, input_str)
                    await message.reply_text(f"✅ **Force Subscribe চালু করা হয়েছে**\nচ্যানেল: [@{input_str}](https://t.me/{input_str})", disable_web_page_preview=True)
                except UserNotParticipant:
                    await message.reply_text(f"❗ **বটটি @{input_str} চ্যানেলে Admin নয়!** আগে চ্যানেলটিতে বটকে Admin করুন।", disable_web_page_preview=True)
                except (UsernameNotOccupied, PeerIdInvalid):
                    await message.reply_text("❗ **চ্যানেলের ইউজারনেম সঠিক নয়।**")
                except Exception as err:
                    await message.reply_text(f"❗ **ERROR:** `{err}`")
        else:
            setting = fs_settings(chat_id)
            if setting:
                await message.reply_text(f"✅ **বর্তমানে Force Subscribe চালু আছে:**\nচ্যানেল: [@{setting.channel}](https://t.me/{setting.channel})", disable_web_page_preview=True)
            else:
                await message.reply_text("❌ **বর্তমানে Force Subscribe বন্ধ আছে।**")
    else:
        await message.reply_text("❗ **কেবল গ্রুপের ওনার এই কমান্ডটি চালাতে পারবেন।**")
