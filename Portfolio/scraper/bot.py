import discord
from scraper import Scraper
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def build_message(item):
  embed = discord.Embed(type="rich", title=item["name"])
  embed.colour = discord.Colour.brand_red()
  embed.description = item["brand"]
  embed.set_author(name="jikime")
  embed.set_footer(text="copyright")
  embed.set_thumbnail(url=item["image"])
  embed.url = item["url"]
  embed.add_field(name="원래 가격", value=item["original_price"], inline=True)
  embed.add_field(name="세일 가격", value=item  ["sale_price"], inline=True)
  
  return embed
  
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
      return

    if message.content.startswith('$hello'):
      await message.channel.send('Hello!')
        
    if message.content.startswith("!무신사베스트"):
      # 무신사 베스트 결과를 출력한다.
      scraper = Scraper(limit=5)
      results = scraper.do()
      embeds = []
      for item in results:
        embed = build_message(item)
        embeds.append(embed)
      
      await message.channel.send(embeds=embeds)

# scraper token
discord_token = os.getenv("DISCORD_API_KEY")  

# langchain 스터디 token
discord_token = os.getenv("DISCORD_API_KEY2")  

client.run(discord_token)
