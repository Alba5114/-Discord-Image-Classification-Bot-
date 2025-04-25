import discord
import random
from discord.ext import commands
import numpy as np
from PIL import Image, ImageOps
from keras.models import load_model
import os
import aiohttp
import io


model = load_model("keras_model.h5", compile=False)
class_names = open("labels.txt", "r").readlines()
letters = ("abcdefghijklmnopqrstuvxyz")


intents = discord.Intents.default()
intents.message_content = True
model = load_model("keras_model.h5", compile=False)
class_names = open("labels.txt", "r", encoding="UTF-8").readlines()

bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send(f'hi im {bot.user}')

@bot.command()
async def rng(ctx):
    x = random.randint(1, 2)
    win = random.randint(1, 2)
    await ctx.send(f'You rolled: {x}')
    await ctx.send(f'The winning number was: {win}')

    if x == win:
        await ctx.send("**you won the gazilliard dollar jackpot!!!**")

@bot.command()
async def heh(ctx, count_heh = 5):
    await ctx.send("he" * count_heh)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                await message.channel.send("Processing...")

                try:
                    # Görseli indir
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:
                            if resp.status != 200:
                                await message.channel.send('Failed to download image')
                                return
                            data_bytes = await resp.read()

                    # Görseli işle
                    image = Image.open(io.BytesIO(data_bytes)).convert("RGB")
                    size = (224, 224)
                    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
                    image_array = np.asarray(image)
                    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
                    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
                    data[0] = normalized_image_array

                    # Tahmin yap
                    prediction = model.predict(data)
                    index = np.argmax(prediction)
                    confidence_score = prediction[0][index]
                    class_name = class_names[index].strip()
                    class_name = " ".join(class_name.split(" "[1:]))

                    # Cevap oluştur
                    response = f"**Guess:** `{class_name}`\n**Confidence Score:** `{confidence_score:.2f}`\n"
                    new_class_name = class_name.strip()      


                    # Öneriyi oku 
                    print(class_name)
                    file_name = class_name.lower() + ".txt"
                    if os.path.exists(file_name):
                        with open(file_name, "r", encoding="UTF-8") as f:
                            suggestion = f.read()
                            response += f"**Food suggestion:**\n```{suggestion}```"
                    else:
                        response += "_No file was found._"

                    await message.channel.send(response)

                except Exception as e:
                    await message.channel.send(f"Warning: {e}")

    await bot.process_commands(message)  # Komutları da işlesin

bot.run("bahhh")