import discord
from discord.ext import commands
from models import GameState, Killer, Survivor, Character, Alias
from sqlalchemy.orm import joinedload
from PIL import Image, ImageDraw
from sqlalchemy import func


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
            and not message.content.startswith('_')
            and message.channel == self.game_state.thread
        ):
            print(message.content)
            comparison = self.compare_characters(message.content)
            character_name = comparison.pop('character_name', None)
            await message.channel.send(**comparison)
            if character_name:
                if self.game_state.guess(character_name):
                    await message.channel.send(
                        f"{message.author.nick if message.author.nick else message.author.display_name} "
                        f"guessed correct!\nIt took {self.game_state.attempts} attempts"
                    )
                    await self.game_state.stop_game()

    @commands.command()
    async def guess_classic(self, ctx):
        print(ctx.message.content)
        if not self.game_state.is_game_active:
            self.game_state.start_game()
            thread = await ctx.channel.create_thread(
                name="Guess Classic", type=discord.ChannelType.public_thread
            )
            self.game_state.thread = thread
        else:
            await ctx.send("A game is already ongoing")

    def compare_characters(self, character_name):
        survivor_query = self.bot.session.query(None)
        killer_query = self.bot.session.query(None)
        if self.game_state.game_type == GameState.SURVIVOR or self.game_state.game_type == GameState.RANDOM:
            survivor_query = (
                self.bot.session.query(Survivor)
                .options(
                    joinedload(Survivor.perks),
                    joinedload(Survivor.aliases),
                )
                .filter(func.lower(Survivor.name).contains(func.lower(character_name))).union(
                    self.bot.session.query(Survivor).join(Alias).filter(func.lower(Alias.title)
                                                                        .contains(func.lower(character_name)))
                )
            )
        if self.game_state.game_type == GameState.KILLER or self.game_state.game_type == GameState.RANDOM:
            killer_query = (
                self.bot.session.query(Killer)
                .options(
                    joinedload(Killer.perks),
                    joinedload(Killer.aliases),
                    joinedload(Killer.terror_radius),
                )
                .filter(func.lower(Killer.name).contains(func.lower(character_name))).union(
                    self.bot.session.query(Killer).join(Alias).filter(func.lower(Alias.title)
                                                                      .contains(func.lower(character_name)))
                )
            )

        character = survivor_query.union(killer_query)
        if character.count() > 1:
            return {'content': 'Your guess returned too many characters, please be more specific'}
        character = character.first()
        if character:
            self.compare_attribute(
                character.gender, self.game_state.character.gender, 'gender'
            )
            self.compare_attribute(
                character.origin, self.game_state.character.origin, 'origin'
            )
            self.compare_dates(
                character.release_date, self.game_state.character.release_date, 'release_date'
            )
            self.compare_attribute(
                character.licence, self.game_state.character.licence, 'license'
            )
            return {
                'content': character.name,
                'character_name': character.name,
                'files': [
                    discord.File('images/classic/gender.png'),
                    discord.File('images/classic/origin.png'),
                    discord.File('images/classic/release_date.png'),
                    discord.File('images/classic/license.png'),
                ]
            }
        else:
            return {'content': "No character with such name, no attempt counted"}

    def compare_attribute(self, character_attribute, correct_character_attribute, filename):
        if character_attribute == correct_character_attribute:
            self.create_box(self.GREEN, character_attribute, filename)
        else:
            self.create_box(self.RED, character_attribute, filename)

    def compare_dates(self, character_date, correct_character_date, filename):
        if character_date < correct_character_date:
            self.create_box(self.RED, str(character_date), filename, 'lt')
        elif character_date > correct_character_date:
            self.create_box(self.RED, str(character_date), filename, 'gt')
        else:
            self.create_box(self.GREEN, str(character_date), filename)

    @staticmethod
    def create_box(color, attribute, filename, arrow=None):
        width, height = (198, 219)
        if arrow == 'gt':
            img = Image.open('images/classic/templates/arrow_down.png')
        elif arrow == 'lt':
            img = Image.open('images/classic/templates/arrow_up.png')
        else:
            img = Image.new('RGB', (width, height), color=color)

        draw = ImageDraw.Draw(img)
        draw.text((100, 100), attribute, fill=(0, 0, 0), align='center', anchor='mm', font_size=25)
        img.save('images/classic/' + filename + '.png')


async def setup(bot):
    await bot.add_cog(Classic(bot))
