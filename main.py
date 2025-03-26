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
from discord.ui import Button, View

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

##--- EVENTO DE MENÇÃO AO BOT ---##

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
            "• `/info`: Informações sobre o Ayla Bot.\n"
            "• `/live`: informações sobre o canal da Viih.\n"
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

        ##                                ##
        ##--- COMANDOS DA LIVE DA VIIH ---##
        ##                                ##

##--- COMANDO /LIVE ---##
@bot.tree.command(name="live", description="lives da Viih")
async def info(interaction: discord.Interaction):
    live_embed = discord.Embed(
        title="🍄 **LIVES DA VIIH** 🍄",
        description="Olá meu nome é Viih, sou nova na plataforma e quero muito ser uma streamer conhecida. Espero que gostem das minhas lives e se divirtam. 🩷🌈",
        color=discord.Color.pink()
    )
    live_embed.set_thumbnail(url="https://i.imgur.com/zK2DR2F.jpeg")

    # Criando botões
    twitch_button = Button(label="Acessar Twitch", url="https://www.twitch.tv/nnico_robiin", style=discord.ButtonStyle.link)
    tiktok_button = Button(label="Acessar TikTok", url="https://www.tiktok.com/@jardim_da_viih", style=discord.ButtonStyle.link)

    # Criando a view e adicionando os botões
    view = View()
    view.add_item(twitch_button)
    view.add_item(tiktok_button)

    await interaction.response.send_message(embed=live_embed, view=view)

##--- COMANDO /DIVULGAR LIVE ---##
@bot.tree.command(name="divulgar_live", description="Divulga a live da Viih no canal de divulgação")
async def divulgar_live(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Você precisa ser administrador para usar este comando.", ephemeral=True)
        return

    canal_divulgacao = bot.get_channel(00000)  # ID do canal de divulgação
    cargo_mencao = interaction.guild.get_role(00000)  # ID do cargo a ser mencionado

    if not canal_divulgacao or not cargo_mencao:
        await interaction.response.send_message("❌ O canal ou cargo não foi encontrado.", ephemeral=True)
        return

    live_embed = discord.Embed(
        title="🔴 LIVE AO VIVO!",
        description="A Viih está ao vivo! Venha assistir e se divertir! 🌸🎮",
        color=discord.Color.red(),
        url="https://www.twitch.tv/nnico_robiin"
    )
    live_embed.set_thumbnail(url="https://i.imgur.com/3q6IuqP.png")
    live_embed.add_field(name="🎥 Link da Live:", value="[Clique aqui para assistir!](https://www.twitch.tv/nnico_robiin)", inline=False)
    live_embed.set_footer(text="Apoie a Viih! 💖", icon_url="https://i.imgur.com/zK2DR2F.jpeg")

    await canal_divulgacao.send(f"{cargo_mencao.mention} A Viih está AO VIVO! 🔴", embed=live_embed)
    await interaction.response.send_message("✅ Live divulgada com sucesso!", ephemeral=True)


##--- PROCESSAMENTO DE ERROS ---##
@bot.event
async def on_error(event, *args, **kwargs):
    erro = traceback.format_exc()
    
    # Canal de logs de erro
    canal_erro = bot.get_channel(00000)
    
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
