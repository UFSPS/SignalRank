from discord.ext import commands
from services import trivia as trivia_service

class Trivia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def trivia(self, ctx, difficulty: str = None):
        '''
        Start a single trivia question.

        Usage: .trivia or .trivia easy/medium/hard
        '''
        await trivia_service.trivia(self.bot, ctx, difficulty)
    
    @commands.command()
    async def trivia_multi(self, ctx, num_questions: int = 5, difficulty: str = None):
        '''
        Start a trivia game with multiple questions.

        Usage: .trivia_multi 5 or .trivia_multi 10 hard
        '''
        await trivia_service.trivia_multi(self.bot, ctx, num_questions, difficulty)
    
    @commands.command()
    async def trivia_help(self, ctx):
        '''
        Display help information for the trivia bot.
        '''
        await trivia_service.trivia_help_cmd(ctx)
              
async def setup(bot: commands.Bot):
    await bot.add_cog(Trivia(bot))