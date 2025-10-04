from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        '''Shows Latency'''
        await ctx.send(f"Pong! {self.bot.latency*1000:.2f}ms")

async def setup(bot):
    await bot.add_cog(Commands(bot))