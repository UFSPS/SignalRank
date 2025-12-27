import discord
from discord.ext import commands
import requests
import html
import random
import asyncio

# Store active trivia sessions per channel
active_sessions = {}

def get_session_token():
    """Retrieve a session token from the Open Trivia Database API."""
    try:
        response = requests.get("https://opentdb.com/api_token.php?command=request")
        data = response.json()
        if data["response_code"] == 0:
            return data["token"]
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching session token: {e}")
        return None

def fetch_trivia_questions(amount=1, category=None, difficulty=None, type="multiple", token=None):
    """Fetch trivia questions from the Open Trivia Database API."""
    base_url = "https://opentdb.com/api.php"
    params = {
        "amount": amount,
        "type": type
    }
    if category:
        params["category"] = category
    if difficulty:
        params["difficulty"] = difficulty
    if token:
        params["token"] = token

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching questions: {e}")
        return None

def decode_html(text):
    """Decode HTML-encoded text."""
    return html.unescape(text)

def create_question_embed(question_data, answers):
    """Create a Discord embed for the trivia question."""
    question = decode_html(question_data["question"])
    category = decode_html(question_data["category"])
    difficulty = question_data["difficulty"].capitalize()
    
    embed = discord.Embed(
        title="🎯 Trivia Question",
        description=question,
        color=discord.Color.blue()
    )
    embed.add_field(name="Category", value=category, inline=True)
    embed.add_field(name="Difficulty", value=difficulty, inline=True)
    
    # Add answer options
    options = ""
    for i, answer in enumerate(answers, 1):
        options += f"**{i}.** {answer}\n"
    embed.add_field(name="Options", value=options, inline=False)
    embed.set_footer(text="Reply with the number (1-4) of your answer!")
    
    return embed

async def trivia(bot, ctx, difficulty: str = None):
    channel_id = ctx.channel.id
    
    # Check if there's already an active session in this channel
    if channel_id in active_sessions:
        await ctx.send("⚠️ There's already an active trivia question in this channel! Please answer it first.")
        return
    
    # Validate difficulty
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty and difficulty.lower() not in valid_difficulties:
        await ctx.send(f"⚠️ Invalid difficulty! Choose from: easy, medium, hard")
        return
    
    difficulty = difficulty.lower() if difficulty else None
    
    # Fetch a trivia question
    await ctx.send("🔄 Fetching trivia question...")
    token = get_session_token()
    data = fetch_trivia_questions(amount=1, difficulty=difficulty, token=token)
    
    if not data or data["response_code"] != 0:
        await ctx.send("❌ Error fetching trivia question. Please try again!")
        return
    
    question_data = data["results"][0]
    correct_answer = decode_html(question_data["correct_answer"])
    incorrect_answers = [decode_html(ans) for ans in question_data["incorrect_answers"]]
    
    # Combine and shuffle answers
    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)
    
    # Store the session
    active_sessions[channel_id] = {
        "correct_answer": correct_answer,
        "user_id": ctx.author.id,
        "answers": all_answers
    }
    
    # Send the question
    embed = create_question_embed(question_data, all_answers)
    await ctx.send(embed=embed)
    
    # Wait for answer (30 seconds timeout)
    def check(m):
        return (m.channel.id == channel_id and 
                m.author.id == ctx.author.id and 
                m.content.isdigit() and 
                1 <= int(m.content) <= 4)
    
    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        
        # Check answer
        user_answer_index = int(msg.content) - 1
        user_answer = all_answers[user_answer_index]
        
        if user_answer == correct_answer:
            await ctx.send(f"✅ **Correct!** Well done, {ctx.author.mention}! 🎉")
        else:
            await ctx.send(f"❌ **Incorrect!** The correct answer was: **{correct_answer}**")
        
        # Clean up session
        del active_sessions[channel_id]
        
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The correct answer was: **{correct_answer}**")
        del active_sessions[channel_id]

async def trivia_multi(bot, ctx, num_questions: int = 5, difficulty: str = None):
    channel_id = ctx.channel.id
    
    # Check if there's already an active session
    if channel_id in active_sessions:
        await ctx.send("⚠️ There's already an active trivia session in this channel!")
        return
    
    # Validate inputs
    if not 1 <= num_questions <= 20:
        await ctx.send("⚠️ Number of questions must be between 1 and 20!")
        return
    
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty and difficulty.lower() not in valid_difficulties:
        await ctx.send(f"⚠️ Invalid difficulty! Choose from: easy, medium, hard")
        return
    
    difficulty = difficulty.lower() if difficulty else None
    
    # Mark session as active
    active_sessions[channel_id] = {"in_progress": True}
    
    # Fetch questions
    await ctx.send(f"🔄 Fetching {num_questions} trivia questions...")
    token = get_session_token()
    data = fetch_trivia_questions(amount=num_questions, difficulty=difficulty, token=token)
    
    if not data or data["response_code"] != 0:
        await ctx.send("❌ Error fetching trivia questions. Please try again!")
        del active_sessions[channel_id]
        return
    
    questions = data["results"]
    score = 0
    
    # Ask each question
    for i, question_data in enumerate(questions, 1):
        correct_answer = decode_html(question_data["correct_answer"])
        incorrect_answers = [decode_html(ans) for ans in question_data["incorrect_answers"]]
        
        # Combine and shuffle answers
        all_answers = incorrect_answers + [correct_answer]
        random.shuffle(all_answers)
        
        # Send question
        embed = create_question_embed(question_data, all_answers)
        embed.title = f"🎯 Question {i}/{num_questions}"
        await ctx.send(embed=embed)
        
        # Wait for answer
        def check(m):
            return (m.channel.id == channel_id and 
                    m.author.id == ctx.author.id and 
                    m.content.isdigit() and 
                    1 <= int(m.content) <= 4)
        
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=check)
            
            user_answer_index = int(msg.content) - 1
            user_answer = all_answers[user_answer_index]
            
            if user_answer == correct_answer:
                await ctx.send(f"✅ **Correct!**")
                score += 1
            else:
                await ctx.send(f"❌ **Incorrect!** The correct answer was: **{correct_answer}**")
            
            # Small delay before next question
            if i < num_questions:
                await asyncio.sleep(2)
                
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The correct answer was: **{correct_answer}**")
            if i < num_questions:
                await asyncio.sleep(2)
    
    # Show final score
    percentage = (score / num_questions) * 100
    await ctx.send(f"🏆 **Game Over!** {ctx.author.mention}\nYour score: **{score}/{num_questions}** ({percentage:.1f}%)")
    
    # Clean up session
    del active_sessions[channel_id]

async def trivia_help_cmd(ctx):
    embed = discord.Embed(
        title="🎮 SignalRank - Trivia Commands",
        description="Here are all the available trivia commands:",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name=".trivia [difficulty]",
        value="Start a single trivia question\nExample: `.trivia` or `.trivia hard`",
        inline=False
    )
    
    embed.add_field(
        name=".trivia_multi [num] [difficulty]",
        value="Start a multi-question trivia game (1-20 questions)\nExample: `.trivia_multi 10` or `.trivia_multi 5 easy`",
        inline=False
    )
    
    embed.add_field(
        name="Difficulties",
        value="easy, medium, hard",
        inline=False
    )
    
    embed.set_footer(text="You have 30 seconds to answer each question!")
    
    await ctx.send(embed=embed)