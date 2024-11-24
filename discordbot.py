import discord
from discord.ext import commands
import json
import os
from keep_alive import run

# Botの設定
bot = commands.Bot(command_prefix='!')
# Intentsの設定
intents = discord.Intents.default()
intents.message_content = True

# Botの初期化
bot = commands.Bot(command_prefix="!", intents=intents)

# データファイル名
DATA_FILE = "coins.json"

# コインデータをロードする関数
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}  # ファイルがない場合は空の辞書を返す

# コインデータを保存する関数
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 初期データのロード
coins = load_data()

# コイン残高を確認するコマンド
@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    user_coins = coins.get(user_id, 0)
    await ctx.send(f"{ctx.author.mention} さんの所持コインは {user_coins} コインです！")

# 管理者がコインを追加するコマンド
@bot.command()
@commands.has_permissions(administrator=True)
async def add_coins(ctx, member: discord.Member, amount: int):
    user_id = str(member.id)
    if user_id not in coins:
        coins[user_id] = 0
    coins[user_id] += amount
    save_data(coins)  # データを保存
    await ctx.send(f"{member.mention} さんに {amount} コインを付与しました！ 現在の所持コイン: {coins[user_id]}")

# 管理者がコインを減らすコマンド
@bot.command()
@commands.has_permissions(administrator=True)
async def remove_coins(ctx, member: discord.Member, amount: int):
    user_id = str(member.id)
    if user_id in coins and coins[user_id] >= amount:
        coins[user_id] -= amount
        save_data(coins)  # データを保存
        await ctx.send(f"{member.mention} さんから {amount} コインを減らしました。現在の所持コイン: {coins[user_id]}")
    else:
        await ctx.send(f"{member.mention} さんは十分なコインを持っていません。")

# ショップ機能
@bot.command()
async def shop(ctx, role_name: str):
    # ロールとその価格の設定
    shop_items = {
        "プレミアロール": 3000,
        "神ロール": 1000,
        "とろろロール": 500
    }

    # 入力されたロールが存在するか確認
    if role_name not in shop_items:
        await ctx.send(f"{ctx.author.mention} 無効なロール名です。以下のロールを購入できます:\n" +
                       "\n".join([f"{r} - {p} コイン" for r, p in shop_items.items()]))
        return

    # ロールの価格を取得
    price = shop_items[role_name]

    # ユーザーのコイン残高を確認
    user_id = str(ctx.author.id)
    user_coins = coins.get(user_id, 0)
    if user_coins < price:
        await ctx.send(f"{ctx.author.mention} コインが足りません！必要コイン: {price}, あなたのコイン: {user_coins}")
        return

    # サーバーからロールを取得
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"{ctx.author.mention} {role_name} ロールが見つかりません。管理者にお問い合わせください。")
        return

    # ロールを付与
    await ctx.author.add_roles(role)

    # コインを減らして保存
    coins[user_id] -= price
    save_data(coins)

    await ctx.send(f"{ctx.author.mention} {role_name} ロールを購入しました！ 残りのコイン: {coins[user_id]}")

# 管理者が全ユーザーのコインを一覧表示するコマンド
@bot.command()
@commands.has_permissions(administrator=True)
async def list_coins(ctx):
    if coins:
        message = "📜 全ユーザーのコイン一覧:\n"
        for user_id, amount in coins.items():
            user = await bot.fetch_user(user_id)
            message += f"{user.name}: {amount} コイン\n"
        await ctx.send(message)
    else:
        await ctx.send("現在、コインデータは空です。")
# Botを起動する前にkeep-aliveサーバーを起動
run()

# Botの起動メッセージ
@bot.event
async def on_ready():
    print(f"Botがログインしました: {bot.user}")

# Botを起動
bot.run("MTMxMDA0MzIxMDk5ODg3NDE5Mg.G2RUU0.SRlmhVff39pf3Oks3TxcX--olUvYiCh4YakrBI", bot=True, reconnect=True)
