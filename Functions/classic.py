import discord
from discord.ext import commands
from PIL import Image, ImageDraw
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from models import Alias, GameState, Killer, Survivor


class Classic(commands.Cog):
    GREEN = (9, 193, 46)
    YELLOW = (217, 126, 11)
    RED = (218, 21, 15)

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
            if message.content == 'give_up':
                await message.channel.send(f"You guessed {self.game_state.attempts} times.\n"
                                           f"The correct answer was: {self.game_state.character.name}")
                await self.game_state.stop_game()
                return
            print(message.content)
            comparison = self.compare_characters(message.content)
            character_name = comparison.pop("character_name", None)
            await message.channel.send(**comparison)
            if character_name:
                if self.game_state.guess(character_name):
                    await message.channel.send(
                        f"{message.author.nick if message.author.nick else message.author.display_name} "
                        f"guessed correct!\nIt took {self.game_state.attempts} attempts"
                    )
                    await self.game_state.stop_game()

    @commands.command()
    async def guess_classic(self, ctx, game_type=GameState.RANDOM):
        print(ctx.message.content)
        if game_type.lower().startswith("k"):
            game_type = GameState.KILLER
        elif game_type.lower().startswith("s"):
            game_type = GameState.SURVIVOR
        else:
            game_type = GameState.RANDOM
        if not self.game_state.is_game_active:
            self.game_state.start_game(game_type=game_type)
            thread = await ctx.channel.create_thread(
                name="Guess Classic", type=discord.ChannelType.public_thread,
            )
            await thread.send("Type `give_up` in this thread to give up")
            self.game_state.thread = thread
        else:
            await ctx.send("A game is already ongoing")

    def compare_characters(self, character_name):
        characters = self.game_state.find_character(character_name)
        if characters.count() > 1:
            return {
                "content": "Your guess returned too many characters, please be more specific"
            }
        character = characters.first()
        if character:
            self.compare_attribute(
                character.gender, self.game_state.character.gender, "gender"
            )
            self.compare_attribute(
                character.origin, self.game_state.character.origin, "origin"
            )
            self.compare_comparable(
                character.release_date,
                self.game_state.character.release_date,
                "release date",
            )
            self.compare_attribute(
                character.license, self.game_state.character.license, "license"
            )
            files = [
                discord.File("images/classic/gender.png"),
                discord.File("images/classic/origin.png"),
                discord.File("images/classic/release date.png"),
                discord.File("images/classic/license.png"),
            ]
            if self.game_state.game_type == self.game_state.KILLER:
                self.compare_comparable(
                    character.terror_radius.speed,
                    self.game_state.character.terror_radius.speed,
                    "speed",
                )
                self.compare_attribute(
                    character.terror_radius.default_range,
                    self.game_state.character.terror_radius.default_range,
                    "terror radius range",
                )
                files += [
                    discord.File("images/classic/speed.png"),
                    discord.File("images/classic/terror radius range.png"),
                ]
            return {
                "content": character.name,
                "character_name": character.name,
                "files": files,
            }
        else:
            return {"content": "No character with such name, no attempt counted"}

    def compare_attribute(
        self, character_attribute, correct_character_attribute, filename
    ):
        if character_attribute == correct_character_attribute:
            self.create_box(self.GREEN, character_attribute, filename)
        else:
            self.create_box(self.RED, character_attribute, filename)

    def compare_comparable(self, character_data, correct_character_data, filename):
        if character_data < correct_character_data:
            self.create_box(self.RED, str(character_data), filename, "lt")
        elif character_data > correct_character_data:
            self.create_box(self.RED, str(character_data), filename, "gt")
        else:
            self.create_box(self.GREEN, str(character_data), filename)

    @staticmethod
    def create_box(color, attribute, filename, arrow=None):
        width, height = (198, 219)
        if arrow == "gt":
            img = Image.open("images/classic/templates/arrow_down.png")
        elif arrow == "lt":
            img = Image.open("images/classic/templates/arrow_up.png")
        else:
            img = Image.new("RGB", (width, height), color=color)

        draw = ImageDraw.Draw(img)
        draw.text(
            (100, 100),
            f"{filename}\n{attribute}",
            fill=(0, 0, 0),
            align="center",
            anchor="mm",
            font_size=25,
        )
        img.save("images/classic/" + filename + ".png")


async def setup(bot):
    await bot.add_cog(Classic(bot))
