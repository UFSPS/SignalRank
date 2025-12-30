from discord.ext import commands
from database.db import db
from datetime import datetime, timezone
import traceback

class MessageTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = db["users"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        now_utc = datetime.now(timezone.utc).isoformat()

        try:
            self.users.update_one(
                {"discord_id": user_id},
                {"$setOnInsert": {
                    "level": 1,
                    "points": 0,
                    "metadata": {"recorded_msgs": 0, "last_msg": now_utc}
                }},
                upsert=True
            )

            self.users.update_one(
                {"discord_id": user_id},
                {
                    "$inc": {"points": 1, "metadata.recorded_msgs": 1},
                    "$set": {"metadata.last_msg": now_utc}
                }
            )

            user_data = self.users.find_one({"discord_id": user_id})
            current_points = user_data.get("points", 0)
            print(f"[TRACK] {message.author} now has {current_points} points")

        except Exception as e:
            print(f"[ERROR] Failed to update points for user {message.author} ({user_id}): {e}")
            traceback.print_exc()

        finally:
            await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(MessageTracker(bot))
