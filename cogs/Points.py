from discord.ext import commands
from database.db import db

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = db["users"]

    @commands.command()
    async def points(self, ctx):
        user_id = str(ctx.author.id)
        user = self.users.find_one({"discord_id": user_id})

        if not user:
            await ctx.send("You have no points yet.")
        else:
            await ctx.send(f"You have {user['points']} points.")

    @commands.command()
    async def addpoints(self, ctx, amount: int):
        user_id = str(ctx.author.id)
        self.users.update_one(
            {"discord_id": user_id},
            {
                "$inc": {"points": amount},
                "$setOnInsert": {
                    "level": 1,
                    "metadata": {"recorded_msgs": 0}
                }
            },
            upsert=True
        )
        await ctx.send(f"Added {amount} points!")

async def setup(bot):
    await bot.add_cog(Points(bot))