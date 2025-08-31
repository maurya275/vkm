import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message

import config
from AnonXMusic import app
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils.database import get_top_groups, get_served_chats
from AnonXMusic.utils.decorators.language import language
from config import BANNED_USERS

@app.on_message(filters.command(["topgc", "topgroups"]) & ~BANNED_USERS)
@language
async def top_groups_command(client, message: Message, _):
    """Show top 10 groups by songs played"""
    
    # Send initial message
    msg = await message.reply_text("🔍 **Fetching top groups data...**")
    
    try:
        # Get top groups from database
        top_groups = await get_top_groups(10)
        
        if not top_groups:
            return await msg.edit_text("❌ **No group statistics found!**\n\n*Groups need to play songs to appear in rankings.*")
        
        # Build the ranking message
        text = f"🏆 **TOP 10 GROUPS BY SONGS PLAYED**\n\n"
        text += f"📊 **Ranked by total songs played**\n"
        text += f"🎵 **Bot:** {app.mention}\n\n"
        
        # Add rankings
        for i, group in enumerate(top_groups, 1):
            chat_id = group.get("chat_id", "Unknown")
            chat_title = group.get("chat_title", "Unknown Group")
            songs_played = group.get("songs_played", 0)
            total_users = group.get("total_users", "Unknown")
            last_played = group.get("last_played")
            
            # Truncate long group names
            if len(chat_title) > 25:
                chat_title = chat_title[:22] + "..."
            
            # Format last played time
            if last_played:
                if isinstance(last_played, str):
                    time_str = "Recently"
                else:
                    time_str = last_played.strftime("%d/%m/%Y")
            else:
                time_str = "Unknown"
            
            # Add ranking emoji
            if i == 1:
                emoji = "🥇"
            elif i == 2:
                emoji = "🥈"
            elif i == 3:
                emoji = "🥉"
            else:
                emoji = f"{i}."
            
            text += f"{emoji} **{chat_title}**\n"
            text += f"    ├ 🎵 Songs: `{songs_played:,}`\n"
            text += f"    ├ 👥 Users: `{total_users}`\n"
            text += f"    └ 📅 Last: `{time_str}`\n\n"
        
        # Add footer
        total_served = len(await get_served_chats())
        text += f"📈 **Total Served Groups:** `{total_served:,}`\n"
        text += f"⏰ **Updated:** `{datetime.now().strftime('%d/%m/%Y %H:%M')}`"
        
        # Send the ranking
        await msg.edit_text(text, disable_web_page_preview=True)
        
    except Exception as e:
        await msg.edit_text(f"❌ **Error occurred while fetching data!**\n\n**Error:** `{str(e)}`")
