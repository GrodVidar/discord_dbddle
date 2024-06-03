import random
import urllib.request

from PIL import Image
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String, Table,
                        func, Date)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, joinedload, reconstructor, relationship
import random
import re

Base = declarative_base()


class Character(Base):
    __abstract__ = True
    pk = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    origin = Column(String)
    release_date = Column(Date)
    licence = Column(String)

    def __init__(self, name, gender, origin, release_date, licence, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.gender = gender
        self.origin = origin
        self.release_date = release_date
        self.licence = licence


    @staticmethod
    def get_random_character(session, random_type=True):
        if random_type:
            is_survivor = bool(random.getrandbits(1))
            if is_survivor:
                character = Character.get_random_survivor(session)
            else:
                character = Character.get_random_killer(session)
            return is_survivor, character

    @staticmethod
    def get_random_killer(session):
        return (
            session.query(Killer)
            .options(
                joinedload(Killer.aliases),
                joinedload(Killer.perks),
                joinedload(Killer.terror_radius)
            )
            .order_by(func.random())
            .first()
        )

    @staticmethod
    def get_random_survivor(session):
        return (
            session.query(Survivor)
            .options(
                joinedload(Survivor.aliases),
                joinedload(Survivor.perks)
            )
            .order_by(func.random())
            .first()
        )


class Survivor(Character):
    __tablename__ = 'survivor'
    aliases = relationship("Alias", secondary=None, back_populates='survivor')
    perks = relationship('Perk', secondary=None, back_populates='survivor')

    def __init__(self, aliases, perks, **kwargs):
        super().__init__(**kwargs)
        self.aliases = [Alias(title=title) for title in aliases]
        self.perks = perks


class Killer(Character):
    __tablename__ = 'killer'
    aliases = relationship("Alias", secondary=None, back_populates='killer')
    perks = relationship('Perk', secondary=None, back_populates='killer')
    terror_radius = relationship('TerrorRadius', secondary=None, back_populates='killer', uselist=False)

    def __init__(self, aliases, perks, terror_radius, **kwargs):
        super().__init__(**kwargs)
        self.aliases = [Alias(title=title) for title in aliases]
        self.perks = perks
        self.terror_radius = terror_radius


class Alias(Base):
    __tablename__ = 'alias'
    pk = Column(Integer, primary_key=True)
    title = Column(String)
    survivor_id = Column(Integer, ForeignKey('survivor.pk'))
    survivor = relationship('Survivor', back_populates='aliases')
    killer_id = Column(Integer, ForeignKey('killer.pk'))
    killer = relationship('Killer', back_populates='aliases')


class Perk(Base):
    __tablename__ = 'perk'
    pk = Column(Integer, primary_key=True)
    name = Column(String)
    image_url = Column(String)
    survivor_id = Column(Integer, ForeignKey('survivor.pk'))
    survivor = relationship('Survivor', back_populates='perks')
    killer_id = Column(Integer, ForeignKey('killer.pk'))
    killer = relationship('Killer', back_populates='perks')

    def __init__(self, name, image_url, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.image_url = image_url


class TerrorRadius(Base):
    __tablename__ = 'terror_radius'
    pk = Column(Integer, primary_key=True)
    default_range = Column(Integer)
    sound = Column(String)
    killer_id = Column(Integer, ForeignKey('killer.pk'), unique=True)
    killer = relationship('Killer', back_populates='terror_radius', uselist=False)

    def __init__(self, sound, default_range, **kwargs):
        super().__init__(**kwargs)
        self.sound = sound
        self.default_range = default_range


class GameState:
    KILLER = 'killer'
    SURVIVOR = 'survivor'
    RANDOM = 'random'

    def __init__(self, bot):
        self.bot = bot
        self.attempts = 0
        self.character = None
        self.is_survivor = False
        self.thread = None
        self.is_game_active = False
        self.game_type = GameState.RANDOM

    async def stop_game(self):
        self.attempts = 0
        self.is_survivor = False
        await self.thread.edit(archived=True)
        self.thread = None
        self.is_game_active = False

    def start_game(self, game_type=RANDOM):
        self.attempts = 0
        self.game_type = game_type
        if game_type == GameState.RANDOM:
            self.is_survivor, self.character = Character.get_random_character(self.bot.session)
        elif game_type == GameState.SURVIVOR:
            self.is_survivor = True
            self.character = Survivor.get_random_survivor(self.bot.session)
        else:
            self.is_survivor = False
            self.character = Killer.get_random_killer(self.bot.session)
        self.is_game_active = True

    def guess(self, character_name: str):
        self.attempts += 1
        return character_name == self.character.name


