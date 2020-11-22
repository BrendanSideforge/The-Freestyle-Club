
class Config:

    token = ""
    cogs = [
        'jishaku',
        'cogs.developer',
        'cogs.matches',
        'cogs.stats'
    ]

class Postgres:

    user = 'postgres'
    port = 5432
    host = 'localhost'
    password = 'BS103261'
    database = 'freestyleclub'

class Redis:

    host = 'localhost'
    port = 6379 

class Database:
    def __init__(self, db):
        self.db = db

    async def create_tables(self):
        
        try:
            await self.db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                guild_id bigint,
                bout_id integer,
                defender_id bigint,
                challenger_id bigint,
                judges bigint[],
                host_id bigint,
                winner_id bigint,
                loser_id bigint,
                ratio integer[],
                decision text,
                defender_category_wins text[],
                defender_category_losses text[],
                challenger_category_wins text[],
                challenger_category_losses text[],
                match_type text,
                inserted_at timestamp,
                winner_quote text
            )
            """)

            await self.db.execute("""
            CREATE TABLE IF NOT EXISTS title_matches (
                guild_id bigint,
                bout_id integer,
                defender_id bigint,
                challenger_id bigint,
                judges bigint[],
                host_id bigint,
                winner_id bigint,
                loser_id bigint,
                ratio integer[],
                decision text,
                defender_category_wins text[],
                defender_category_losses text[],
                challenger_category_wins text[],
                challenger_category_losses text[],
                match_type text,
                inserted_at timestamp,
                winner_quote text
            )
            """)

            await self.db.execute("""
            CREATE TABLE IF NOT EXISTS linked_accounts (
                guild_id bigint,
                linked_account bigint,
                main_account bigint
            )
            """)
        except Exception as e:
            print(f"[POSTGRES ERROR] {e}")