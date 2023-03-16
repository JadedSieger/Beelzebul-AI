import discord
import openai
import os
import asyncio
from gtts import gTTS
from discord import FFmpegPCMAudio
from pydub import AudioSegment
from pydub.playback import play
from aiohttp import web

client = discord.Client(intents = discord.Intents.all())

openai.api_key = " " # get your API key in the OpenAI website.

async def generate_response(message):
    try:
        model_engine = "text-davinci-002"
        prompt = f"User: {message.content}\nAI:"
        response = openai.Completion.create(
            engine = model_engine,
            prompt = prompt,
            max_tokens = 60,
            n = 1,
            stop = None,
            temperature = 0.7,
        )
        return response.choices[0].text
    except Exception as e:
        print(f"Error: {e}")
        response = None
    return response

async def speak_in_vc(voice_channel, response):
    try:
        language = "en"
        speech = gTTS(text=response, lang=language, slow=False, tld="co.jp")
        speech.save("./speech/TextToSpeech.mp3")
        audio_file = "./speech/TextToSpeech.mp3"
        voice_client = await voice_channel.connect()
        audio_source = FFmpegPCMAudio(audio_file)
        voice_client.play(audio_source)
        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()  # add this line to make the bot leave the voice channel after TTS is done playing
    except Exception as e:
        print(f"Error: {e}")

prefix = "tex,"

async def keepalive(request):
    return web.Response(text = "I'm alive!")

async def start_webserver():
    app = web.Application()
    app.add_routes([web.get('/', keepalive)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()


@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return
        if not message.content.startswith(prefix):
            return
      
        response = await generate_response(message)
        await message.channel.send(response)

        if message.author.voice and message.author.voice.channel:
            vc = message.author.voice.channel
            await speak_in_vc(vc, response)
    except Exception as e:
        print(f"Error: {e}")

@client.event
async def on_ready():
    try:
        print(f"Logged in as {client.user.name}")
        await client.change_presence(activity=discord.Streaming(name="Streaming your mom", url="https://www.twitch.tv/vedal987"))
    except Exception as e:
        print(f"Error: {e}")

os.environ['BOT KEY'] = " " #get yout Bot Key from Discord Dev Portal.
client.run(os.environ['BOT KEY'])
