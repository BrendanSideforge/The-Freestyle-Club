import datetime

import discord
from discord.ext.commands import Cog, command, has_guild_permissions, Context
import psutil

from utils.converters import get_member_info

class Stats(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()

    @command(
        name='info',
        aliases=['stats'],
        usage="<user:snowflake>",
        brief="View the stats and battle history of a user."
    )
    async def info(self, ctx: Context, user: discord.Member = None):
        """View the stats and battle history of a user."""

        server = ctx.guild
        user = user or ctx.author

        all_stats = await ctx.fetch("""
        SELECT * FROM matches
        WHERE (guild_id=$1 AND defender_id=$2)
        OR (guild_id=$1 AND challenger_id=$2)
        ORDER BY bout_id DESC;
        """, server.id, user.id)
        linked_accounts = await ctx.fetch("""
        SELECT * FROM linked_accounts
        WHERE (guild_id=$1 AND linked_account=$2)
        OR (guild_id=$1 AND main_account=$2)
        """, server.id, user.id)

        total_wins = 0
        wins_by_ko = 0
        total_losses = 0
        losses_by_ko = 0
        total_bouts = 0
        total_rounds = 0
        total_kos = 0
        for stat in all_stats:
            if stat['winner_id'] == user.id:
                total_wins += 1
                wins_by_ko += 1 if stat['decision'] == "KO" else 0
            if stat['loser_id'] == user.id:
                total_losses += 1
                losses_by_ko += 1 if stat['decision'] == "KO" else 0
            
            if stat['match_type'] == "regular":
                total_rounds += 3 if stat['decision'] != "KO" else 2
            if stat['match_type'] == "title":
                total_rounds += 3 if stat['decision'] != "KO" else 2
            if stat['match_type'] == 'champion':
                total_rounds += 5 if stat['decision'] != "KO" else 4
            
            total_bouts += 1
            
            if stat['decision'] == "KO":
                total_kos += 1

        content_wins = 0
        total_content = 0
        flow_wins = 0
        total_flow = 0
        delivery_wins = 0
        total_delivery = 0
        for stat in all_stats:

            if stat['defender_id'] == user.id:
                # await ctx.send(f"Wins(defender): {stat['defender_category_wins']}")
                # await ctx.send(f"Losses(defender): {stat['defender_category_losses']}")
                content_wins += len([s for s in stat['defender_category_wins'] if 'content' in s])
                total_content += len([s for s in stat['defender_category_wins'] if 'content' in s])+len([s for s in stat['defender_category_losses'] if 'content' in s])
                flow_wins += len([s for s in stat['defender_category_wins'] if 'flow' in s])
                total_flow += len([s for s in stat['defender_category_wins'] if 'flow' in s])+len([s for s in stat['defender_category_losses'] if 'flow' in s])
                delivery_wins += len([s for s in stat['defender_category_wins'] if 'delivery' in s])
                total_delivery += len([s for s in stat['defender_category_wins'] if 'delivery' in s])+len([s for s in stat['defender_category_losses'] if 'delivery' in s])

            if stat['challenger_id'] == user.id:
                # await ctx.send(f"Wins(challenger): {stat['challenger_category_wins']}")
                # await ctx.send(f"Losses(challenger): {stat['challenger_category_losses']}")
                content_wins += len([s for s in stat['challenger_category_wins'] if 'content' in s])
                total_content += len([s for s in stat['challenger_category_wins'] if 'content' in s])+len([s for s in stat['challenger_category_losses'] if 'content' in s])
                flow_wins += len([s for s in stat['challenger_category_wins'] if 'flow' in s])
                total_flow += len([s for s in stat['challenger_category_wins'] if 'flow' in s])+len([s for s in stat['challenger_category_losses'] if 'flow' in s])
                delivery_wins += len([s for s in stat['challenger_category_wins'] if 'delivery' in s])
                total_delivery += len([s for s in stat['challenger_category_wins'] if 'delivery' in s])+len([s for s in stat['challenger_category_losses'] if 'delivery' in s])

        for account in linked_accounts:
            stats = await ctx.fetch("""
            SELECT * FROM matches
            WHERE (guild_id=$1 AND defender_id=$2)
            OR (guild_id=$1 AND challenger_id=$1)
            ORDER BY bout_id DESC;
            """, server.id, account['linked_account'] if user.id == account['main_account'] else account['main_account'])

            linked = account['linked_account'] if user.id == account['main_account'] else account['main_account']

            for stat in stats:
                if stat['winner_id'] == linked:
                    total_wins += 1
                    wins_by_ko += 1 if stat['decision'] == "KO" else 0
                if stat['loser_id'] == linked:
                    total_losses += 1
                    losses_by_ko += 1 if stat['decision'] == "KO" else 0
                
                if stat['match_type'] == "regular":
                    total_rounds += 3 if stat['decision'] != "KO" else 2
                if stat['match_type'] == "title":
                    total_rounds += 3 if stat['decision'] != "KO" else 2
                if stat['match_type'] == 'champion':
                    total_rounds += 5 if stat['decision'] != "KO" else 4
                
                if stat['decision'] == "KO":
                    total_kos += 1

                total_bouts += 1

                if stat['defender_id'] == linked:
                    # await ctx.send(f"Wins(defender): {stat['defender_category_wins']}")
                    # await ctx.send(f"Losses(defender): {stat['defender_category_losses']}")
                    content_wins += len([s for s in stat['defender_category_wins'] if 'content' in s])
                    total_content += len([s for s in stat['defender_category_wins'] if 'content' in s])+len([s for s in stat['defender_category_losses'] if 'content' in s])
                    flow_wins += len([s for s in stat['defender_category_wins'] if 'flow' in s])
                    total_flow += len([s for s in stat['defender_category_wins'] if 'flow' in s])+len([s for s in stat['defender_category_losses'] if 'flow' in s])
                    delivery_wins += len([s for s in stat['defender_category_wins'] if 'delivery' in s])
                    total_delivery += len([s for s in stat['defender_category_wins'] if 'delivery' in s])+len([s for s in stat['defender_category_losses'] if 'delivery' in s])

                if stat['challenger_id'] == linked:
                    # await ctx.send(f"Wins(challenger): {stat['challenger_category_wins']}")
                    # await ctx.send(f"Losses(challenger): {stat['challenger_category_losses']}")
                    content_wins += len([s for s in stat['challenger_category_wins'] if 'content' in s])
                    total_content += len([s for s in stat['challenger_category_wins'] if 'content' in s])+len([s for s in stat['challenger_category_losses'] if 'content' in s])
                    flow_wins += len([s for s in stat['challenger_category_wins'] if 'flow' in s])
                    total_flow += len([s for s in stat['challenger_category_wins'] if 'flow' in s])+len([s for s in stat['challenger_category_losses'] if 'flow' in s])
                    delivery_wins += len([s for s in stat['challenger_category_wins'] if 'delivery' in s])
                    total_delivery += len([s for s in stat['challenger_category_wins'] if 'delivery' in s])+len([s for s in stat['challenger_category_losses'] if 'delivery' in s])


        if total_content > 0 and content_wins > 0:
            content_wins_per = f"{content_wins/total_content*100:.2f}%"
        else:
            content_wins_per = "0.00%"
        if total_flow > 0 and flow_wins > 0:
            flow_wins_per = f"{flow_wins/total_flow*100:.2f}%"
        else:
            flow_wins_per = "0.00%"
        if total_delivery > 0 and delivery_wins > 0:
            delivery_wins_per = f"{delivery_wins/total_delivery*100:.2f}%"
        else:
            delivery_wins_per = "0.00%"

        if total_kos > 0 and wins_by_ko > 0:
            wins_ko_per = f"{wins_by_ko/total_wins*100:.2f}%"
        else:
            wins_ko_per = "0.00%"

        embed = discord.Embed()
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_author(name=f"{user} Statistics", icon_url=user.avatar_url)
        embed.add_field(name=f"Total Wins", value=f"{total_wins} ({wins_by_ko} by KO)", inline=False)
        embed.add_field(name=f"Total Losses", value=f"{total_losses} ({losses_by_ko} by KO)", inline=False)
        embed.add_field(name=f"Win %", value=f"{total_wins/total_bouts*100:.2f}%", inline=False)
        embed.add_field(name=f"Total Bouts", value=total_bouts, inline=False)
        embed.add_field(name=f"Total Rounds", value=total_rounds, inline=False)
        embed.add_field(name=f"KO %", value=f"{wins_ko_per}", inline=False)
        embed.add_field(name=f"Category Win %", value="\n".join([
            f"Content: {content_wins_per}",
            f"Flow: {flow_wins_per}",
            f"Delivery: {delivery_wins_per}"
        ]))
        stat_message = await ctx.send(embed=embed)

    @command(
        name="history",
        aliases=[],
        usage="<user:snowflake>",
        brief="View the battle history for a certain user."
    )
    async def history(self, ctx: Context, user: discord.Member = None):
        """View the battle history for a certain user."""

        server = ctx.guild
        user = user or ctx.author

        all_stats = await ctx.fetch("""
        SELECT * FROM matches
        WHERE (guild_id=$1 AND defender_id=$2)
        OR (guild_id=$1 AND challenger_id=$2)
        ORDER BY inserted_at DESC;
        """, server.id, user.id)

        pages = ceil(len(all_stats)/6)
        embed = await self.show_history(server, user, all_stats[:6])
        embed.set_footer(text=f"Page (1/{pages})")
        message = await ctx.send(embed=embed)

        if len(all_stats) > 6:
            await message.add_reaction("◀")
            await message.add_reaction("❌")
            await message.add_reaction("▶")

        def reactioncheck(reaction, user):
            if user == ctx.author:
                if reaction.message.id == message.id:
                    if reaction.emoji == "▶" or reaction.emoji == "❌" or reaction.emoji == "◀" or reaction.emoji == "🇮":
                        return True

        x = 0
        while True:
            reaction, reaction_user = await self.bot.wait_for("reaction_add", check=reactioncheck)
            if reaction.emoji == "◀":
                x -= 6
                if x < 0:
                    x = 0
                await message.remove_reaction("◀", reaction_user)
            elif reaction.emoji == "❌":
                await message.delete()
            elif reaction.emoji == "▶":
                x += 6
                if x > len(all_stats):
                    x = len(all_stats) - 6
                await message.remove_reaction("▶", reaction_user)
            embed = await self.show_history(server, user, all_stats[x:x+6])
            embed.set_footer(text=f'Page ({x//6+1}/{pages})')
            await message.edit(embed=embed)
            await message.remove_reaction("▶", reaction_user)
            
    async def show_history(self, server, user, all_stats):

        embed = discord.Embed()
        embed.set_author(name=f"Battle History for {user}", icon_url=user.avatar_url)

        for stat in all_stats:
            
            if stat['winner_id'] == user.id:
                winner_status = "<:win:778819462119292928> "
            if stat['loser_id'] == user.id:
                winner_status = "<:loss:778819439951872041> "

            opponent = await self.bot.fetch_user(stat['defender_id']) if stat['challenger_id'] == user.id else await self.bot.fetch_user(stat['challenger_id'])

            opponent_last_6 = await self.bot.db.fetch("""
            SELECT * FROM matches
            WHERE (guild_id=$1 AND challenger_id=$2)
            OR (guild_id=$1 AND defender_id=$2)
            ORDER BY inserted_at DESC;
            """, server.id, opponent.id)
            wins = 0
            losses = 0
            last_6 = ""
            matches_before_this = [match for match in opponent_last_6 if round(match['inserted_at'].timestamp() < stat['inserted_at'].timestamp())]
            for match in matches_before_this[:5]:
                if match['winner_id'] == opponent.id:
                    last_6 += f"W "
                    wins += 1
                if match['loser_id'] == opponent.id:
                    last_6 += f"L "
                    losses += 1

            winner = await self.bot.fetch_user(stat['winner_id'])
            winner_fm = winner.mention if winner else 'Not found'
            print(stat['ratio'][1])
            print(stat['decision'])

            date = stat['inserted_at'].strftime("%m-%d-%Y")
            embed.add_field(name=f"{date} {winner_status}", value="\n".join([
                f"{stat['match_type'].capitalize()} Match",
                f"Opponent: {opponent.mention} [{wins}-{losses}] Last 6: {last_6}",
                f"Winner: {winner_fm} {stat['ratio'][0]}-{stat['ratio'][1]} by **{stat['decision']}**",
                f'"{stat["winner_quote"].replace("match ", " ")}"'
            ]), inline=False)
        
        return embed

    @command(
        name="link",
        brief="Link another account to show their stats on their main account."
    )
    @has_guild_permissions(manage_guild=True)
    async def link_account(self, ctx: Context, user: discord.Member = None):
        """Link another account to show their stats on their main account."""

        server = ctx.guild

        embed = discord.Embed()
        embed.add_field(name='Who is the main account?', value="\n".join([
            f"To link this account you need to mention their main account."
        ]), inline=False)
        await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        link_acc = await self.bot.wait_for('message', check=check)
        linked_member = await get_member_info(ctx, link_acc.content)

        if link_acc.content.lower() == "cancel":
            return await ctx.send(f":ok_hand: Canceled this account linking.")
        
        if not linked_member:
            ok = False
            canceled = False
            while ok is False and canceled is False:
                embed = discord.Embed()
                embed.add_field(name='Who is the linked account?', value="\n".join([
                    f"To link a user to this account you need to mention the linked user."
                ]), inline=False)
                await ctx.send(embed=embed)

                link_acc = await self.bot.wait_for('message', check=check)
                linked_member = await get_member_info(ctx, link_acc.content)

                if link_acc.content.lower() == "cancel":
                    await ctx.send(f":ok_hand: Canceled this account linking.")
                    canceled = True
                
                if not linked_member:
                    continue
                else:
                    ok = True
    
        await ctx.execute("""
        INSERT INTO linked_accounts (
            guild_id,
            linked_account,
            main_account
        ) VALUES (
            $1, $2, $3
        )
        """, server.id, linked_member.id, user.id)

        embed = discord.Embed()
        embed.add_field(name=":ok_hand: Done", value=f"Successfully added {user.mention} as a linked account to {linked_member.mention}.")
        await ctx.send(embed=embed)

    # @command(
    #     name="about",
    #     aliases=['botinfo', 'bot-info'],
    #     brief="View information about the TFC Bot."
    # )
    # async def about(self, ctx: Context):
    #     """View the information about the TFC Bot."""

    #     embed = discord.Embed(color=discord.Color.blurlpe())
    #     embed

def setup(bot):
    bot.add_cog(Stats(bot))