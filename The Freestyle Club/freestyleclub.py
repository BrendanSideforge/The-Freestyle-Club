import datetime

import discord
from discord import activity
from discord.ext.commands import Bot, when_mentioned_or
import aioredis
import asyncpg
from discord.ext.commands.bot import AutoShardedBot

from constants import *
from utils.context import Context

class FreestyleClub(AutoShardedBot):


    intents = discord.Intents.default()
    intents.members = True

    def __init__(self):
        super().__init__(
            command_prefix=when_mentioned_or("tfc "),
            case_insensitive=True,
            intents=self.intents
        )

        self.db = None
        self.redis = None

    async def on_ready(self) -> None:

        self.uptime = datetime.datetime.utcnow()

        print(f"[READY] {self.user} has logged into Discord with the ID of {self.user.id}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Battles'))

    async def connect_postgres(self) -> None:

        self.db = await asyncpg.create_pool(
            host=Postgres.host,
            port=Postgres.port,
            database=Postgres.database,
            user=Postgres.user,
            password=Postgres.password
        )
        await Database(self.db).create_tables()
        print(f"[DATABSE] PostgreSQL has connected.")

    async def connect_redis(self) -> None:

        self.redis = await aioredis.create_redis_pool(
            address=(Redis.host, Redis.port)
        )
        print(f"[DATABASE] Redis has connected.")

    def load_cogs(self) -> None:

        for cog in Config.cogs:
            try:
                self.load_extension(cog)
                print(f"[COG LOADED] Loaded the cog: {cog}")
            except Exception as e:
                print(f"[COG FAILED] {cog} failed to load: {e}")

    async def login(self, *args, **kwargs) -> None:

        self.load_cogs()
        await self.connect_redis()
        await self.connect_postgres()

        await super().login(*args, **kwargs)

    async def get_context(self, message, cls=None):
        if not message.guild or message.author.bot:
            return None
        return await super().get_context(message, cls=cls)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        if not ctx or ctx.command is None:
            return

        await self.invoke(ctx)

bot = FreestyleClub()

bot.run(Config.token)
