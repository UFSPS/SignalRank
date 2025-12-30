import discord
from discord.ext import commands
from database.db import db

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = db["users"]

    @commands.command()
    async def leaderboard(self, ctx):
        top = list(self.users.find().sort("points", -1).limit(10))

        if not top:
            return await ctx.send("Leaderboard is empty.")

        description = ""

        for i, user in enumerate(top, start=1):
            user_id = int(user["discord_id"])
            try:
                member = await ctx.guild.fetch_member(user_id)
                name = member.mention
            except:
                name = f"<@{user_id}>"

            description += f"**#{i} — {name}:** {user['points']} points\n"

        embed = discord.Embed(
            title="Leaderboard — Top 10 Users",
            description=description,
            color=0xFFD700
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
