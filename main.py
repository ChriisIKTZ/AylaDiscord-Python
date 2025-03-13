import discord
from discord.ext import commands
from discord import app_commands
import os
import time
import random
import json
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
    discord.Activity(type=discord.ActivityType.listening, name="Mr. Kitty - After Dark")
]

async def change_activity():
    while True:
        try:
            await asyncio.sleep(60)  # Aguarda 1 minuto antes de mudar a atividade
            activity = random.choice(activities)
            await bot.change_presence(activity=activity)
        except (discord.HTTPException, discord.ConnectionClosed, asyncio.CancelledError):
            print("⚠️ Conexão perdida ao tentar atualizar presença. Tentando novamente em 10 segundos...")
            await asyncio.sleep(10)  # Aguarda antes de tentar novamente

##--- INICIALIZAÇÃO DO BOT ---##
@bot.event
async def on_ready():
    print(f"✅ Bot inicializado com sucesso!")
    bot.loop.create_task(change_activity()) # Inicia a mudança de atividades

    try:
        await bot.tree.sync()
        print("✅ Comandos Slash sincronizados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")

##--- EVENTO DE MENÇÃO AO BOT E CONTAGEM DE MENSAGENS ---##
def load_ranking():
    try:
        with open("ranking.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_ranking(data):
    with open("ranking.json", "w") as f:
        json.dump(data, f, indent=4)

ranking = load_ranking()  # Carregar dados ao iniciar

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignora mensagens de bots

    # ✅ Responde se for mencionado
    if bot.user in message.mentions:
        respostas = [
            'Diga',
            '🍆',
            'O que você quer?',
            'Para de mencionar buceta...',
        ]
        await message.channel.send(random.choice(respostas))

    # ✅ Contagem de mensagens para ranking
    user_id = str(message.author.id)

    # Usando o apelido (nickname) se disponível, ou o nome de usuário normal
    user_name = message.author.display_name

    if user_id in ranking:
        ranking[user_id]["messages"] += 1
    else:
        ranking[user_id] = {"name": user_name, "messages": 1}

    save_ranking(ranking)  # Salva no JSON

    await bot.process_commands(message)  # Processa comandos normalmente

##--- EVENTO DE ENTRADA DE MEMBRO ---##
@bot.event
async def on_member_join(membro: discord.Member):
    canal = bot.get_channel(00000)  # ID do canal
    if canal:
        await canal.send(f"{membro.mention} Olá!")

##--- COMANDO /STATUS ---##
@bot.tree.command(name="status", description="Verificar a latência do bot")
async def status(interaction: discord.Interaction):
    latency = bot.latency * 1000
    uptime = time.time() - start_time
    await interaction.response.send_message(
        f"✅ Está tudo ok! Latência: {latency:.2f} ms\nTempo de atividade: {uptime:.0f} segundos",
        ephemeral=True
    )

##--- COMANDO /INFO ---##
@bot.tree.command(name="info", description="Informações sobre o bot")
async def info(interaction: discord.Interaction):
    info_embed = discord.Embed(
        title="🌸 **Ayla Bot** 🌸",
        description="Olá, sou o Ayla! Estou aqui para ajudar no servidor com recursos incríveis e interações divertidas!",
        color=discord.Color.pink()  # Escolha uma cor que combina com o estilo do bot
    )
    
    info_embed.add_field(
        name="🔧 Versão:",
        value="**v0.1** - Em constante atualização para ficar ainda melhor! 🚀",
        inline=False
    )
    
    info_embed.add_field(
        name="📜 **Comandos Disponíveis:**",
        value=(
            "• `/status`: Verifique a latência do bot e o tempo de atividade.\n"
            "• `/ranking`: Veja o ranking de mensagens do servidor.\n"
            "• `/info`: Informações sobre o Ayla Bot.\n"
            "• `/limpar`: Limpar mensagens do canal.\n"
            "• `/divulgar [link]`: Divulgue um link no servidor.\n"
        ),
        inline=False
    )

    info_embed.add_field(
        name="📅 Última Atualização:",
        value="Em breve! Estou sempre sendo aprimorado para mais diversão e utilidade! 🔄",
        inline=False
    )

    info_embed.set_thumbnail(url="https://i.imgur.com/MG3ixny.png")  # URL para uma imagem de miniatura bonita
    info_embed.set_footer(text="Bot criado com 💖 por Chriis ✨", icon_url="https://i.imgur.com/CoCnKIT.jpeg")  # Footer personalizado

    await interaction.response.send_message(embed=info_embed)

##--- COMANDO /RANKING ---##
@bot.tree.command(name="ranking", description="Mostra o ranking de mensagens do servidor")
async def ranking_command(interaction: discord.Interaction):
    ranking_data = load_ranking()
    if not ranking_data:
        await interaction.response.send_message("Ainda não há mensagens registradas!", ephemeral=True)
        return

    sorted_ranking = sorted(ranking_data.items(), key=lambda x: x[1]["messages"], reverse=True)
    top_users = "\n".join(
        [f"**{i+1}. {data['name']}** • {data['messages']} mensagens" for i, (_, data) in enumerate(sorted_ranking[:10])]
    )

    embed = discord.Embed(title="🏆 Ranking de Mensagens", description=top_users, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

##--- COMANDO /LIMPAR ---##
@bot.tree.command(name="limpar", description="Remove uma quantidade de mensagens de um canal")
async def limpar(interaction: discord.Interaction, quantidade: int):
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

##--- PROCESSAMENTO DE ERROS ---##
@bot.event
async def on_error(event, *args, **kwargs):
    erro = traceback.format_exc()
    
    # Canal de logs de erro
    canal_erro = bot.get_channel(00000)  # ID do canal
    
    if canal_erro:
        embed = discord.Embed(
            title="❌ Erro no Bot",
            description=f"**Evento:** `{event}`\n```py\n{erro[:4000]}```",  # Limite de caracteres do embed
            color=discord.Color.red()
        )
        embed.set_footer(text="Verifique o erro e corrija!", icon_url="https://i.imgur.com/CoCnKIT.jpeg")
        await canal_erro.send(embed=embed)
    
    print(f"❌ Erro no evento {event}:\n{erro}")  # Mantém o print para debug no terminal


@bot.event
async def on_disconnect():
    print("⚠️   O bot foi desconectado! Tentando reconectar...")
    bot.loop.create_task(change_activity())  # Reinicia a troca de atividades após reconexão

# Inicia o bot com o token carregado
bot.run(TOKEN)
