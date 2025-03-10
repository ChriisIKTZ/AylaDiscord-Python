import discord
from discord.ext import commands
from discord import app_commands
import os
import time
import random
import asyncio
import traceback 
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Registra o tempo de início do bot
start_time = time.time()

# Carrega o token do arquivo .env
TOKEN = os.getenv("DISCORD_TOKEN")

# Verifica se o token foi carregado corretamente
if TOKEN is None:
    print("❌ Token não encontrado. Verifique o arquivo .env.")
    exit()

# Define as permissões do bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

##--- RICH PRESENCE ---##

activities = [
    discord.Game("TL Viih - Discord 🍄"),
    discord.Activity(type=discord.ActivityType.watching, name="Lives da Viih 🍄"),
    discord.Game("Ajudando no servidor 😎"),
    #discord.Activity(type=discord.ActivityType.watching, name="streams de games 🎮"),
    discord.Activity(type=discord.ActivityType.listening, name="Mr. Kitty - After Dark")
]

async def change_activity():
    while True:
        await asyncio.sleep(60)  # Muda a atividade a cada 60 segundos (1 minuto)
        activity = random.choice(activities)  # Escolhe uma atividade aleatória da lista
        await bot.change_presence(activity=activity)

##--- INICIALIZAÇÃO DO BOT ---##

@bot.event
async def on_ready():
    """Evento acionado quando o bot é iniciado."""
    print(f"✅ Bot inicializado com sucesso!")
    bot.loop.create_task(change_activity())  # Inicia a troca automática de status
    try:
        await bot.tree.sync()
        print("✅ Comandos Slash sincronizados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")


##--- EVENTO DE MENÇÃO AO BOT ---##

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignora mensagens de bots

    if bot.user.mentioned_in(message) and message.content.strip() == f"<@{bot.user.id}>":
        respostas = [
            'Diga',
            '🍆',
            'O que você quer?',
            'Para de mencionar buceta...',
        ]
        await message.channel.send(random.choice(respostas))

    await bot.process_commands(message)  # Processa comandos normalmente

##--- EVENTO DE ENTRADA DE MEMBRO ---##

@bot.event
async def on_member_join(membro: discord.Member):
    """Evento acionado quando um novo membro entra no servidor."""
    canal = bot.get_channel(00000)  # ID do canal
    if canal:
        await canal.send(f"{membro.mention} Olá!")

##--- COMANDO /STATUS ---##

@bot.tree.command(name="status", description="Verificar a latência do bot")
async def status(interaction: discord.Interaction):
    """Comando para verificar a latência do bot e o tempo de atividade."""
    latency = bot.latency * 1000  # Converte para milissegundos
    uptime = time.time() - start_time  # Calcula o tempo de atividade
    await interaction.response.send_message(f"✅ Está tudo ok! Latência atual: {latency:.2f} ms\nTempo de atividade: {uptime:.0f} segundos", ephemeral=True)

##--- COMANDO /INFO ---##

@bot.tree.command(name="info", description="Informações sobre o bot")
async def info(interaction: discord.Interaction):
    info_embed = discord.Embed(
        title="Nome: Ayla🌺",
        description="Olá, estou atualmente na versão 0.1, sendo programada em Python!",
        color=discord.Color.green()
    )

    imagem_path = "img/avatar_Ayla.jpg"
    
    if os.path.exists(imagem_path):
        imagem = discord.File(imagem_path, filename="avatar.jpg")
        info_embed.set_thumbnail(url="attachment://avatar.jpg")
        await interaction.response.send_message(embed=info_embed, file=imagem)
    else:
        info_embed.set_footer(text="⚠️ Imagem não encontrada.")
        await interaction.response.send_message(embed=info_embed, ephemeral=True)

##--- COMANDO /DIVULGAR ---##

@bot.tree.command(name="divulgar", description="Divulgar uma mensagem")
async def divulgar(interaction: discord.Interaction, link: str):
    """Comando para divulgar uma mensagem com um link."""
    # Verifica se o link é válido
    if not link.startswith("http"):
        await interaction.response.send_message("❌ O link fornecido não parece válido. Por favor, forneça um link completo.", ephemeral=True)
        return

    # Verifica se o usuário tem permissões adequadas
    if not (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_messages):
        await interaction.response.send_message("❌ Você precisa de permissões adequadas para usar este comando.", ephemeral=True)
        return

    # Obtém o avatar do usuário (caso ele não tenha, usa o padrão)
    avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url

    div_embed = discord.Embed(
        title="Divulgação 📢",
        description=f"Mensagem de divulgação: {link}",
        color=discord.Color.gold()
    )
    div_embed.set_footer(text=f"Enviado por: @{interaction.user.name}", icon_url=avatar_url)

    canal_div = bot.get_channel(00000)  # ID do canal
    if canal_div:
        await canal_div.send(embed=div_embed)

    await interaction.response.send_message("✅ Mensagem de divulgação enviada com sucesso!", ephemeral=True)

##--- EXCLUIR MENSSAGEM ---##

@bot.tree.command(name="limpar", description="Remove uma quantidade de mensagens de um canal")
async def limpar(interaction: discord.Interaction, quantidade: int):
    """Comando para excluir mensagens no chat."""
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message('❌ Você não tem permissões para usar este comando.', ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)  # Adia a resposta para evitar erro de tempo limite
    
    try:
        deleted = await interaction.channel.purge(limit=quantidade)
        await interaction.followup.send(f'✅ {len(deleted)} mensagens excluídas!', ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ Não tenho permissão para excluir mensagens neste canal.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ Ocorreu um erro ao tentar excluir mensagens: {e}", ephemeral=True)


##--- PROCESSAMENTO DE ERROS ---##

@bot.event
async def on_error(event, *args, **kwargs):
    """Captura e exibe erros detalhados."""
    print(f"❌ Erro no evento {event}: {args} {kwargs}")
    traceback.print_exc()  # Exibe a stacktrace completa do erro

# Inicia o bot com o token carregado
bot.run(TOKEN)
