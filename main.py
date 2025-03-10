import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
from dotenv import load_dotenv

load_dotenv() # Carregando o token do arquivo .env
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None: # Verifique se o token foi carregado corretamente
    print("❌ Token não encontrado. Verifique o arquivo .env.")
    exit()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

##--- RICH PRESENCE ---##

activities = [
    discord.Game("TL Viih - Discord 🍄"),
    discord.Activity(type=discord.ActivityType.watching, name="Lives da Viih 🍄"),
    discord.Game("Ajudando no servidor 😎"),
    discord.Activity(type=discord.ActivityType.watching, name="streams de games 🎮"),
    #discord.Activity(type=discord.ActivityType.listening, name="Música relaxante 🎶")
]

async def change_activity():
    while True:
        await asyncio.sleep(60)  # Muda a atividade a cada 60 segundos (1 minuto)
        activity = random.choice(activities)  # Escolhe uma atividade aleatória da lista
        await bot.change_presence(activity=activity)

##--- INICIALIZANDO ---##

@bot.event
async def on_ready():
    print("✅ Bot inicializado com sucesso!")
    
    # Iniciar a função que muda a atividade periodicamente
    bot.loop.create_task(change_activity())

    # Sincronizar os comandos com o servidor (slash)
    await bot.tree.sync()
    print("✅ Comandos Slash sincronizados com sucesso!")

##--- RESPOSTAS AO MENCIONAR ---##

@bot.event
async def on_message(message):
    # Ignora o próprio bot para evitar respostas infinitas
    if message.author == bot.user:
        return

    # Verifica se o bot foi mencionado
    if bot.user.mentioned_in(message):
        respostas = [
            f'Você me chamou, {message.author.mention}? Como posso ajudar?',
            f'Oi, {message.author.mention}, em que posso te ajudar?',
            f'Fala, {message.author.mention}, o que você precisa?',
            f'Estou aqui, {message.author.mention}. O que você quer?'
        ]
        # Escolhe uma resposta aleatória
        resposta_aleatoria = random.choice(respostas)
        await message.channel.send(resposta_aleatoria)

    await bot.process_commands(message)

##--- EVENTO DE ENTRADA ---##

@bot.event
async def on_member_join(membro: discord.Member):
    canal = bot.get_channel(1330013786593296446)  # ID do canal
    if canal:
        await canal.send(f"{membro.mention} Olá!")

##--- COMANDO /STATUS ---##

@bot.tree.command(name="status", description="Verificar a latência do bot")
async def status(interaction: discord.Interaction):
    latency = bot.latency * 1000  # Converte para milissegundos
    await interaction.response.send_message(f"✅ Está tudo ok! Latência atual: {latency:.2f} ms", ephemeral=True)

##--- COMANDO /INFO ---##

@bot.tree.command(name="info", description="Informações sobre o bot")
async def info(interaction: discord.Interaction):
    info_embed = discord.Embed(
        title="Nome: Ayla🌺",
        description="Olá, estou atualmente na versão 0.1, sendo programada em Python!\n\nAqui estão alguns comandos. ⚙️\n\n• /Info ⚙️\n• /Divulgar (link)\n• Em Breve...",
        color=discord.Color.green()
    )
    imagem = discord.File("img/avatar_Ayla.jpg", "avatar.jpg")
    info_embed.set_thumbnail(url="attachment://avatar.jpg")
    info_embed.set_footer(text="BETA v0.1")
    await interaction.response.send_message(embed=info_embed, file=imagem)

##--- COMANDO /DIVULGAR ---##

@bot.tree.command(name="divulgar", description="Divulgar uma mensagem")
async def divulgar(interaction: discord.Interaction, link: str):
    # Verifica se o link parece válido
    if not link.startswith("http"):
        await interaction.response.send_message("❌ O link fornecido não parece válido. Por favor, forneça um link completo.", ephemeral=True)
        return

    if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Você precisa ter permissão de Administrador ou Gerenciar Mensagens para usar este comando.", ephemeral=True)
        return

    div_embed = discord.Embed(
        title="Divulgação 📢",
        description=f"Mensagem de divulgação: {link}",
        color=discord.Color.gold()
    )
    div_embed.set_footer(text=f"Enviado por: @{interaction.user.name}", icon_url=interaction.user.avatar.url)

    canal_div = bot.get_channel(1330018559564189847)  # ID do canal
    if canal_div:
        await canal_div.send(embed=div_embed)
    
    await interaction.response.send_message("✅ Mensagem de divulgação enviada com sucesso!", ephemeral=True)

##--- PROCESSAMENTO DE ERROS ---##

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Erro no evento {event}: {args} {kwargs}")

# Executando o bot
bot.run(TOKEN)
