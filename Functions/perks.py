import discord
from discord.ext import commands

from models import Alias, GameState, Killer, Survivor


class PerkGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_state = GameState(bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            self.game_state.is_game_active
            and not message.author.bot
            and message.channel == self.game_state.thread
        ):
            if message.content == "give_up":
                perks = [
                    f"{x.name}: {x.popularity}%"
                    for x in self.game_state.character.perks
                ]
                await message.channel.send(
                    f"You guessed {self.game_state.attempts} times.\n"
                    f"The correct answer was: {self.game_state.character.name}\n"
                    f"with the perks: {', '.join(perks)}"
                )
                await self.game_state.stop_game()
                return
            print(message.content)
            characters = self.game_state.find_character(message.content)
            if characters.count() > 1:
                await message.channel.send(
                    "Your guess returned too many characters, please be more specific"
                )
            character = characters.first()
            if character:
                if self.game_state.guess(character.name):
                    perks = [
                        f"{x.name}: {x.popularity}%"
                        for x in self.game_state.character.perks
                    ]
                    await message.channel.send(
                        f"{message.author.nick if message.author.nick else message.author.display_name} "
                        f"guessed correct!\nIt took {self.game_state.attempts} attempts\n"
                        f"the perks were: {', '.join(perks)}"
                    )
                    await self.game_state.stop_game()
                else:
                    await message.channel.send(
                        f"{character.name} was not the correct answer."
                    )
            else:
                await message.channel.send(
                    "No character with such name, no attempt counted"
                )

    @commands.command()
    async def guess_perks(self, ctx, game_type=GameState.RANDOM):
        if game_type.lower().startswith("k"):
            game_type = GameState.KILLER
        elif game_type.lower().startswith("s"):
            game_type = GameState.SURVIVOR
        else:
            game_type = GameState.RANDOM
        if not self.game_state.is_game_active:
            self.game_state.start_game(game_type=game_type)
            thread = await ctx.channel.create_thread(
                name="Guess Perk Popularity", type=discord.ChannelType.public_thread
            )
            await thread.send("Type `give_up` in this thread to give up")
            perks_popularity = [
                str(x.popularity) + "%" for x in self.game_state.character.perks
            ]
            await thread.send(
                f"{type(self.game_state.character).__name__} with perk pick rates: {', '.join(perks_popularity)}"
            )
            self.game_state.thread = thread


async def setup(bot):
    await bot.add_cog(PerkGame(bot))
