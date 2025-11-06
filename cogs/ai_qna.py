from discord.ext import commands
import discord
from services import ai as ai_service

class QnA(commands.Cog):
    """Cog to handle mention-based Q&A with a generative AI backend.

    Behavior:
    - Listens for messages that mention the bot.
    - Removes the mention text and treats the remaining content as the prompt.
    - Calls `services.ai.generate_answer(prompt)` and replies with the result.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore bots
        if message.author.bot:
            return

        # check if the bot was mentioned
        if self.bot.user and self.bot.user in message.mentions:
            # Remove mention tokens from the message content to get the prompt.
            content = message.content
            # Support both <@id> and <@!id> mention formats
            if message.mentions:
                for m in message.mentions:
                    content = content.replace(f"<@!{m.id}>", "")
                    content = content.replace(f"<@{m.id}>", "")

            prompt = content.strip()
            if not prompt:
                await message.channel.send("Hi — mention me with a question and I'll try to answer it.")
                return

            # Indicate typing while we wait for the AI
            async with message.channel.typing():
                try:
                    answer = await ai_service.generate_answer(prompt)
                except Exception as e:
                    answer = f"Error generating answer: {e}"

            # Reply without pinging the author
            try:
                await message.reply(answer, mention_author=False)
            except Exception:
                # Fall back to channel send if reply fails for some reason
                await message.channel.send(answer)


async def setup(bot: commands.Bot):
    await bot.add_cog(QnA(bot))
