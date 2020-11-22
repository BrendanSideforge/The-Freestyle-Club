import datetime
import asyncio
from math import ceil
from collections import Counter
import random
import traceback

import discord
from discord.ext.commands import Cog, command, Context, has_guild_permissions

from utils.converters import get_member_info, get_member

class Matches(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @command(
        name="startmatch",
        aliases=['sm', 'start-match', 's-m'],
        brief="Leads you through a process of setting up a match through questions."
    )
    @has_guild_permissions(manage_guild=True)
    async def startmatch(
        self,
        ctx: Context
    ):
        """Leads you through a process of setting up a match through questions."""

        server = ctx.guild

        def reaction_check(reaction, user):
            if user == ctx.author:
                if reaction.message.author == self.bot.user:
                    if (
                        reaction.emoji == "1️⃣" 
                        or reaction.emoji == "2️⃣"
                        or reaction.emoji == "3️⃣"
                        or reaction.emoji == "4️⃣"
                        or reaction.emoji == "5️⃣"
                        or reaction.emoji == "6️⃣"
                        or reaction.emoji == "✅"
                        or reaction.emoji == "❌"
                    ):
                        return True
        
        def msg_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        starting_embed = discord.Embed()
        starting_embed.add_field(name="What type of match are you setting up?", value="\n".join([
            f":one: Champion",
            f":two: Title",
            f":three: Regular",
            f":x: Endmatch"
        ]))
        starting_message = await ctx.send(embed=starting_embed)

        await starting_message.add_reaction("1️⃣")
        await starting_message.add_reaction("2️⃣")
        await starting_message.add_reaction("3️⃣")
        await starting_message.add_reaction("❌")
            
        starting_reaction, starting_user = await self.bot.wait_for('reaction_add', check=reaction_check)
        if starting_reaction.emoji == "3️⃣":
            
            # Asking who the defender is
            defender_embed = discord.Embed()
            defender_embed.add_field(name=f"Who is the defender?", value="\n".join([
                f"Acceptable inputs are: member ID, mention, or username"
            ]))
            defender_message = await ctx.send(embed=defender_embed)

            defender_response = await self.bot.wait_for('message', check=msg_check)
            if defender_response.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")
            defender = await get_member_info(ctx, defender_response.content)

            if not defender:
                found = False
                while found is False:

                    defender_embed = discord.Embed()
                    defender_embed.add_field(name=f"Who is the defender?", value="\n".join([
                        f"Acceptable inputs are: member ID, mention, or username"
                    ]))
                    defender_message = await ctx.send(embed=defender_embed)

                    defender_response = await self.bot.wait_for('message', check=msg_check)
                    if defender_response.content.lower() == "cancel":
                        return await ctx.send(f":ok_hand: Cancelled start match.")
                    defender = await get_member_info(ctx, defender_response.content)

                    if not defender:
                        continue
                    
                    found = True

            challenger_embed = discord.Embed()
            challenger_embed.add_field(name="Who is the challenger?", value="\n".join([ 
                f"Acceptable inputs are: member ID, mention, or username"
            ]))
            challenger_message = await ctx.send(embed=challenger_embed)

            challenger_response = await self.bot.wait_for('message', check=msg_check)
            if challenger_response.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")
            challenger = await get_member_info(ctx, challenger_response.content)

            if not challenger:
                found = False
                while found is False:

                    challenger_embed = discord.Embed()
                    challenger_embed.add_field(name="Who is the challenger?", value="\n".join([
                        f"Acceptable inputs are: member ID, mention, or username"
                    ]))
                    challenger_message = await ctx.send(embed=challenger_embed)

                    challenger_response = await self.bot.wait_for('message', check=msg_check)
                    if challenger_response.content.lower() == "cancel":
                        return await ctx.send(f":ok_hand: Cancelled start match.")
                    challenger = await get_member_info(ctx, challenger_response.content)

                    if not challenger:
                        continue

                    found = True

            # ========================================================
            # ROUND 1 INFORMATION
            # ========================================================
            # ROUND 1 CONTENT
            # ========================================================

            defender_previous_wins = await ctx.fetch("""
            SELECT * FROM matches
            WHERE guild_id=$1 AND winner_id=$2
            """, server.id, defender.id)
            defender_previous_losses = await ctx.fetch("""
            SELECT * FROM matches
            WHERE guild_id=$1 AND loser_id=$2
            """, server.id, defender.id)
            defender_most_previous = f"[{len(defender_previous_wins)}-{len(defender_previous_losses)}]"

            challenger_previous_wins = await ctx.fetch("""
            SELECT * FROM matches
            WHERE guild_id=$1 AND winner_id=$2
            """, server.id, challenger.id)
            challenger_previous_losses = await ctx.fetch("""
            SELECT * FROM matches
            WHERE guild_id=$1 AND loser_id=$2
            """, server.id, challenger.id)
            challenger_most_previous = f"[{len(challenger_previous_wins)}-{len(challenger_previous_losses)}]"

            defender_points = []
            challenger_points = []

            round_1_content_embed = discord.Embed()
            round_1_content_embed.add_field(name="Who won round one content?", value=f"\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_1_content_message = await ctx.send(embed=round_1_content_embed)

            await round_1_content_message.add_reaction("1️⃣")
            await round_1_content_message.add_reaction("2️⃣")
            await round_1_content_message.add_reaction("❌")

            round_1_content_reaction, round_1_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_1_content_reaction.emoji == "1️⃣":
                round_1_content_winner = defender
                defender_points.append('round 1 content')
            elif round_1_content_reaction.emoji == "2️⃣":
                round_1_content_winner = challenger
                challenger_points.append('round 1 content')
            elif round_1_content_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # ROUND 1 FLOW
            # ========================================================

            round_1_flow_embed = discord.Embed()
            round_1_flow_embed.add_field(name="Who won round one flow?", value="\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_1_flow_message = await ctx.send(embed=round_1_flow_embed)

            await round_1_flow_message.add_reaction("1️⃣")
            await round_1_flow_message.add_reaction("2️⃣")
            await round_1_flow_message.add_reaction("❌")

            round_1_flow_reaction, round_1_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_1_flow_reaction.emoji == "1️⃣":
                round_1_flow_winner = defender
                defender_points.append('round 1 flow')
            elif round_1_flow_reaction.emoji == "2️⃣":
                round_1_flow_winner = challenger
                challenger_points.append('round 1 flow')
            elif round_1_flow_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # ROUND 1 DELIVERY
            # ========================================================

            round_1_delivery_embed = discord.Embed()
            round_1_delivery_embed.add_field(name="Who won round one delivery?", value="\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_1_delivery_message = await ctx.send(embed=round_1_delivery_embed)

            await round_1_delivery_message.add_reaction("1️⃣")
            await round_1_delivery_message.add_reaction("2️⃣")
            await round_1_delivery_message.add_reaction("❌")

            round_1_delivery_reaction, round_1_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_1_delivery_reaction.emoji == "1️⃣":
                round_1_delivery_winner = defender
                defender_points.append('round 1 delivery')
            elif round_1_delivery_reaction.emoji == "2️⃣":
                round_1_delivery_winner = challenger
                challenger_points.append('round 1 delivery')
            elif round_1_delivery_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # SAFETY CHECK
            # ========================================================

            round_1_check = discord.Embed()
            round_1_check.add_field(name="Round 1 Results", value="\n".join([
                f":brain: Content - {round_1_content_winner.mention}",
                f":ocean: Flow - {round_1_flow_winner.mention}",
                f":speaking_head: Delivery - {round_1_delivery_winner.mention}",
            ]))
            round_1_check_message = await ctx.send(embed=round_1_check)

            await round_1_check_message.add_reaction("✅")
            await round_1_check_message.add_reaction("❌")

            round_1_check_reaction, round_1_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_1_check_reaction.emoji == "❌":
                ok = False

                for win in defender_points:
                    if 'round 1' in win:
                        defender_points.remove(win)
                
                for win in challenger_points:
                    if 'round 1' in win:
                        challenger_points.remove(win)

                while ok is False:
                    # ========================================================
                    # ROUND 1 INFORMATION
                    # ========================================================
                    # ROUND 1 CONTENT
                    # ========================================================

                    round_1_content_embed = discord.Embed()
                    round_1_content_embed.add_field(name="Who won round one content?", value=f"\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_1_content_message = await ctx.send(embed=round_1_content_embed)

                    await round_1_content_message.add_reaction("1️⃣")
                    await round_1_content_message.add_reaction("2️⃣")
                    await round_1_content_message.add_reaction("❌")

                    round_1_content_reaction, round_1_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_1_content_reaction.emoji == "1️⃣":
                        round_1_content_winner = defender
                        defender_points.append('round 1 content')
                    elif round_1_content_reaction.emoji == "2️⃣":
                        round_1_content_winner = challenger
                        challenger_points.append('round 1 content')
                    elif round_1_content_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    # ========================================================
                    # ROUND 1 FLOW
                    # ========================================================

                    round_1_flow_embed = discord.Embed()
                    round_1_flow_embed.add_field(name="Who won round one flow?", value="\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_1_flow_message = await ctx.send(embed=round_1_flow_embed)

                    await round_1_flow_message.add_reaction("1️⃣")
                    await round_1_flow_message.add_reaction("2️⃣")
                    await round_1_flow_message.add_reaction("❌")

                    round_1_flow_reaction, round_1_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_1_flow_reaction.emoji == "1️⃣":
                        round_1_flow_winner = defender
                        defender_points.append('round 1 flow')
                    elif round_1_flow_reaction.emoji == "2️⃣":
                        round_1_flow_winner = challenger
                        challenger_points.append('round 1 flow')
                    elif round_1_flow_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    # ========================================================
                    # ROUND 1 DELIVERY
                    # ========================================================

                    round_1_delivery_embed = discord.Embed()
                    round_1_delivery_embed.add_field(name="Who won round one delivery?", value="\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}"
                    ]))
                    round_1_delivery_message = await ctx.send(embed=round_1_delivery_embed)

                    await round_1_delivery_message.add_reaction("1️⃣")
                    await round_1_delivery_message.add_reaction("2️⃣")
                    await round_1_delivery_message.add_reaction("❌")

                    round_1_delivery_reaction, round_1_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_1_delivery_reaction.emoji == "1️⃣":
                        round_1_delivery_winner = defender
                        defender_points.append('round 1 delivery')
                    elif round_1_delivery_reaction.emoji == "2️⃣":
                        round_1_delivery_winner = challenger
                        challenger_points.append('round 1 delivery')
                    elif round_1_delivery_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    round_1_check = discord.Embed()
                    round_1_check.add_field(name="Round 1 Results", value="\n".join([
                        f":brain: Content - {round_1_content_winner.mention}",
                        f":ocean: Flow - {round_1_flow_winner.mention}",
                        f":speaking_head: Delivery - {round_1_delivery_winner.mention}",
                    ]))
                    round_1_check_message = await ctx.send(embed=round_1_check)

                    await round_1_check_message.add_reaction("✅")
                    await round_1_check_message.add_reaction("❌")

                    round_1_check_reaction, round_1_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_1_check_reaction.emoji == "✅":
                        ok = True
                    else:
                        continue

            # ========================================================
            # ROUND 2 INFORMATION
            # ========================================================
            # ROUND 2 CONTENT
            # ========================================================

            round_2_content_embed = discord.Embed()
            round_2_content_embed.add_field(name="Who won round two content?", value=f"\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_2_content_message = await ctx.send(embed=round_2_content_embed)

            await round_2_content_message.add_reaction("1️⃣")
            await round_2_content_message.add_reaction("2️⃣")
            await round_2_content_message.add_reaction("❌")

            round_2_content_reaction, round_2_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_2_content_reaction.emoji == "1️⃣":
                round_2_content_winner = defender
                defender_points.append('round 2 content')
            elif round_2_content_reaction.emoji == "2️⃣":
                round_2_content_winner = challenger
                challenger_points.append('round 2 content')
            elif round_2_content_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # ROUND 2 FLOW
            # ========================================================

            round_2_flow_embed = discord.Embed()
            round_2_flow_embed.add_field(name="Who won round two flow?", value="\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_2_flow_message = await ctx.send(embed=round_2_flow_embed)

            await round_2_flow_message.add_reaction("1️⃣")
            await round_2_flow_message.add_reaction("2️⃣")
            await round_2_flow_message.add_reaction("❌")

            round_2_flow_reaction, round_2_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_2_flow_reaction.emoji == "1️⃣":
                round_2_flow_winner = defender
                defender_points.append('round 2 flow')
            elif round_2_flow_reaction.emoji == "2️⃣":
                round_2_flow_winner = challenger
                challenger_points.append('round 2 flow')
            elif round_2_flow_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # ROUND 2 DELIVERY
            # ========================================================

            round_2_delivery_embed = discord.Embed()
            round_2_delivery_embed.add_field(name="Who won round two delivery?", value="\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_2_delivery_message = await ctx.send(embed=round_2_delivery_embed)

            await round_2_delivery_message.add_reaction("1️⃣")
            await round_2_delivery_message.add_reaction("2️⃣")
            await round_2_delivery_message.add_reaction("❌")

            round_2_delivery_reaction, round_2_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_2_delivery_reaction.emoji == "1️⃣":
                round_2_delivery_winner = defender
                defender_points.append('round 2 delivery')
            elif round_2_delivery_reaction.emoji == "2️⃣":
                round_2_delivery_winner = challenger
                challenger_points.append('round 2 delivery')
            elif round_2_delivery_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # SAFETY CHECK
            # ========================================================

            round_2_check = discord.Embed()
            round_2_check.add_field(name="Round 2 Results", value="\n".join([
                f":brain: Content - {round_2_content_winner.mention}",
                f":ocean: Flow - {round_2_flow_winner.mention}",
                f":speaking_head: Delivery - {round_2_delivery_winner.mention}",
            ]))
            round_2_check_message = await ctx.send(embed=round_2_check)

            await round_2_check_message.add_reaction("✅")
            await round_2_check_message.add_reaction("❌")

            round_2_check_reaction, round_2_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_2_check_reaction.emoji == "❌":
                ok = False

                for win in defender_points:
                    if 'round 2' in win:
                        defender_points.remove(win)
                
                for win in challenger_points:
                    if 'round 2' in win:
                        challenger_points.remove(win)

                while ok is False:
                    # ========================================================
                    # ROUND 2 INFORMATION
                    # ========================================================
                    # ROUND 2 CONTENT
                    # ========================================================

                    round_2_content_embed = discord.Embed()
                    round_2_content_embed.add_field(name="Who won round two content?", value=f"\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_2_content_message = await ctx.send(embed=round_2_content_embed)

                    await round_2_content_message.add_reaction("1️⃣")
                    await round_2_content_message.add_reaction("2️⃣")
                    await round_2_content_message.add_reaction("❌")

                    round_2_content_reaction, round_2_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_2_content_reaction.emoji == "1️⃣":
                        round_2_content_winner = defender
                        defender_points.append('round 2 content')
                    elif round_2_content_reaction.emoji == "2️⃣":
                        round_2_content_winner = challenger
                        challenger_points.append('round 2 content')
                    elif round_2_content_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    # ========================================================
                    # ROUND 1 FLOW
                    # ========================================================

                    round_2_flow_embed = discord.Embed()
                    round_2_flow_embed.add_field(name="Who won round two flow?", value="\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_2_flow_message = await ctx.send(embed=round_2_flow_embed)

                    await round_2_flow_message.add_reaction("1️⃣")
                    await round_2_flow_message.add_reaction("2️⃣")
                    await round_2_flow_message.add_reaction("❌")

                    round_2_flow_reaction, round_2_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_2_flow_reaction.emoji == "1️⃣":
                        round_2_flow_winner = defender
                        defender_points.append('round 2 flow')
                    elif round_2_flow_reaction.emoji == "2️⃣":
                        round_2_flow_winner = challenger
                        challenger_points.append('round 2 flow')
                    elif round_2_flow_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    # ========================================================
                    # ROUND 2 DELIVERY
                    # ========================================================

                    round_2_delivery_embed = discord.Embed()
                    round_2_delivery_embed.add_field(name="Who won round two delivery?", value="\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_2_delivery_message = await ctx.send(embed=round_2_delivery_embed)

                    await round_2_delivery_message.add_reaction("1️⃣")
                    await round_2_delivery_message.add_reaction("2️⃣")
                    await round_2_delivery_message.add_reaction("❌")

                    round_2_delivery_reaction, round_2_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_2_delivery_reaction.emoji == "1️⃣":
                        round_2_delivery_winner = defender
                        defender_points.append('round 2 delivery')
                    elif round_2_delivery_reaction.emoji == "2️⃣":
                        round_2_delivery_winner = challenger
                        challenger_points.append('round 2 delivery')
                    elif round_2_delivery_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    round_2_check = discord.Embed()
                    round_2_check.add_field(name="Round 2 Results", value="\n".join([
                        f":brain: Content - {round_2_content_winner.mention}",
                        f":ocean: Flow - {round_2_flow_winner.mention}",
                        f":speaking_head: Delivery - {round_2_delivery_winner.mention}",
                    ]))
                    round_2_check_message = await ctx.send(embed=round_2_check)

                    await round_2_check_message.add_reaction("✅")
                    await round_2_check_message.add_reaction("❌")

                    round_2_check_reaction, round_2_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_2_check_reaction.emoji == "✅":
                        ok = True
                    else:
                        continue

            # ========================================================
            # DETERMINE THE CALL FOR THE MATCH
            # ========================================================

            majority_round_one = None
            majority_round_two = None
            majority_round_three = None
            defender_majorities = 0
            challenger_majorities = 0

            defender_round_ones = 0
            defender_round_twos = 0
            defender_round_threes = 0
        
            challenger_round_ones = 0
            challenger_round_twos = 0
            challenger_round_threes = 0

            for point in defender_points:

                if 'round 1' in point:
                    defender_round_ones += 1
                elif 'round 2' in point:
                    defender_round_twos += 1
                elif 'round 3' in point:
                    defender_round_threes += 1
                
            for point in challenger_points:

                if 'round 1' in point:
                    challenger_round_ones += 1
                elif 'round 2' in point:
                    challenger_round_twos += 1
                elif 'round 3' in point:
                    challenger_round_threes += 1
            
            if defender_round_ones > challenger_round_ones:
                majority_round_one = defender
                defender_majorities += 1
            if challenger_round_ones > defender_round_ones:
                majority_round_one = challenger
                challenger_majorities += 1
            
            if defender_round_twos > challenger_round_twos:
                majority_round_two = defender
                defender_majorities += 1
            if challenger_round_twos > defender_round_twos:
                majority_round_two = challenger
                challenger_majorities += 1

            if defender_round_threes > challenger_round_threes:
                majority_round_three = defender
                defender_majorities += 1
            if challenger_round_threes > defender_round_threes:
                majority_round_three = challenger
                challenger_majorities += 1

            calling = "Couldn't make the call."

            if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                calling = "Unanimous Decision"
            if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                calling = "KO"
            if defender_majorities >= 1 and challenger_majorities >= 1:
                calling = "Split Decision"

            round_3_ignored = True

            if calling == "KO":
                pass
            else:
                round_3_ignored = False
                # ========================================================
                # ROUND 3 INFORMATION
                # ========================================================
                # ROUND 3 CONTENT
                # ========================================================

                round_3_content_embed = discord.Embed()
                round_3_content_embed.add_field(name="Who won round three content?", value=f"\n".join([
                    f":one: Defender: {defender.mention}",
                    f":two: Challenger: {challenger.mention}",
                    f":x: Endmatch"
                ]))
                round_3_content_message = await ctx.send(embed=round_3_content_embed)

                await round_3_content_message.add_reaction("1️⃣")
                await round_3_content_message.add_reaction("2️⃣")
                await round_3_content_message.add_reaction("❌")

                round_3_content_reaction, round_3_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                if round_3_content_reaction.emoji == "1️⃣":
                    round_3_content_winner = defender
                    defender_points.append('round 3 content')
                elif round_3_content_reaction.emoji == "2️⃣":
                    round_3_content_winner = challenger
                    challenger_points.append('round 3 content')
                elif round_3_content_reaction.emoji == "❌":
                    return await ctx.send(f":ok_hand: Cancelled start match.")

                # ========================================================
                # ROUND 3 FLOW
                # ========================================================

                round_3_flow_embed = discord.Embed()
                round_3_flow_embed.add_field(name="Who won round three flow?", value="\n".join([
                    f":one: Defender: {defender.mention}",
                    f":two: Challenger: {challenger.mention}",
                    f":x: Endmatch"
                ]))
                round_3_flow_message = await ctx.send(embed=round_2_flow_embed)

                await round_3_flow_message.add_reaction("1️⃣")
                await round_3_flow_message.add_reaction("2️⃣")
                await round_3_flow_message.add_reaction("❌")

                round_3_flow_reaction, round_3_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                if round_3_flow_reaction.emoji == "1️⃣":
                    round_3_flow_winner = defender
                    defender_points.append('round 3 flow')
                elif round_3_flow_reaction.emoji == "2️⃣":
                    round_3_flow_winner = challenger
                    challenger_points.append('round 3 flow')
                elif round_3_flow_reaction.emoji == "❌":
                    return await ctx.send(f":ok_hand: Cancelled start match.")

                # ========================================================
                # ROUND 3 DELIVERY
                # ========================================================

                round_3_delivery_embed = discord.Embed()
                round_3_delivery_embed.add_field(name="Who won round two delivery?", value="\n".join([
                    f":one: Defender: {defender.mention}",
                    f":two: Challenger: {challenger.mention}",
                    f":x: Endmatch"
                ]))
                round_3_delivery_message = await ctx.send(embed=round_3_delivery_embed)

                await round_3_delivery_message.add_reaction("1️⃣")
                await round_3_delivery_message.add_reaction("2️⃣")
                await round_3_delivery_message.add_reaction("❌")

                round_3_delivery_reaction, round_3_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                if round_3_delivery_reaction.emoji == "1️⃣":
                    round_3_delivery_winner = defender
                    defender_points.append('round 3 delivery')
                elif round_3_delivery_reaction.emoji == "2️⃣":
                    round_3_delivery_winner = challenger
                    challenger_points.append('round 3 delivery')
                elif round_3_delivery_reaction.emoji == "❌":
                    return await ctx.send(f":ok_hand: Cancelled start match.")

                # ========================================================
                # SAFETY CHECK
                # ========================================================

                round_3_check = discord.Embed()
                round_3_check.add_field(name="Round 3 Results", value="\n".join([
                    f":brain: Content - {round_3_content_winner.mention}",
                    f":ocean: Flow - {round_3_flow_winner.mention}",
                    f":speaking_head: Delivery - {round_3_delivery_winner.mention}",
                ]))
                round_3_check_message = await ctx.send(embed=round_3_check)

                await round_3_check_message.add_reaction("✅")
                await round_3_check_message.add_reaction("❌")

                round_3_check_reaction, round_3_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                if round_3_check_reaction.emoji == "❌":
                    ok = False
                    

                    for win in defender_points:
                        if 'round 3' in win:
                            defender_points.remove(win)
                    
                    for win in challenger_points:
                        if 'round 3' in win:
                            challenger_points.remove(win)

                    while ok is False:
                        # ========================================================
                        # ROUND 3 INFORMATION
                        # ========================================================
                        # ROUND 3 CONTENT
                        # ========================================================

                        round_3_content_embed = discord.Embed()
                        round_3_content_embed.add_field(name="Who won round three content?", value=f"\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}",
                            f":x: Endmatch"
                        ]))
                        round_3_content_message = await ctx.send(embed=round_3_content_embed)

                        await round_3_content_message.add_reaction("1️⃣")
                        await round_3_content_message.add_reaction("2️⃣")
                        await round_3_content_message.add_reaction("❌")

                        round_3_content_reaction, round_3_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_content_reaction.emoji == "1️⃣":
                            round_3_content_winner = defender
                            defender_points.append('round 3 content')
                        elif round_3_content_reaction.emoji == "2️⃣":
                            round_3_content_winner = challenger
                            challenger_points.append('round 3 content')
                        elif round_3_content_reaction.emoji == "❌":
                            return await ctx.send(f":ok_hand: Cancelled start match.")

                        # ========================================================
                        # ROUND 3 FLOW
                        # ========================================================

                        round_3_flow_embed = discord.Embed()
                        round_3_flow_embed.add_field(name="Who won round three flow?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}",
                            f":x: Endmatch"
                        ]))
                        round_3_flow_message = await ctx.send(embed=round_3_flow_embed)

                        await round_3_flow_message.add_reaction("1️⃣")
                        await round_3_flow_message.add_reaction("2️⃣")
                        await round_3_flow_message.add_reaction("❌")

                        round_3_flow_reaction, round_3_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_flow_reaction.emoji == "1️⃣":
                            round_3_flow_winner = defender
                            defender_points.append('round 3 flow')
                        elif round_3_flow_reaction.emoji == "2️⃣":
                            round_3_flow_winner = challenger
                            challenger_points.append('round 3 flow')
                        elif round_3_flow_reaction.emoji == "❌":
                            return await ctx.send(f":ok_hand: Cancelled start match.")

                        # ========================================================
                        # ROUND 3 DELIVERY
                        # ========================================================

                        round_3_delivery_embed = discord.Embed()
                        round_3_delivery_embed.add_field(name="Who won round three delivery?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}",
                            f":x: Endmatch"
                        ]))
                        round_3_delivery_message = await ctx.send(embed=round_3_delivery_embed)

                        await round_3_delivery_message.add_reaction("1️⃣")
                        await round_3_delivery_message.add_reaction("2️⃣")
                        await round_3_delivery_message.add_reaction("❌")

                        round_3_delivery_reaction, round_3_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_delivery_reaction.emoji == "1️⃣":
                            round_3_delivery_winner = defender
                            defender_points.append('round 3 delivery')
                        elif round_3_delivery_reaction.emoji == "2️⃣":
                            round_3_delivery_winner = challenger
                            challenger_points.append('round 3 delivery')
                        elif round_3_delivery_reaction.emoji == "❌":
                            return await ctx.send(f":ok_hand: Cancelled start match.")

                        round_3_check = discord.Embed()
                        round_3_check.add_field(name="Round 3 Results", value="\n".join([
                            f":brain: Content - {round_3_content_winner.mention}",
                            f":ocean: Flow - {round_3_flow_winner.mention}",
                            f":speaking_head: Delivery - {round_3_delivery_winner.mention}",
                        ]))
                        round_3_check_message = await ctx.send(embed=round_3_check)

                        await round_3_check_message.add_reaction("✅")
                        await round_3_check_message.add_reaction("❌")

                        round_3_check_reaction, round_3_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_check_reaction.emoji == "✅":
                            ok = True
                        else:
                            continue

            # ========================================================
            # JUDGES AND HOST 
            # ========================================================

            judge_embed = discord.Embed()
            judge_embed.add_field(name="Who are the judges for this match?", value="\n".join([
                "Mention the judges and put a space between each mention."
            ]))
            judge_message = await ctx.send(embed=judge_embed)

            judge_response = await self.bot.wait_for('message', check=msg_check)
            if judge_response.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")
            judges = []

            for judge in judge_response.content.split(" "):
                valid_judge = await get_member_info(ctx, judge)
                judges.append(valid_judge)

            host_embed = discord.Embed()
            host_embed.add_field(name="Who is the host for this match?", value="\n".join([
                "Acceptable inputs are: member ID, mention, or username"
            ]))
            host_message = await ctx.send(embed=host_embed)

            host_response = await self.bot.wait_for('message', check=msg_check)
            if host_response.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")
            host = await get_member_info(ctx, host_response.content)

            winner = {'who': challenger, 'ratio': (len(challenger_points), len(defender_points)), 'by': calling} if len(challenger_points) > len(defender_points) else {'who': defender, 'ratio': (len(defender_points), len(challenger_points)), 'by': calling}

            quote_embed = discord.Embed()
            quote_embed.add_field(name="What is the quote of the match winner?", value="Type the winner's quote in the chat please.")
            quote_message = await ctx.send(embed=quote_embed)

            winner_quote = await self.bot.wait_for('message', check=msg_check)
            if winner_quote.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # DETERMINE THE CALL FOR THE MATCH
            # ========================================================

            majority_round_one = None
            majority_round_two = None
            majority_round_three = None
            defender_majorities = 0
            challenger_majorities = 0

            defender_round_ones = 0
            defender_round_twos = 0
            defender_round_threes = 0
        
            challenger_round_ones = 0
            challenger_round_twos = 0
            challenger_round_threes = 0

            for point in defender_points:

                if 'round 1' in point:
                    defender_round_ones += 1
                elif 'round 2' in point:
                    defender_round_twos += 1
                elif 'round 3' in point:
                    defender_round_threes += 1
                
            for point in challenger_points:

                if 'round 1' in point:
                    challenger_round_ones += 1
                elif 'round 2' in point:
                    challenger_round_twos += 1
                elif 'round 3' in point:
                    challenger_round_threes += 1
            
            if defender_round_ones > challenger_round_ones:
                majority_round_one = defender
                defender_majorities += 1
            if challenger_round_ones > defender_round_ones:
                majority_round_one = challenger
                challenger_majorities += 1
            
            if defender_round_twos > challenger_round_twos:
                majority_round_two = defender
                defender_majorities += 1
            if challenger_round_twos > defender_round_twos:
                majority_round_two = challenger
                challenger_majorities += 1

            if defender_round_threes > challenger_round_threes:
                majority_round_three = defender
                defender_majorities += 1
            if challenger_round_threes > defender_round_threes:
                majority_round_three = challenger
                challenger_majorities += 1

            calling = "Couldn't make the call."

            if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                calling = "Unanimous Decision"
            if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                calling = "KO"
            if defender_majorities >= 1 and challenger_majorities >= 1:
                calling = "Split Decision"

            round_1 = {
                "content": 'N/A',
                "flow": 'N/A',
                "delivery": 'N/A'
            }
            round_2 = {
                "content": 'N/A',
                "flow": 'N/A',
                "delivery": 'N/A'
            }
            round_3 = {
                "content": 'N/A',
                "flow": 'N/A',
                "delivery": 'N/A'
            }

            for point in defender_points:
                if 'round 1 content' in point:
                    round_1['content'] = defender.display_name
                elif 'round 1 flow' in point:
                    round_1['flow'] = defender.display_name
                elif 'round 1 delivery' in point:
                    round_1['delivery'] = defender.display_name
                elif 'round 2 content' in point:
                    round_2['content'] = defender.display_name
                elif 'round 2 flow' in point:
                    round_2['flow'] = defender.display_name
                elif 'round 2 delivery' in point:
                    round_2['delivery'] = defender.display_name
                elif 'round 3 content' in point:
                    round_3['content'] = defender.display_name
                elif 'round 3 flow' in point:
                    round_3['flow'] = defender.display_name
                elif 'round 3 delivery' in point:
                    round_3['delivery'] = defender.display_name

            for point in challenger_points:
                if 'round 1 content' in point:
                    round_1['content'] = challenger.display_name
                elif 'round 1 flow' in point:
                    round_1['flow'] = challenger.display_name
                elif 'round 1 delivery' in point:
                    round_1['delivery'] = challenger.display_name
                elif 'round 2 content' in point:
                    round_2['content'] = challenger.display_name
                elif 'round 2 flow' in point:
                    round_2['flow'] = challenger.display_name
                elif 'round 2 delivery' in point:
                    round_2['delivery'] = challenger.display_name
                elif 'round 3 content' in point:
                    round_3['content'] = challenger.display_name
                elif 'round 3 flow' in point:
                    round_3['flow'] = challenger.display_name
                elif 'round 3 delivery' in point:
                    round_3['delivery'] = challenger.display_name

            judge_formatted = " ".join([judge.mention for judge in judges])
            
            bout_embed = discord.Embed()
            bout_embed.title = "TFC Regular Match Conclusion"
            bout_embed.description = "\n".join([
                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                "",
                f"Host: {host.mention}",
                f"Judges: {judge_formatted}",
                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
            ])
            bout_embed.add_field(name="Round 1", value="\n".join([
                f"Content: {round_1['content']}",
                f"Flow: {round_1['flow']}",
                f"Delivery: {round_1['delivery']}",
            ]), inline=False)
            bout_embed.add_field(name=f"Round 2", value="\n".join([
                f"Content: {round_2['content']}",
                f"Flow: {round_2['flow']}",
                f"Delivery: {round_2['delivery']}",
            ]), inline=False)
            bout_embed.add_field(name=f"Round 3", value="\n".join([
                f"Content: {round_3['content']}",
                f"Flow: {round_3['flow']}",
                f"Delivery: {round_3['delivery']}",
            ]), inline=False)
            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
            bout_message = await ctx.send(embed=bout_embed)

            await bout_message.add_reaction("✅")
            await bout_message.add_reaction("❌")

            bouts = server.get_channel(777650383769960469)

            bout_reaction, bout_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if bout_reaction.emoji == "✅":
                await bouts.send(embed=bout_embed)
                await ctx.send(":ok_hand:")
            else:
                editting = True
                while editting is True:
                    embed = discord.Embed()
                    embed.add_field(name="What would you like to change?", value="\n".join([
                        f":one: Round One",
                        f":two: Round Two",
                        f":three: Round Three",
                        f":four: Host",
                        f":five: Judges",
                        f":six: Winner Quote",
                        f":x: Cancel Edit (send in #bouts)"
                    ]))
                    msg = await ctx.send(embed=embed)

                    await msg.add_reaction("1️⃣")
                    await msg.add_reaction("2️⃣")
                    await msg.add_reaction("3️⃣")
                    await msg.add_reaction("4️⃣")
                    await msg.add_reaction("5️⃣")
                    await msg.add_reaction("6️⃣")
                    await msg.add_reaction("❌")

                    edit_reaction, edit_user = await self.bot.wait_for('reaction_add', check=reaction_check)

                    if edit_reaction.emoji == "6️⃣":
                        quote_embed = discord.Embed()
                        quote_embed.add_field(name="What is the quote of the match winner?", value="Type the winner's quote in the chat please.")
                        quote_message = await ctx.send(embed=quote_embed)

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":
                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Regular Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue

                    elif edit_reaction.emoji == "4️⃣":
                        host_embed = discord.Embed()
                        host_embed.add_field(name="Who is the host for this match?", value="\n".join([
                            "Acceptable inputs are: member ID, mention, or username"
                        ]))
                        host_message = await ctx.send(embed=host_embed)

                        host_response = await self.bot.wait_for('message', check=msg_check)
                        host = await get_member_info(ctx, host_response.content)

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":
                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Regular Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "5️⃣":
                        judge_embed = discord.Embed()
                        judge_embed.add_field(name="Who are the judges for this match?", value="\n".join([
                            "Mention the judges and put a space between each mention."
                        ]))
                        judge_message = await ctx.send(embed=judge_embed)

                        judge_response = await self.bot.wait_for('message', check=msg_check)
                        judges = []

                        for judge in judge_response.content.split(" "):
                            valid_judge = await get_member_info(ctx, judge)
                            judges.append(valid_judge)

                        judge_formatted = " ".join([judge.mention for judge in judges])

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":
                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Regular Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "1️⃣":

                        majority_round_one = None
                        majority_round_two = None
                        majority_round_three = None
                        defender_majorities = 0
                        challenger_majorities = 0

                        defender_round_ones = 0
                        defender_round_twos = 0
                        defender_round_threes = 0
                    
                        challenger_round_ones = 0
                        challenger_round_twos = 0
                        challenger_round_threes = 0

                        for point in defender_points:

                            if 'round 1' in point:
                                defender_round_ones += 1
                            elif 'round 2' in point:
                                defender_round_twos += 1
                            elif 'round 3' in point:
                                defender_round_threes += 1
                            
                        for point in challenger_points:

                            if 'round 1' in point:
                                challenger_round_ones += 1
                            elif 'round 2' in point:
                                challenger_round_twos += 1
                            elif 'round 3' in point:
                                challenger_round_threes += 1
                        
                        if defender_round_ones > challenger_round_ones:
                            majority_round_one = defender
                            defender_majorities += 1
                        if challenger_round_ones > defender_round_ones:
                            majority_round_one = challenger
                            challenger_majorities += 1
                        
                        if defender_round_twos > challenger_round_twos:
                            majority_round_two = defender
                            defender_majorities += 1
                        if challenger_round_twos > defender_round_twos:
                            majority_round_two = challenger
                            challenger_majorities += 1

                        if defender_round_threes > challenger_round_threes:
                            majority_round_three = defender
                            defender_majorities += 1
                        if challenger_round_threes > defender_round_threes:
                            majority_round_three = challenger
                            challenger_majorities += 1

                        calling = "Couldn't make the call."

                        if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                            calling = "Unanimous Decision"
                        if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                            calling = "KO"
                        if defender_majorities >= 1 and challenger_majorities >= 1:
                            calling = "Split Decision"

                        winner = {'who': challenger, 'ratio': (len(challenger_points), len(defender_points)), 'by': calling} if len(challenger_points) > len(defender_points) else {'who': defender, 'ratio': (len(defender_points), len(challenger_points)), 'by': calling}

                        # ========================================================
                        # ROUND 1 INFORMATION
                        # ========================================================
                        # ROUND 1 CONTENT
                        # ========================================================

                        for point in defender_points:
                            if 'round 1' in point:
                                defender_points.remove(point)
                            
                        for point in challenger_points:
                            if 'round 1' in point:
                                challenger_points.remove(point)

                        round_1_content_embed = discord.Embed()
                        round_1_content_embed.add_field(name="Who won round one content?", value=f"\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_1_content_message = await ctx.send(embed=round_1_content_embed)

                        await round_1_content_message.add_reaction("1️⃣")
                        await round_1_content_message.add_reaction("2️⃣")

                        round_1_content_reaction, round_1_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_1_content_reaction.emoji == "1️⃣":
                            round_1_content_winner = defender
                            defender_points.append('round 1 content')
                        elif round_1_content_reaction.emoji == "2️⃣":
                            round_1_content_winner = challenger
                            challenger_points.append('round 1 content')

                        # ========================================================
                        # ROUND 1 FLOW
                        # ========================================================

                        round_1_flow_embed = discord.Embed()
                        round_1_flow_embed.add_field(name="Who won round one flow?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_1_flow_message = await ctx.send(embed=round_1_flow_embed)

                        await round_1_flow_message.add_reaction("1️⃣")
                        await round_1_flow_message.add_reaction("2️⃣")

                        round_1_flow_reaction, round_1_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_1_flow_reaction.emoji == "1️⃣":
                            round_1_flow_winner = defender
                            defender_points.append('round 1 flow')
                        elif round_1_flow_reaction.emoji == "2️⃣":
                            round_1_flow_winner = challenger
                            challenger_points.append('round 1 flow')

                        # ========================================================
                        # ROUND 1 DELIVERY
                        # ========================================================

                        round_1_delivery_embed = discord.Embed()
                        round_1_delivery_embed.add_field(name="Who won round one delivery?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_1_delivery_message = await ctx.send(embed=round_1_delivery_embed)

                        await round_1_delivery_message.add_reaction("1️⃣")
                        await round_1_delivery_message.add_reaction("2️⃣")

                        round_1_delivery_reaction, round_1_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_1_delivery_reaction.emoji == "1️⃣":
                            round_1_delivery_winner = defender
                            defender_points.append('round 1 delivery')
                        elif round_1_delivery_reaction.emoji == "2️⃣":
                            round_1_delivery_winner = challenger
                            challenger_points.append('round 1 delivery')

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":

                            round_1 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_2 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_3 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }

                            for point in defender_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = defender.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = defender.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = defender.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = defender.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = defender.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = defender.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = defender.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = defender.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = defender.display_name

                            for point in challenger_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = challenger.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = challenger.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = challenger.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = challenger.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = challenger.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = challenger.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = challenger.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = challenger.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = challenger.display_name

                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Regular Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "2️⃣":

                        majority_round_one = None
                        majority_round_two = None
                        majority_round_three = None
                        defender_majorities = 0
                        challenger_majorities = 0

                        defender_round_ones = 0
                        defender_round_twos = 0
                        defender_round_threes = 0
                    
                        challenger_round_ones = 0
                        challenger_round_twos = 0
                        challenger_round_threes = 0

                        for point in defender_points:

                            if 'round 1' in point:
                                defender_round_ones += 1
                            elif 'round 2' in point:
                                defender_round_twos += 1
                            elif 'round 3' in point:
                                defender_round_threes += 1
                            
                        for point in challenger_points:

                            if 'round 1' in point:
                                challenger_round_ones += 1
                            elif 'round 2' in point:
                                challenger_round_twos += 1
                            elif 'round 3' in point:
                                challenger_round_threes += 1
                        
                        if defender_round_ones > challenger_round_ones:
                            majority_round_one = defender
                            defender_majorities += 1
                        if challenger_round_ones > defender_round_ones:
                            majority_round_one = challenger
                            challenger_majorities += 1
                        
                        if defender_round_twos > challenger_round_twos:
                            majority_round_two = defender
                            defender_majorities += 1
                        if challenger_round_twos > defender_round_twos:
                            majority_round_two = challenger
                            challenger_majorities += 1

                        if defender_round_threes > challenger_round_threes:
                            majority_round_three = defender
                            defender_majorities += 1
                        if challenger_round_threes > defender_round_threes:
                            majority_round_three = challenger
                            challenger_majorities += 1

                        calling = "Couldn't make the call."

                        if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                            calling = "Unanimous Decision"
                        if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                            calling = "KO"
                        if defender_majorities >= 1 and challenger_majorities >= 1:
                            calling = "Split Decision"

                        winner = {'who': challenger, 'ratio': (len(challenger_points), len(defender_points)), 'by': calling} if len(challenger_points) > len(defender_points) else {'who': defender, 'ratio': (len(defender_points), len(challenger_points)), 'by': calling}

                        # ========================================================
                        # ROUND 2 INFORMATION
                        # ========================================================
                        # ROUND 2 CONTENT
                        # ========================================================

                        for point in defender_points:
                            if 'round 2' in point:
                                defender_points.remove(point)
                            
                        for point in challenger_points:
                            if 'round 2' in point:
                                challenger_points.remove(point)

                        round_2_content_embed = discord.Embed()
                        round_2_content_embed.add_field(name="Who won round two content?", value=f"\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_2_content_message = await ctx.send(embed=round_2_content_embed)

                        await round_2_content_message.add_reaction("1️⃣")
                        await round_2_content_message.add_reaction("2️⃣")

                        round_2_content_reaction, round_2_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_2_content_reaction.emoji == "1️⃣":
                            round_2_content_winner = defender
                            defender_points.append('round 2 content')
                        elif round_2_content_reaction.emoji == "2️⃣":
                            round_2_content_winner = challenger
                            challenger_points.append('round 2 content')

                        # ========================================================
                        # ROUND 1 FLOW
                        # ========================================================

                        round_2_flow_embed = discord.Embed()
                        round_2_flow_embed.add_field(name="Who won round two flow?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_2_flow_message = await ctx.send(embed=round_2_flow_embed)

                        await round_2_flow_message.add_reaction("1️⃣")
                        await round_2_flow_message.add_reaction("2️⃣")

                        round_2_flow_reaction, round_2_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_2_flow_reaction.emoji == "1️⃣":
                            round_2_flow_winner = defender
                            defender_points.append('round 2 flow')
                        elif round_2_flow_reaction.emoji == "2️⃣":
                            round_2_flow_winner = challenger
                            challenger_points.append('round 2 flow')

                        # ========================================================
                        # ROUND 2 DELIVERY
                        # ========================================================

                        round_2_delivery_embed = discord.Embed()
                        round_2_delivery_embed.add_field(name="Who won round two delivery?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_2_delivery_message = await ctx.send(embed=round_2_delivery_embed)

                        await round_2_delivery_message.add_reaction("1️⃣")
                        await round_2_delivery_message.add_reaction("2️⃣")

                        round_2_delivery_reaction, round_2_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_2_delivery_reaction.emoji == "1️⃣":
                            round_2_delivery_winner = defender
                            defender_points.append('round 2 delivery')
                        elif round_2_delivery_reaction.emoji == "2️⃣":
                            round_2_delivery_winner = challenger
                            challenger_points.append('round 2 delivery')

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":

                            round_1 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_2 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_3 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }

                            for point in defender_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = defender.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = defender.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = defender.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = defender.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = defender.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = defender.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = defender.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = defender.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = defender.display_name

                            for point in challenger_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = challenger.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = challenger.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = challenger.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = challenger.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = challenger.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = challenger.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = challenger.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = challenger.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = challenger.display_name

                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Regular Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "3️⃣":

                        majority_round_one = None
                        majority_round_two = None
                        majority_round_three = None
                        defender_majorities = 0
                        challenger_majorities = 0

                        defender_round_ones = 0
                        defender_round_twos = 0
                        defender_round_threes = 0
                    
                        challenger_round_ones = 0
                        challenger_round_twos = 0
                        challenger_round_threes = 0

                        for point in defender_points:

                            if 'round 1' in point:
                                defender_round_ones += 1
                            elif 'round 2' in point:
                                defender_round_twos += 1
                            elif 'round 3' in point:
                                defender_round_threes += 1
                            
                        for point in challenger_points:

                            if 'round 1' in point:
                                challenger_round_ones += 1
                            elif 'round 2' in point:
                                challenger_round_twos += 1
                            elif 'round 3' in point:
                                challenger_round_threes += 1
                        
                        if defender_round_ones > challenger_round_ones:
                            majority_round_one = defender
                            defender_majorities += 1
                        if challenger_round_ones > defender_round_ones:
                            majority_round_one = challenger
                            challenger_majorities += 1
                        
                        if defender_round_twos > challenger_round_twos:
                            majority_round_two = defender
                            defender_majorities += 1
                        if challenger_round_twos > defender_round_twos:
                            majority_round_two = challenger
                            challenger_majorities += 1

                        if defender_round_threes > challenger_round_threes:
                            majority_round_three = defender
                            defender_majorities += 1
                        if challenger_round_threes > defender_round_threes:
                            majority_round_three = challenger
                            challenger_majorities += 1

                        calling = "Couldn't make the call."

                        if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                            calling = "Unanimous Decision"
                        if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                            calling = "KO"
                        if defender_majorities >= 1 and challenger_majorities >= 1:
                            calling = "Split Decision"

                        winner = {'who': challenger, 'ratio': (len(challenger_points), len(defender_points)), 'by': calling} if len(challenger_points) > len(defender_points) else {'who': defender, 'ratio': (len(defender_points), len(challenger_points)), 'by': calling}

                        # ========================================================
                        # ROUND 2 INFORMATION
                        # ========================================================
                        # ROUND 2 CONTENT
                        # ========================================================

                        for point in defender_points:
                            if 'round 3' in point:
                                defender_points.remove(point)
                            
                        for point in challenger_points:
                            if 'round 3' in point:
                                challenger_points.remove(point)

                        round_3_content_embed = discord.Embed()
                        round_3_content_embed.add_field(name="Who won round three content?", value=f"\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_3_content_message = await ctx.send(embed=round_3_content_embed)

                        await round_3_content_message.add_reaction("1️⃣")
                        await round_3_content_message.add_reaction("2️⃣")

                        round_3_content_reaction, round_3_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_content_reaction.emoji == "1️⃣":
                            round_3_content_winner = defender
                            defender_points.append('round 3 content')
                        elif round_3_content_reaction.emoji == "2️⃣":
                            round_3_content_winner = challenger
                            challenger_points.append('round 3 content')

                        # ========================================================
                        # ROUND 3 FLOW
                        # ========================================================

                        round_3_flow_embed = discord.Embed()
                        round_3_flow_embed.add_field(name="Who won round three flow?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_3_flow_message = await ctx.send(embed=round_3_flow_embed)

                        await round_3_flow_message.add_reaction("1️⃣")
                        await round_3_flow_message.add_reaction("2️⃣")

                        round_3_flow_reaction, round_3_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_flow_reaction.emoji == "1️⃣":
                            round_3_flow_winner = defender
                            defender_points.append('round 3 flow')
                        elif round_3_flow_reaction.emoji == "2️⃣":
                            round_3_flow_winner = challenger
                            challenger_points.append('round 3 flow')

                        # ========================================================
                        # ROUND 3 DELIVERY
                        # ========================================================

                        round_3_delivery_embed = discord.Embed()
                        round_3_delivery_embed.add_field(name="Who won round three delivery?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_3_delivery_message = await ctx.send(embed=round_3_delivery_embed)

                        await round_3_delivery_message.add_reaction("1️⃣")
                        await round_3_delivery_message.add_reaction("2️⃣")

                        round_3_delivery_reaction, round_3_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_delivery_reaction.emoji == "1️⃣":
                            round_3_delivery_winner = defender
                            defender_points.append('round 3 delivery')
                        elif round_3_delivery_reaction.emoji == "2️⃣":
                            round_3_delivery_winner = challenger
                            challenger_points.append('round 3 delivery')

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":

                            round_1 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_2 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_3 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }

                            for point in defender_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = defender.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = defender.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = defender.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = defender.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = defender.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = defender.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = defender.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = defender.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = defender.display_name

                            for point in challenger_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = challenger.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = challenger.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = challenger.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = challenger.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = challenger.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = challenger.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = challenger.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = challenger.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = challenger.display_name

                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Regular Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "❌":

                        await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                        editting = False
                        bout_embed = discord.Embed()
                        bout_embed.title = "TFC Regular Match Conclusion"
                        bout_embed.description = "\n".join([
                            f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                            "",
                            f"Host: {host.mention}",
                            f"Judges: {judge_formatted}",
                            f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                        ])
                        bout_embed.add_field(name="Round 1", value="\n".join([
                            f"Content: {round_1['content']}",
                            f"Flow: {round_1['flow']}",
                            f"Delivery: {round_1['delivery']}",
                        ]), inline=False)
                        bout_embed.add_field(name=f"Round 2", value="\n".join([
                            f"Content: {round_2['content']}",
                            f"Flow: {round_2['flow']}",
                            f"Delivery: {round_2['delivery']}",
                        ]), inline=False)
                        bout_embed.add_field(name=f"Round 3", value="\n".join([
                            f"Content: {round_3['content']}",
                            f"Flow: {round_3['flow']}",
                            f"Delivery: {round_3['delivery']}",
                        ]), inline=False)
                        bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                        bout_message = await bouts.send(embed=bout_embed)
            
            previous_matches = await ctx.fetch("SELECT * FROM matches WHERE guild_id=$1", server.id)
            bout_id = len(previous_matches) if previous_matches else 0

            defender_id = defender.id
            challenger_id = challenger.id
            judges = [judge.id for judge in judges]
            host_id = host.id
            winner_id = winner['who'].id
            loser_id = defender.id if winner['who'].id == challenger.id else challenger.id
            ratio = [winner['ratio'][0], winner['ratio'][1]]
            decision = calling
            defender_category_wins = defender_points
            defender_category_losses = challenger_points
            challenger_category_wins = challenger_points
            challenger_category_losses = defender_points
            match_type = 'regular'

            await ctx.execute("""
            INSERT INTO matches (
                guild_id,
                bout_id,
                defender_id,
                challenger_id,
                judges,
                host_id,
                winner_id,
                loser_id,
                ratio,
                decision,
                defender_category_wins,
                defender_category_losses,
                challenger_category_wins,
                challenger_category_losses,
                match_type,
                inserted_at,
                winner_quote
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                $11, $12, $13, $14, $15, $16, $17
            )
            """, server.id, bout_id+1, defender_id, challenger_id, judges, host_id, winner_id, loser_id, ratio, decision, defender_category_wins, defender_category_losses, challenger_category_wins, challenger_category_losses, match_type, datetime.datetime.utcnow(), winner_quote.content)
            
        elif starting_reaction.emoji == "2️⃣":
            
            # Asking who the defender is
            defender_embed = discord.Embed()
            defender_embed.add_field(name=f"Who is the defender?", value="\n".join([
                f"Acceptable inputs are: member ID, mention, or username"
            ]))
            defender_message = await ctx.send(embed=defender_embed)

            defender_response = await self.bot.wait_for('message', check=msg_check)
            if defender_response.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")
            defender = await get_member_info(ctx, defender_response.content)

            if not defender:
                found = False
                while found is False:

                    defender_embed = discord.Embed()
                    defender_embed.add_field(name=f"Who is the defender?", value="\n".join([
                        f"Acceptable inputs are: member ID, mention, or username"
                    ]))
                    defender_message = await ctx.send(embed=defender_embed)

                    defender_response = await self.bot.wait_for('message', check=msg_check)
                    if defender_response.content.lower() == "cancel":
                        return await ctx.send(f":ok_hand: Cancelled start match.")
                    defender = await get_member_info(ctx, defender_response.content)

                    if not defender:
                        continue
                    
                    found = True

            challenger_embed = discord.Embed()
            challenger_embed.add_field(name="Who is the challenger?", value="\n".join([ 
                f"Acceptable inputs are: member ID, mention, or username"
            ]))
            challenger_message = await ctx.send(embed=challenger_embed)

            challenger_response = await self.bot.wait_for('message', check=msg_check)
            if challenger_response.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")
            challenger = await get_member_info(ctx, challenger_response.content)

            if not challenger:
                found = False
                while found is False:

                    challenger_embed = discord.Embed()
                    challenger_embed.add_field(name="Who is the challenger?", value="\n".join([
                        f"Acceptable inputs are: member ID, mention, or username"
                    ]))
                    challenger_message = await ctx.send(embed=challenger_embed)

                    challenger_response = await self.bot.wait_for('message', check=msg_check)
                    if challenger_response.content.lower() == "cancel":
                        return await ctx.send(f":ok_hand: Cancelled start match.")
                    challenger = await get_member_info(ctx, challenger_response.content)

                    if not challenger:
                        continue

                    found = True

            # ========================================================
            # ROUND 1 INFORMATION
            # ========================================================
            # ROUND 1 CONTENT
            # ========================================================

            defender_previous_wins = await ctx.fetch("""
            SELECT * FROM matches
            WHERE guild_id=$1 AND winner_id=$2
            """, server.id, defender.id)
            defender_previous_losses = await ctx.fetch("""
            SELECT * FROM matches
            WHERE guild_id=$1 AND loser_id=$2
            """, server.id, defender.id)
            defender_most_previous = f"[{len(defender_previous_wins)}-{len(defender_previous_losses)}]"

            challenger_previous_wins = await ctx.fetch("""
            SELECT * FROM matches
            WHERE guild_id=$1 AND winner_id=$2
            """, server.id, challenger.id)
            challenger_previous_losses = await ctx.fetch("""
            SELECT * FROM matches
            WHERE guild_id=$1 AND loser_id=$2
            """, server.id, challenger.id)
            challenger_most_previous = f"[{len(challenger_previous_wins)}-{len(challenger_previous_losses)}]"

            defender_points = []
            challenger_points = []

            round_1_content_embed = discord.Embed()
            round_1_content_embed.add_field(name="Who won round one content?", value=f"\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_1_content_message = await ctx.send(embed=round_1_content_embed)

            await round_1_content_message.add_reaction("1️⃣")
            await round_1_content_message.add_reaction("2️⃣")
            await round_1_content_message.add_reaction("❌")

            round_1_content_reaction, round_1_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_1_content_reaction.emoji == "1️⃣":
                round_1_content_winner = defender
                defender_points.append('round 1 content')
            elif round_1_content_reaction.emoji == "2️⃣":
                round_1_content_winner = challenger
                challenger_points.append('round 1 content')
            elif round_1_content_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # ROUND 1 FLOW
            # ========================================================

            round_1_flow_embed = discord.Embed()
            round_1_flow_embed.add_field(name="Who won round one flow?", value="\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_1_flow_message = await ctx.send(embed=round_1_flow_embed)

            await round_1_flow_message.add_reaction("1️⃣")
            await round_1_flow_message.add_reaction("2️⃣")
            await round_1_flow_message.add_reaction("❌")

            round_1_flow_reaction, round_1_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_1_flow_reaction.emoji == "1️⃣":
                round_1_flow_winner = defender
                defender_points.append('round 1 flow')
            elif round_1_flow_reaction.emoji == "2️⃣":
                round_1_flow_winner = challenger
                challenger_points.append('round 1 flow')
            elif round_1_flow_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # ROUND 1 DELIVERY
            # ========================================================

            round_1_delivery_embed = discord.Embed()
            round_1_delivery_embed.add_field(name="Who won round one delivery?", value="\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_1_delivery_message = await ctx.send(embed=round_1_delivery_embed)

            await round_1_delivery_message.add_reaction("1️⃣")
            await round_1_delivery_message.add_reaction("2️⃣")
            await round_1_delivery_message.add_reaction("❌")

            round_1_delivery_reaction, round_1_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_1_delivery_reaction.emoji == "1️⃣":
                round_1_delivery_winner = defender
                defender_points.append('round 1 delivery')
            elif round_1_delivery_reaction.emoji == "2️⃣":
                round_1_delivery_winner = challenger
                challenger_points.append('round 1 delivery')
            elif round_1_delivery_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # SAFETY CHECK
            # ========================================================

            round_1_check = discord.Embed()
            round_1_check.add_field(name="Round 1 Results", value="\n".join([
                f":brain: Content - {round_1_content_winner.mention}",
                f":ocean: Flow - {round_1_flow_winner.mention}",
                f":speaking_head: Delivery - {round_1_delivery_winner.mention}",
            ]))
            round_1_check_message = await ctx.send(embed=round_1_check)

            await round_1_check_message.add_reaction("✅")
            await round_1_check_message.add_reaction("❌")

            round_1_check_reaction, round_1_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_1_check_reaction.emoji == "❌":
                ok = False

                for win in defender_points:
                    if 'round 1' in win:
                        defender_points.remove(win)
                
                for win in challenger_points:
                    if 'round 1' in win:
                        challenger_points.remove(win)

                while ok is False:
                    # ========================================================
                    # ROUND 1 INFORMATION
                    # ========================================================
                    # ROUND 1 CONTENT
                    # ========================================================

                    round_1_content_embed = discord.Embed()
                    round_1_content_embed.add_field(name="Who won round one content?", value=f"\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_1_content_message = await ctx.send(embed=round_1_content_embed)

                    await round_1_content_message.add_reaction("1️⃣")
                    await round_1_content_message.add_reaction("2️⃣")
                    await round_1_content_message.add_reaction("❌")

                    round_1_content_reaction, round_1_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_1_content_reaction.emoji == "1️⃣":
                        round_1_content_winner = defender
                        defender_points.append('round 1 content')
                    elif round_1_content_reaction.emoji == "2️⃣":
                        round_1_content_winner = challenger
                        challenger_points.append('round 1 content')
                    elif round_1_content_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    # ========================================================
                    # ROUND 1 FLOW
                    # ========================================================

                    round_1_flow_embed = discord.Embed()
                    round_1_flow_embed.add_field(name="Who won round one flow?", value="\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_1_flow_message = await ctx.send(embed=round_1_flow_embed)

                    await round_1_flow_message.add_reaction("1️⃣")
                    await round_1_flow_message.add_reaction("2️⃣")
                    await round_1_flow_message.add_reaction("❌")

                    round_1_flow_reaction, round_1_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_1_flow_reaction.emoji == "1️⃣":
                        round_1_flow_winner = defender
                        defender_points.append('round 1 flow')
                    elif round_1_flow_reaction.emoji == "2️⃣":
                        round_1_flow_winner = challenger
                        challenger_points.append('round 1 flow')
                    elif round_1_flow_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    # ========================================================
                    # ROUND 1 DELIVERY
                    # ========================================================

                    round_1_delivery_embed = discord.Embed()
                    round_1_delivery_embed.add_field(name="Who won round one delivery?", value="\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}"
                    ]))
                    round_1_delivery_message = await ctx.send(embed=round_1_delivery_embed)

                    await round_1_delivery_message.add_reaction("1️⃣")
                    await round_1_delivery_message.add_reaction("2️⃣")
                    await round_1_delivery_message.add_reaction("❌")

                    round_1_delivery_reaction, round_1_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_1_delivery_reaction.emoji == "1️⃣":
                        round_1_delivery_winner = defender
                        defender_points.append('round 1 delivery')
                    elif round_1_delivery_reaction.emoji == "2️⃣":
                        round_1_delivery_winner = challenger
                        challenger_points.append('round 1 delivery')
                    elif round_1_delivery_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    round_1_check = discord.Embed()
                    round_1_check.add_field(name="Round 1 Results", value="\n".join([
                        f":brain: Content - {round_1_content_winner.mention}",
                        f":ocean: Flow - {round_1_flow_winner.mention}",
                        f":speaking_head: Delivery - {round_1_delivery_winner.mention}",
                    ]))
                    round_1_check_message = await ctx.send(embed=round_1_check)

                    await round_1_check_message.add_reaction("✅")
                    await round_1_check_message.add_reaction("❌")

                    round_1_check_reaction, round_1_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_1_check_reaction.emoji == "✅":
                        ok = True
                    else:
                        continue

            # ========================================================
            # ROUND 2 INFORMATION
            # ========================================================
            # ROUND 2 CONTENT
            # ========================================================

            round_2_content_embed = discord.Embed()
            round_2_content_embed.add_field(name="Who won round two content?", value=f"\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_2_content_message = await ctx.send(embed=round_2_content_embed)

            await round_2_content_message.add_reaction("1️⃣")
            await round_2_content_message.add_reaction("2️⃣")
            await round_2_content_message.add_reaction("❌")

            round_2_content_reaction, round_2_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_2_content_reaction.emoji == "1️⃣":
                round_2_content_winner = defender
                defender_points.append('round 2 content')
            elif round_2_content_reaction.emoji == "2️⃣":
                round_2_content_winner = challenger
                challenger_points.append('round 2 content')
            elif round_2_content_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # ROUND 2 FLOW
            # ========================================================

            round_2_flow_embed = discord.Embed()
            round_2_flow_embed.add_field(name="Who won round two flow?", value="\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_2_flow_message = await ctx.send(embed=round_2_flow_embed)

            await round_2_flow_message.add_reaction("1️⃣")
            await round_2_flow_message.add_reaction("2️⃣")
            await round_2_flow_message.add_reaction("❌")

            round_2_flow_reaction, round_2_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_2_flow_reaction.emoji == "1️⃣":
                round_2_flow_winner = defender
                defender_points.append('round 2 flow')
            elif round_2_flow_reaction.emoji == "2️⃣":
                round_2_flow_winner = challenger
                challenger_points.append('round 2 flow')
            elif round_2_flow_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # ROUND 2 DELIVERY
            # ========================================================

            round_2_delivery_embed = discord.Embed()
            round_2_delivery_embed.add_field(name="Who won round two delivery?", value="\n".join([
                f":one: Defender: {defender.mention}",
                f":two: Challenger: {challenger.mention}",
                f":x: Endmatch"
            ]))
            round_2_delivery_message = await ctx.send(embed=round_2_delivery_embed)

            await round_2_delivery_message.add_reaction("1️⃣")
            await round_2_delivery_message.add_reaction("2️⃣")
            await round_2_delivery_message.add_reaction("❌")

            round_2_delivery_reaction, round_2_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_2_delivery_reaction.emoji == "1️⃣":
                round_2_delivery_winner = defender
                defender_points.append('round 2 delivery')
            elif round_2_delivery_reaction.emoji == "2️⃣":
                round_2_delivery_winner = challenger
                challenger_points.append('round 2 delivery')
            elif round_2_delivery_reaction.emoji == "❌":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # SAFETY CHECK
            # ========================================================

            round_2_check = discord.Embed()
            round_2_check.add_field(name="Round 2 Results", value="\n".join([
                f":brain: Content - {round_2_content_winner.mention}",
                f":ocean: Flow - {round_2_flow_winner.mention}",
                f":speaking_head: Delivery - {round_2_delivery_winner.mention}",
            ]))
            round_2_check_message = await ctx.send(embed=round_2_check)

            await round_2_check_message.add_reaction("✅")
            await round_2_check_message.add_reaction("❌")

            round_2_check_reaction, round_2_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if round_2_check_reaction.emoji == "❌":
                ok = False

                for win in defender_points:
                    if 'round 2' in win:
                        defender_points.remove(win)
                
                for win in challenger_points:
                    if 'round 2' in win:
                        challenger_points.remove(win)

                while ok is False:
                    # ========================================================
                    # ROUND 2 INFORMATION
                    # ========================================================
                    # ROUND 2 CONTENT
                    # ========================================================

                    round_2_content_embed = discord.Embed()
                    round_2_content_embed.add_field(name="Who won round two content?", value=f"\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_2_content_message = await ctx.send(embed=round_2_content_embed)

                    await round_2_content_message.add_reaction("1️⃣")
                    await round_2_content_message.add_reaction("2️⃣")
                    await round_2_content_message.add_reaction("❌")

                    round_2_content_reaction, round_2_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_2_content_reaction.emoji == "1️⃣":
                        round_2_content_winner = defender
                        defender_points.append('round 2 content')
                    elif round_2_content_reaction.emoji == "2️⃣":
                        round_2_content_winner = challenger
                        challenger_points.append('round 2 content')
                    elif round_2_content_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    # ========================================================
                    # ROUND 1 FLOW
                    # ========================================================

                    round_2_flow_embed = discord.Embed()
                    round_2_flow_embed.add_field(name="Who won round two flow?", value="\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_2_flow_message = await ctx.send(embed=round_2_flow_embed)

                    await round_2_flow_message.add_reaction("1️⃣")
                    await round_2_flow_message.add_reaction("2️⃣")
                    await round_2_flow_message.add_reaction("❌")

                    round_2_flow_reaction, round_2_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_2_flow_reaction.emoji == "1️⃣":
                        round_2_flow_winner = defender
                        defender_points.append('round 2 flow')
                    elif round_2_flow_reaction.emoji == "2️⃣":
                        round_2_flow_winner = challenger
                        challenger_points.append('round 2 flow')
                    elif round_2_flow_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    # ========================================================
                    # ROUND 2 DELIVERY
                    # ========================================================

                    round_2_delivery_embed = discord.Embed()
                    round_2_delivery_embed.add_field(name="Who won round two delivery?", value="\n".join([
                        f":one: Defender: {defender.mention}",
                        f":two: Challenger: {challenger.mention}",
                        f":x: Endmatch"
                    ]))
                    round_2_delivery_message = await ctx.send(embed=round_2_delivery_embed)

                    await round_2_delivery_message.add_reaction("1️⃣")
                    await round_2_delivery_message.add_reaction("2️⃣")
                    await round_2_delivery_message.add_reaction("❌")

                    round_2_delivery_reaction, round_2_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_2_delivery_reaction.emoji == "1️⃣":
                        round_2_delivery_winner = defender
                        defender_points.append('round 2 delivery')
                    elif round_2_delivery_reaction.emoji == "2️⃣":
                        round_2_delivery_winner = challenger
                        challenger_points.append('round 2 delivery')
                    elif round_2_delivery_reaction.emoji == "❌":
                        return await ctx.send(f":ok_hand: Cancelled start match.")

                    round_2_check = discord.Embed()
                    round_2_check.add_field(name="Round 2 Results", value="\n".join([
                        f":brain: Content - {round_2_content_winner.mention}",
                        f":ocean: Flow - {round_2_flow_winner.mention}",
                        f":speaking_head: Delivery - {round_2_delivery_winner.mention}",
                    ]))
                    round_2_check_message = await ctx.send(embed=round_2_check)

                    await round_2_check_message.add_reaction("✅")
                    await round_2_check_message.add_reaction("❌")

                    round_2_check_reaction, round_2_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                    if round_2_check_reaction.emoji == "✅":
                        ok = True
                    else:
                        continue

            # ========================================================
            # DETERMINE THE CALL FOR THE MATCH
            # ========================================================

            majority_round_one = None
            majority_round_two = None
            majority_round_three = None
            defender_majorities = 0
            challenger_majorities = 0

            defender_round_ones = 0
            defender_round_twos = 0
            defender_round_threes = 0
        
            challenger_round_ones = 0
            challenger_round_twos = 0
            challenger_round_threes = 0

            for point in defender_points:

                if 'round 1' in point:
                    defender_round_ones += 1
                elif 'round 2' in point:
                    defender_round_twos += 1
                elif 'round 3' in point:
                    defender_round_threes += 1
                
            for point in challenger_points:

                if 'round 1' in point:
                    challenger_round_ones += 1
                elif 'round 2' in point:
                    challenger_round_twos += 1
                elif 'round 3' in point:
                    challenger_round_threes += 1
            
            if defender_round_ones > challenger_round_ones:
                majority_round_one = defender
                defender_majorities += 1
            if challenger_round_ones > defender_round_ones:
                majority_round_one = challenger
                challenger_majorities += 1
            
            if defender_round_twos > challenger_round_twos:
                majority_round_two = defender
                defender_majorities += 1
            if challenger_round_twos > defender_round_twos:
                majority_round_two = challenger
                challenger_majorities += 1

            if defender_round_threes > challenger_round_threes:
                majority_round_three = defender
                defender_majorities += 1
            if challenger_round_threes > defender_round_threes:
                majority_round_three = challenger
                challenger_majorities += 1

            calling = "Couldn't make the call."

            if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                calling = "Unanimous Decision"
            if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                calling = "KO"
            if defender_majorities >= 1 and challenger_majorities >= 1:
                calling = "Split Decision"

            round_3_ignored = True

            if calling == "KO":
                pass
            else:
                round_3_ignored = False
                # ========================================================
                # ROUND 3 INFORMATION
                # ========================================================
                # ROUND 3 CONTENT
                # ========================================================

                round_3_content_embed = discord.Embed()
                round_3_content_embed.add_field(name="Who won round three content?", value=f"\n".join([
                    f":one: Defender: {defender.mention}",
                    f":two: Challenger: {challenger.mention}",
                    f":x: Endmatch"
                ]))
                round_3_content_message = await ctx.send(embed=round_3_content_embed)

                await round_3_content_message.add_reaction("1️⃣")
                await round_3_content_message.add_reaction("2️⃣")
                await round_3_content_message.add_reaction("❌")

                round_3_content_reaction, round_3_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                if round_3_content_reaction.emoji == "1️⃣":
                    round_3_content_winner = defender
                    defender_points.append('round 3 content')
                elif round_3_content_reaction.emoji == "2️⃣":
                    round_3_content_winner = challenger
                    challenger_points.append('round 3 content')
                elif round_3_content_reaction.emoji == "❌":
                    return await ctx.send(f":ok_hand: Cancelled start match.")

                # ========================================================
                # ROUND 3 FLOW
                # ========================================================

                round_3_flow_embed = discord.Embed()
                round_3_flow_embed.add_field(name="Who won round three flow?", value="\n".join([
                    f":one: Defender: {defender.mention}",
                    f":two: Challenger: {challenger.mention}",
                    f":x: Endmatch"
                ]))
                round_3_flow_message = await ctx.send(embed=round_2_flow_embed)

                await round_3_flow_message.add_reaction("1️⃣")
                await round_3_flow_message.add_reaction("2️⃣")
                await round_3_flow_message.add_reaction("❌")

                round_3_flow_reaction, round_3_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                if round_3_flow_reaction.emoji == "1️⃣":
                    round_3_flow_winner = defender
                    defender_points.append('round 3 flow')
                elif round_3_flow_reaction.emoji == "2️⃣":
                    round_3_flow_winner = challenger
                    challenger_points.append('round 3 flow')
                elif round_3_flow_reaction.emoji == "❌":
                    return await ctx.send(f":ok_hand: Cancelled start match.")

                # ========================================================
                # ROUND 3 DELIVERY
                # ========================================================

                round_3_delivery_embed = discord.Embed()
                round_3_delivery_embed.add_field(name="Who won round two delivery?", value="\n".join([
                    f":one: Defender: {defender.mention}",
                    f":two: Challenger: {challenger.mention}",
                    f":x: Endmatch"
                ]))
                round_3_delivery_message = await ctx.send(embed=round_3_delivery_embed)

                await round_3_delivery_message.add_reaction("1️⃣")
                await round_3_delivery_message.add_reaction("2️⃣")
                await round_3_delivery_message.add_reaction("❌")

                round_3_delivery_reaction, round_3_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                if round_3_delivery_reaction.emoji == "1️⃣":
                    round_3_delivery_winner = defender
                    defender_points.append('round 3 delivery')
                elif round_3_delivery_reaction.emoji == "2️⃣":
                    round_3_delivery_winner = challenger
                    challenger_points.append('round 3 delivery')
                elif round_3_delivery_reaction.emoji == "❌":
                    return await ctx.send(f":ok_hand: Cancelled start match.")

                # ========================================================
                # SAFETY CHECK
                # ========================================================

                round_3_check = discord.Embed()
                round_3_check.add_field(name="Round 3 Results", value="\n".join([
                    f":brain: Content - {round_3_content_winner.mention}",
                    f":ocean: Flow - {round_3_flow_winner.mention}",
                    f":speaking_head: Delivery - {round_3_delivery_winner.mention}",
                ]))
                round_3_check_message = await ctx.send(embed=round_3_check)

                await round_3_check_message.add_reaction("✅")
                await round_3_check_message.add_reaction("❌")

                round_3_check_reaction, round_3_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                if round_3_check_reaction.emoji == "❌":
                    ok = False
                    

                    for win in defender_points:
                        if 'round 3' in win:
                            defender_points.remove(win)
                    
                    for win in challenger_points:
                        if 'round 3' in win:
                            challenger_points.remove(win)

                    while ok is False:
                        # ========================================================
                        # ROUND 3 INFORMATION
                        # ========================================================
                        # ROUND 3 CONTENT
                        # ========================================================

                        round_3_content_embed = discord.Embed()
                        round_3_content_embed.add_field(name="Who won round three content?", value=f"\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}",
                            f":x: Endmatch"
                        ]))
                        round_3_content_message = await ctx.send(embed=round_3_content_embed)

                        await round_3_content_message.add_reaction("1️⃣")
                        await round_3_content_message.add_reaction("2️⃣")
                        await round_3_content_message.add_reaction("❌")

                        round_3_content_reaction, round_3_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_content_reaction.emoji == "1️⃣":
                            round_3_content_winner = defender
                            defender_points.append('round 3 content')
                        elif round_3_content_reaction.emoji == "2️⃣":
                            round_3_content_winner = challenger
                            challenger_points.append('round 3 content')
                        elif round_3_content_reaction.emoji == "❌":
                            return await ctx.send(f":ok_hand: Cancelled start match.")

                        # ========================================================
                        # ROUND 3 FLOW
                        # ========================================================

                        round_3_flow_embed = discord.Embed()
                        round_3_flow_embed.add_field(name="Who won round three flow?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}",
                            f":x: Endmatch"
                        ]))
                        round_3_flow_message = await ctx.send(embed=round_3_flow_embed)

                        await round_3_flow_message.add_reaction("1️⃣")
                        await round_3_flow_message.add_reaction("2️⃣")
                        await round_3_flow_message.add_reaction("❌")

                        round_3_flow_reaction, round_3_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_flow_reaction.emoji == "1️⃣":
                            round_3_flow_winner = defender
                            defender_points.append('round 3 flow')
                        elif round_3_flow_reaction.emoji == "2️⃣":
                            round_3_flow_winner = challenger
                            challenger_points.append('round 3 flow')
                        elif round_3_flow_reaction.emoji == "❌":
                            return await ctx.send(f":ok_hand: Cancelled start match.")

                        # ========================================================
                        # ROUND 3 DELIVERY
                        # ========================================================

                        round_3_delivery_embed = discord.Embed()
                        round_3_delivery_embed.add_field(name="Who won round three delivery?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}",
                            f":x: Endmatch"
                        ]))
                        round_3_delivery_message = await ctx.send(embed=round_3_delivery_embed)

                        await round_3_delivery_message.add_reaction("1️⃣")
                        await round_3_delivery_message.add_reaction("2️⃣")
                        await round_3_delivery_message.add_reaction("❌")

                        round_3_delivery_reaction, round_3_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_delivery_reaction.emoji == "1️⃣":
                            round_3_delivery_winner = defender
                            defender_points.append('round 3 delivery')
                        elif round_3_delivery_reaction.emoji == "2️⃣":
                            round_3_delivery_winner = challenger
                            challenger_points.append('round 3 delivery')
                        elif round_3_delivery_reaction.emoji == "❌":
                            return await ctx.send(f":ok_hand: Cancelled start match.")

                        round_3_check = discord.Embed()
                        round_3_check.add_field(name="Round 3 Results", value="\n".join([
                            f":brain: Content - {round_3_content_winner.mention}",
                            f":ocean: Flow - {round_3_flow_winner.mention}",
                            f":speaking_head: Delivery - {round_3_delivery_winner.mention}",
                        ]))
                        round_3_check_message = await ctx.send(embed=round_3_check)

                        await round_3_check_message.add_reaction("✅")
                        await round_3_check_message.add_reaction("❌")

                        round_3_check_reaction, round_3_check_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_check_reaction.emoji == "✅":
                            ok = True
                        else:
                            continue

            # ========================================================
            # JUDGES AND HOST 
            # ========================================================

            judge_embed = discord.Embed()
            judge_embed.add_field(name="Who are the judges for this match?", value="\n".join([
                "Mention the judges and put a space between each mention."
            ]))
            judge_message = await ctx.send(embed=judge_embed)

            judge_response = await self.bot.wait_for('message', check=msg_check)
            if judge_response.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")
            judges = []

            for judge in judge_response.content.split(" "):
                valid_judge = await get_member_info(ctx, judge)
                judges.append(valid_judge)

            host_embed = discord.Embed()
            host_embed.add_field(name="Who is the host for this match?", value="\n".join([
                "Acceptable inputs are: member ID, mention, or username"
            ]))
            host_message = await ctx.send(embed=host_embed)

            host_response = await self.bot.wait_for('message', check=msg_check)
            if host_response.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")
            host = await get_member_info(ctx, host_response.content)

            winner = {'who': challenger, 'ratio': (len(challenger_points), len(defender_points)), 'by': calling} if len(challenger_points) > len(defender_points) else {'who': defender, 'ratio': (len(defender_points), len(challenger_points)), 'by': calling}

            quote_embed = discord.Embed()
            quote_embed.add_field(name="What is the quote of the match winner?", value="Type the winner's quote in the chat please.")
            quote_message = await ctx.send(embed=quote_embed)

            winner_quote = await self.bot.wait_for('message', check=msg_check)
            if winner_quote.content.lower() == "cancel":
                return await ctx.send(f":ok_hand: Cancelled start match.")

            # ========================================================
            # DETERMINE THE CALL FOR THE MATCH
            # ========================================================

            majority_round_one = None
            majority_round_two = None
            majority_round_three = None
            defender_majorities = 0
            challenger_majorities = 0

            defender_round_ones = 0
            defender_round_twos = 0
            defender_round_threes = 0
        
            challenger_round_ones = 0
            challenger_round_twos = 0
            challenger_round_threes = 0

            for point in defender_points:

                if 'round 1' in point:
                    defender_round_ones += 1
                elif 'round 2' in point:
                    defender_round_twos += 1
                elif 'round 3' in point:
                    defender_round_threes += 1
                
            for point in challenger_points:

                if 'round 1' in point:
                    challenger_round_ones += 1
                elif 'round 2' in point:
                    challenger_round_twos += 1
                elif 'round 3' in point:
                    challenger_round_threes += 1
            
            if defender_round_ones > challenger_round_ones:
                majority_round_one = defender
                defender_majorities += 1
            if challenger_round_ones > defender_round_ones:
                majority_round_one = challenger
                challenger_majorities += 1
            
            if defender_round_twos > challenger_round_twos:
                majority_round_two = defender
                defender_majorities += 1
            if challenger_round_twos > defender_round_twos:
                majority_round_two = challenger
                challenger_majorities += 1

            if defender_round_threes > challenger_round_threes:
                majority_round_three = defender
                defender_majorities += 1
            if challenger_round_threes > defender_round_threes:
                majority_round_three = challenger
                challenger_majorities += 1

            calling = "Couldn't make the call."

            if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                calling = "Unanimous Decision"
            if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                calling = "KO"
            if defender_majorities >= 1 and challenger_majorities >= 1:
                calling = "Split Decision"

            round_1 = {
                "content": 'N/A',
                "flow": 'N/A',
                "delivery": 'N/A'
            }
            round_2 = {
                "content": 'N/A',
                "flow": 'N/A',
                "delivery": 'N/A'
            }
            round_3 = {
                "content": 'N/A',
                "flow": 'N/A',
                "delivery": 'N/A'
            }

            for point in defender_points:
                if 'round 1 content' in point:
                    round_1['content'] = defender.display_name
                elif 'round 1 flow' in point:
                    round_1['flow'] = defender.display_name
                elif 'round 1 delivery' in point:
                    round_1['delivery'] = defender.display_name
                elif 'round 2 content' in point:
                    round_2['content'] = defender.display_name
                elif 'round 2 flow' in point:
                    round_2['flow'] = defender.display_name
                elif 'round 2 delivery' in point:
                    round_2['delivery'] = defender.display_name
                elif 'round 3 content' in point:
                    round_3['content'] = defender.display_name
                elif 'round 3 flow' in point:
                    round_3['flow'] = defender.display_name
                elif 'round 3 delivery' in point:
                    round_3['delivery'] = defender.display_name

            for point in challenger_points:
                if 'round 1 content' in point:
                    round_1['content'] = challenger.display_name
                elif 'round 1 flow' in point:
                    round_1['flow'] = challenger.display_name
                elif 'round 1 delivery' in point:
                    round_1['delivery'] = challenger.display_name
                elif 'round 2 content' in point:
                    round_2['content'] = challenger.display_name
                elif 'round 2 flow' in point:
                    round_2['flow'] = challenger.display_name
                elif 'round 2 delivery' in point:
                    round_2['delivery'] = challenger.display_name
                elif 'round 3 content' in point:
                    round_3['content'] = challenger.display_name
                elif 'round 3 flow' in point:
                    round_3['flow'] = challenger.display_name
                elif 'round 3 delivery' in point:
                    round_3['delivery'] = challenger.display_name

            judge_formatted = " ".join([judge.mention for judge in judges])
            
            bout_embed = discord.Embed()
            bout_embed.title = "TFC Title Match Conclusion"
            bout_embed.description = "\n".join([
                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                "",
                f"Host: {host.mention}",
                f"Judges: {judge_formatted}",
                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
            ])
            bout_embed.add_field(name="Round 1", value="\n".join([
                f"Content: {round_1['content']}",
                f"Flow: {round_1['flow']}",
                f"Delivery: {round_1['delivery']}",
            ]), inline=False)
            bout_embed.add_field(name=f"Round 2", value="\n".join([
                f"Content: {round_2['content']}",
                f"Flow: {round_2['flow']}",
                f"Delivery: {round_2['delivery']}",
            ]), inline=False)
            bout_embed.add_field(name=f"Round 3", value="\n".join([
                f"Content: {round_3['content']}",
                f"Flow: {round_3['flow']}",
                f"Delivery: {round_3['delivery']}",
            ]), inline=False)
            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
            bout_message = await ctx.send(embed=bout_embed)

            await bout_message.add_reaction("✅")
            await bout_message.add_reaction("❌")

            bouts = server.get_channel(777650383769960469)

            bout_reaction, bout_user = await self.bot.wait_for('reaction_add', check=reaction_check)
            if bout_reaction.emoji == "✅":
                await bouts.send(embed=bout_embed)
                await ctx.send(":ok_hand:")
            else:
                editting = True
                while editting is True:
                    embed = discord.Embed()
                    embed.add_field(name="What would you like to change?", value="\n".join([
                        f":one: Round One",
                        f":two: Round Two",
                        f":three: Round Three",
                        f":four: Host",
                        f":five: Judges",
                        f":six: Winner Quote",
                        f":x: Cancel Edit (send in #bouts)"
                    ]))
                    msg = await ctx.send(embed=embed)

                    await msg.add_reaction("1️⃣")
                    await msg.add_reaction("2️⃣")
                    await msg.add_reaction("3️⃣")
                    await msg.add_reaction("4️⃣")
                    await msg.add_reaction("5️⃣")
                    await msg.add_reaction("6️⃣")
                    await msg.add_reaction("❌")

                    edit_reaction, edit_user = await self.bot.wait_for('reaction_add', check=reaction_check)

                    if edit_reaction.emoji == "6️⃣":
                        quote_embed = discord.Embed()
                        quote_embed.add_field(name="What is the quote of the match winner?", value="Type the winner's quote in the chat please.")
                        quote_message = await ctx.send(embed=quote_embed)

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":
                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Title Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue

                    elif edit_reaction.emoji == "4️⃣":
                        host_embed = discord.Embed()
                        host_embed.add_field(name="Who is the host for this match?", value="\n".join([
                            "Acceptable inputs are: member ID, mention, or username"
                        ]))
                        host_message = await ctx.send(embed=host_embed)

                        host_response = await self.bot.wait_for('message', check=msg_check)
                        host = await get_member_info(ctx, host_response.content)

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":
                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Regular Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "5️⃣":
                        judge_embed = discord.Embed()
                        judge_embed.add_field(name="Who are the judges for this match?", value="\n".join([
                            "Mention the judges and put a space between each mention."
                        ]))
                        judge_message = await ctx.send(embed=judge_embed)

                        judge_response = await self.bot.wait_for('message', check=msg_check)
                        judges = []

                        for judge in judge_response.content.split(" "):
                            valid_judge = await get_member_info(ctx, judge)
                            judges.append(valid_judge)

                        judge_formatted = " ".join([judge.mention for judge in judges])

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":
                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Title Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "1️⃣":

                        majority_round_one = None
                        majority_round_two = None
                        majority_round_three = None
                        defender_majorities = 0
                        challenger_majorities = 0

                        defender_round_ones = 0
                        defender_round_twos = 0
                        defender_round_threes = 0
                    
                        challenger_round_ones = 0
                        challenger_round_twos = 0
                        challenger_round_threes = 0

                        for point in defender_points:

                            if 'round 1' in point:
                                defender_round_ones += 1
                            elif 'round 2' in point:
                                defender_round_twos += 1
                            elif 'round 3' in point:
                                defender_round_threes += 1
                            
                        for point in challenger_points:

                            if 'round 1' in point:
                                challenger_round_ones += 1
                            elif 'round 2' in point:
                                challenger_round_twos += 1
                            elif 'round 3' in point:
                                challenger_round_threes += 1
                        
                        if defender_round_ones > challenger_round_ones:
                            majority_round_one = defender
                            defender_majorities += 1
                        if challenger_round_ones > defender_round_ones:
                            majority_round_one = challenger
                            challenger_majorities += 1
                        
                        if defender_round_twos > challenger_round_twos:
                            majority_round_two = defender
                            defender_majorities += 1
                        if challenger_round_twos > defender_round_twos:
                            majority_round_two = challenger
                            challenger_majorities += 1

                        if defender_round_threes > challenger_round_threes:
                            majority_round_three = defender
                            defender_majorities += 1
                        if challenger_round_threes > defender_round_threes:
                            majority_round_three = challenger
                            challenger_majorities += 1

                        calling = "Couldn't make the call."

                        if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                            calling = "Unanimous Decision"
                        if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                            calling = "KO"
                        if defender_majorities >= 1 and challenger_majorities >= 1:
                            calling = "Split Decision"

                        winner = {'who': challenger, 'ratio': (len(challenger_points), len(defender_points)), 'by': calling} if len(challenger_points) > len(defender_points) else {'who': defender, 'ratio': (len(defender_points), len(challenger_points)), 'by': calling}

                        # ========================================================
                        # ROUND 1 INFORMATION
                        # ========================================================
                        # ROUND 1 CONTENT
                        # ========================================================

                        for point in defender_points:
                            if 'round 1' in point:
                                defender_points.remove(point)
                            
                        for point in challenger_points:
                            if 'round 1' in point:
                                challenger_points.remove(point)

                        round_1_content_embed = discord.Embed()
                        round_1_content_embed.add_field(name="Who won round one content?", value=f"\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_1_content_message = await ctx.send(embed=round_1_content_embed)

                        await round_1_content_message.add_reaction("1️⃣")
                        await round_1_content_message.add_reaction("2️⃣")

                        round_1_content_reaction, round_1_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_1_content_reaction.emoji == "1️⃣":
                            round_1_content_winner = defender
                            defender_points.append('round 1 content')
                        elif round_1_content_reaction.emoji == "2️⃣":
                            round_1_content_winner = challenger
                            challenger_points.append('round 1 content')

                        # ========================================================
                        # ROUND 1 FLOW
                        # ========================================================

                        round_1_flow_embed = discord.Embed()
                        round_1_flow_embed.add_field(name="Who won round one flow?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_1_flow_message = await ctx.send(embed=round_1_flow_embed)

                        await round_1_flow_message.add_reaction("1️⃣")
                        await round_1_flow_message.add_reaction("2️⃣")

                        round_1_flow_reaction, round_1_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_1_flow_reaction.emoji == "1️⃣":
                            round_1_flow_winner = defender
                            defender_points.append('round 1 flow')
                        elif round_1_flow_reaction.emoji == "2️⃣":
                            round_1_flow_winner = challenger
                            challenger_points.append('round 1 flow')

                        # ========================================================
                        # ROUND 1 DELIVERY
                        # ========================================================

                        round_1_delivery_embed = discord.Embed()
                        round_1_delivery_embed.add_field(name="Who won round one delivery?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_1_delivery_message = await ctx.send(embed=round_1_delivery_embed)

                        await round_1_delivery_message.add_reaction("1️⃣")
                        await round_1_delivery_message.add_reaction("2️⃣")

                        round_1_delivery_reaction, round_1_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_1_delivery_reaction.emoji == "1️⃣":
                            round_1_delivery_winner = defender
                            defender_points.append('round 1 delivery')
                        elif round_1_delivery_reaction.emoji == "2️⃣":
                            round_1_delivery_winner = challenger
                            challenger_points.append('round 1 delivery')

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":

                            round_1 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_2 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_3 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }

                            for point in defender_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = defender.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = defender.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = defender.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = defender.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = defender.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = defender.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = defender.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = defender.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = defender.display_name

                            for point in challenger_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = challenger.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = challenger.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = challenger.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = challenger.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = challenger.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = challenger.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = challenger.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = challenger.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = challenger.display_name

                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Title Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "2️⃣":

                        majority_round_one = None
                        majority_round_two = None
                        majority_round_three = None
                        defender_majorities = 0
                        challenger_majorities = 0

                        defender_round_ones = 0
                        defender_round_twos = 0
                        defender_round_threes = 0
                    
                        challenger_round_ones = 0
                        challenger_round_twos = 0
                        challenger_round_threes = 0

                        for point in defender_points:

                            if 'round 1' in point:
                                defender_round_ones += 1
                            elif 'round 2' in point:
                                defender_round_twos += 1
                            elif 'round 3' in point:
                                defender_round_threes += 1
                            
                        for point in challenger_points:

                            if 'round 1' in point:
                                challenger_round_ones += 1
                            elif 'round 2' in point:
                                challenger_round_twos += 1
                            elif 'round 3' in point:
                                challenger_round_threes += 1
                        
                        if defender_round_ones > challenger_round_ones:
                            majority_round_one = defender
                            defender_majorities += 1
                        if challenger_round_ones > defender_round_ones:
                            majority_round_one = challenger
                            challenger_majorities += 1
                        
                        if defender_round_twos > challenger_round_twos:
                            majority_round_two = defender
                            defender_majorities += 1
                        if challenger_round_twos > defender_round_twos:
                            majority_round_two = challenger
                            challenger_majorities += 1

                        if defender_round_threes > challenger_round_threes:
                            majority_round_three = defender
                            defender_majorities += 1
                        if challenger_round_threes > defender_round_threes:
                            majority_round_three = challenger
                            challenger_majorities += 1

                        calling = "Couldn't make the call."

                        if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                            calling = "Unanimous Decision"
                        if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                            calling = "KO"
                        if defender_majorities >= 1 and challenger_majorities >= 1:
                            calling = "Split Decision"

                        winner = {'who': challenger, 'ratio': (len(challenger_points), len(defender_points)), 'by': calling} if len(challenger_points) > len(defender_points) else {'who': defender, 'ratio': (len(defender_points), len(challenger_points)), 'by': calling}

                        # ========================================================
                        # ROUND 2 INFORMATION
                        # ========================================================
                        # ROUND 2 CONTENT
                        # ========================================================

                        for point in defender_points:
                            if 'round 2' in point:
                                defender_points.remove(point)
                            
                        for point in challenger_points:
                            if 'round 2' in point:
                                challenger_points.remove(point)

                        round_2_content_embed = discord.Embed()
                        round_2_content_embed.add_field(name="Who won round two content?", value=f"\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_2_content_message = await ctx.send(embed=round_2_content_embed)

                        await round_2_content_message.add_reaction("1️⃣")
                        await round_2_content_message.add_reaction("2️⃣")

                        round_2_content_reaction, round_2_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_2_content_reaction.emoji == "1️⃣":
                            round_2_content_winner = defender
                            defender_points.append('round 2 content')
                        elif round_2_content_reaction.emoji == "2️⃣":
                            round_2_content_winner = challenger
                            challenger_points.append('round 2 content')

                        # ========================================================
                        # ROUND 1 FLOW
                        # ========================================================

                        round_2_flow_embed = discord.Embed()
                        round_2_flow_embed.add_field(name="Who won round two flow?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_2_flow_message = await ctx.send(embed=round_2_flow_embed)

                        await round_2_flow_message.add_reaction("1️⃣")
                        await round_2_flow_message.add_reaction("2️⃣")

                        round_2_flow_reaction, round_2_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_2_flow_reaction.emoji == "1️⃣":
                            round_2_flow_winner = defender
                            defender_points.append('round 2 flow')
                        elif round_2_flow_reaction.emoji == "2️⃣":
                            round_2_flow_winner = challenger
                            challenger_points.append('round 2 flow')

                        # ========================================================
                        # ROUND 2 DELIVERY
                        # ========================================================

                        round_2_delivery_embed = discord.Embed()
                        round_2_delivery_embed.add_field(name="Who won round two delivery?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_2_delivery_message = await ctx.send(embed=round_2_delivery_embed)

                        await round_2_delivery_message.add_reaction("1️⃣")
                        await round_2_delivery_message.add_reaction("2️⃣")

                        round_2_delivery_reaction, round_2_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_2_delivery_reaction.emoji == "1️⃣":
                            round_2_delivery_winner = defender
                            defender_points.append('round 2 delivery')
                        elif round_2_delivery_reaction.emoji == "2️⃣":
                            round_2_delivery_winner = challenger
                            challenger_points.append('round 2 delivery')

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":

                            round_1 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_2 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_3 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }

                            for point in defender_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = defender.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = defender.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = defender.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = defender.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = defender.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = defender.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = defender.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = defender.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = defender.display_name

                            for point in challenger_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = challenger.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = challenger.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = challenger.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = challenger.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = challenger.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = challenger.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = challenger.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = challenger.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = challenger.display_name

                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Title Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "3️⃣":

                        majority_round_one = None
                        majority_round_two = None
                        majority_round_three = None
                        defender_majorities = 0
                        challenger_majorities = 0

                        defender_round_ones = 0
                        defender_round_twos = 0
                        defender_round_threes = 0
                    
                        challenger_round_ones = 0
                        challenger_round_twos = 0
                        challenger_round_threes = 0

                        for point in defender_points:

                            if 'round 1' in point:
                                defender_round_ones += 1
                            elif 'round 2' in point:
                                defender_round_twos += 1
                            elif 'round 3' in point:
                                defender_round_threes += 1
                            
                        for point in challenger_points:

                            if 'round 1' in point:
                                challenger_round_ones += 1
                            elif 'round 2' in point:
                                challenger_round_twos += 1
                            elif 'round 3' in point:
                                challenger_round_threes += 1
                        
                        if defender_round_ones > challenger_round_ones:
                            majority_round_one = defender
                            defender_majorities += 1
                        if challenger_round_ones > defender_round_ones:
                            majority_round_one = challenger
                            challenger_majorities += 1
                        
                        if defender_round_twos > challenger_round_twos:
                            majority_round_two = defender
                            defender_majorities += 1
                        if challenger_round_twos > defender_round_twos:
                            majority_round_two = challenger
                            challenger_majorities += 1

                        if defender_round_threes > challenger_round_threes:
                            majority_round_three = defender
                            defender_majorities += 1
                        if challenger_round_threes > defender_round_threes:
                            majority_round_three = challenger
                            challenger_majorities += 1

                        calling = "Couldn't make the call."

                        if defender_round_ones == 2 and defender_round_twos == 2 and defender_round_threes == 2 or challenger_round_ones == 2 and challenger_round_twos == 2 and challenger_round_threes == 2:
                            calling = "Unanimous Decision"
                        if defender_round_ones + defender_round_twos >= 5 or challenger_round_ones + challenger_round_twos >= 5:
                            calling = "KO"
                        if defender_majorities >= 1 and challenger_majorities >= 1:
                            calling = "Split Decision"

                        winner = {'who': challenger, 'ratio': (len(challenger_points), len(defender_points)), 'by': calling} if len(challenger_points) > len(defender_points) else {'who': defender, 'ratio': (len(defender_points), len(challenger_points)), 'by': calling}

                        # ========================================================
                        # ROUND 2 INFORMATION
                        # ========================================================
                        # ROUND 2 CONTENT
                        # ========================================================

                        for point in defender_points:
                            if 'round 3' in point:
                                defender_points.remove(point)
                            
                        for point in challenger_points:
                            if 'round 3' in point:
                                challenger_points.remove(point)

                        round_3_content_embed = discord.Embed()
                        round_3_content_embed.add_field(name="Who won round three content?", value=f"\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_3_content_message = await ctx.send(embed=round_3_content_embed)

                        await round_3_content_message.add_reaction("1️⃣")
                        await round_3_content_message.add_reaction("2️⃣")

                        round_3_content_reaction, round_3_content_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_content_reaction.emoji == "1️⃣":
                            round_3_content_winner = defender
                            defender_points.append('round 3 content')
                        elif round_3_content_reaction.emoji == "2️⃣":
                            round_3_content_winner = challenger
                            challenger_points.append('round 3 content')

                        # ========================================================
                        # ROUND 3 FLOW
                        # ========================================================

                        round_3_flow_embed = discord.Embed()
                        round_3_flow_embed.add_field(name="Who won round three flow?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_3_flow_message = await ctx.send(embed=round_3_flow_embed)

                        await round_3_flow_message.add_reaction("1️⃣")
                        await round_3_flow_message.add_reaction("2️⃣")

                        round_3_flow_reaction, round_3_flow_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_flow_reaction.emoji == "1️⃣":
                            round_3_flow_winner = defender
                            defender_points.append('round 3 flow')
                        elif round_3_flow_reaction.emoji == "2️⃣":
                            round_3_flow_winner = challenger
                            challenger_points.append('round 3 flow')

                        # ========================================================
                        # ROUND 3 DELIVERY
                        # ========================================================

                        round_3_delivery_embed = discord.Embed()
                        round_3_delivery_embed.add_field(name="Who won round three delivery?", value="\n".join([
                            f":one: Defender: {defender.mention}",
                            f":two: Challenger: {challenger.mention}"
                        ]))
                        round_3_delivery_message = await ctx.send(embed=round_3_delivery_embed)

                        await round_3_delivery_message.add_reaction("1️⃣")
                        await round_3_delivery_message.add_reaction("2️⃣")

                        round_3_delivery_reaction, round_3_delivery_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if round_3_delivery_reaction.emoji == "1️⃣":
                            round_3_delivery_winner = defender
                            defender_points.append('round 3 delivery')
                        elif round_3_delivery_reaction.emoji == "2️⃣":
                            round_3_delivery_winner = challenger
                            challenger_points.append('round 3 delivery')

                        all_embed = discord.Embed()
                        all_embed.add_field(name="Successfully Edited", value="Is that all?")
                        all_message = await ctx.send(embed=all_embed)

                        await all_message.add_reaction("✅")
                        await all_message.add_reaction("❌")

                        confirmation_reaction, confirmation_user = await self.bot.wait_for('reaction_add', check=reaction_check)
                        if confirmation_reaction.emoji == "✅":

                            round_1 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_2 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }
                            round_3 = {
                                "content": 'N/A',
                                "flow": 'N/A',
                                "delivery": 'N/A'
                            }

                            for point in defender_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = defender.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = defender.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = defender.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = defender.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = defender.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = defender.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = defender.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = defender.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = defender.display_name

                            for point in challenger_points:
                                if 'round 1 content' in point:
                                    round_1['content'] = challenger.display_name
                                elif 'round 1 flow' in point:
                                    round_1['flow'] = challenger.display_name
                                elif 'round 1 delivery' in point:
                                    round_1['delivery'] = challenger.display_name
                                elif 'round 2 content' in point:
                                    round_2['content'] = challenger.display_name
                                elif 'round 2 flow' in point:
                                    round_2['flow'] = challenger.display_name
                                elif 'round 2 delivery' in point:
                                    round_2['delivery'] = challenger.display_name
                                elif 'round 3 content' in point:
                                    round_3['content'] = challenger.display_name
                                elif 'round 3 flow' in point:
                                    round_3['flow'] = challenger.display_name
                                elif 'round 3 delivery' in point:
                                    round_3['delivery'] = challenger.display_name

                            await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                            editting = False
                            bout_embed = discord.Embed()
                            bout_embed.title = "TFC Title Match Conclusion"
                            bout_embed.description = "\n".join([
                                f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                                "",
                                f"Host: {host.mention}",
                                f"Judges: {judge_formatted}",
                                f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                            ])
                            bout_embed.add_field(name="Round 1", value="\n".join([
                                f"Content: {round_1['content']}",
                                f"Flow: {round_1['flow']}",
                                f"Delivery: {round_1['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 2", value="\n".join([
                                f"Content: {round_2['content']}",
                                f"Flow: {round_2['flow']}",
                                f"Delivery: {round_2['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name=f"Round 3", value="\n".join([
                                f"Content: {round_3['content']}",
                                f"Flow: {round_3['flow']}",
                                f"Delivery: {round_3['delivery']}",
                            ]), inline=False)
                            bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                            bout_message = await bouts.send(embed=bout_embed)
                        else:
                            continue
                    elif edit_reaction.emoji == "❌":

                        await ctx.send(f":white_check_mark: Embed has been sent to the bouts channel and the stats have been added to the members.")
                        editting = False
                        bout_embed = discord.Embed()
                        bout_embed.title = "TFC Regular Match Conclusion"
                        bout_embed.description = "\n".join([
                            f"{defender.mention} {defender_most_previous} VS {challenger.mention} {challenger_most_previous}",
                            "",
                            f"Host: {host.mention}",
                            f"Judges: {judge_formatted}",
                            f"Winner {winner['ratio'][0]}-{winner['ratio'][1]} by **{winner['by']}** : {winner['who'].mention}",
                        ])
                        bout_embed.add_field(name="Round 1", value="\n".join([
                            f"Content: {round_1['content']}",
                            f"Flow: {round_1['flow']}",
                            f"Delivery: {round_1['delivery']}",
                        ]), inline=False)
                        bout_embed.add_field(name=f"Round 2", value="\n".join([
                            f"Content: {round_2['content']}",
                            f"Flow: {round_2['flow']}",
                            f"Delivery: {round_2['delivery']}",
                        ]), inline=False)
                        bout_embed.add_field(name=f"Round 3", value="\n".join([
                            f"Content: {round_3['content']}",
                            f"Flow: {round_3['flow']}",
                            f"Delivery: {round_3['delivery']}",
                        ]), inline=False)
                        bout_embed.add_field(name="Quote", value=f'"{winner_quote.content}" - {winner["who"].display_name}', inline=False)
                        bout_message = await bouts.send(embed=bout_embed)
            
            previous_matches = await ctx.fetch("SELECT * FROM matches WHERE guild_id=$1", server.id)
            bout_id = len(previous_matches) if previous_matches else 0

            defender_id = defender.id
            challenger_id = challenger.id
            judges = [judge.id for judge in judges]
            host_id = host.id
            winner_id = winner['who'].id
            loser_id = defender.id if winner['who'].id == challenger.id else challenger.id
            ratio = [winner['ratio'][0], winner['ratio'][1]]
            decision = calling
            defender_category_wins = defender_points
            defender_category_losses = challenger_points
            challenger_category_wins = challenger_points
            challenger_category_losses = defender_points
            match_type = 'title'

            await ctx.execute("""
            INSERT INTO matches (
                guild_id,
                bout_id,
                defender_id,
                challenger_id,
                judges,
                host_id,
                winner_id,
                loser_id,
                ratio,
                decision,
                defender_category_wins,
                defender_category_losses,
                challenger_category_wins,
                challenger_category_losses,
                match_type,
                inserted_at,
                winner_quote
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                $11, $12, $13, $14, $15, $16, $17
            )
            """, server.id, bout_id+1, defender_id, challenger_id, judges, host_id, winner_id, loser_id, ratio, decision, defender_category_wins, defender_category_losses, challenger_category_wins, challenger_category_losses, match_type, datetime.datetime.utcnow(), winner_quote.content)
            
        elif starting_reaction.emoji == "❌":
            await ctx.send(f":ok_hand: Cancelled match startup.")
            return

def setup(bot):
    bot.add_cog(Matches(bot))