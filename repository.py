import json

from models import Killer, Survivor, TerrorRadius, Perk
from datetime import datetime


def populate_database(session, filename):
    with open(filename, 'r', encoding='utf8') as f:
        characters_data = json.load(f)
        survivors = characters_data['survivors']
        for survivor in survivors:
            release_date = datetime.strptime(survivor.pop('release_date'), '%Y-%m-%d').date()
            perks = []
            for perk in survivor.pop('perks'):
                perks.append(Perk(**perk))
            character = Survivor(
                release_date=release_date,
                perks=perks,
                **survivor
            )
            session.add(character)
            print(character.name + ' added to db')
        killers = characters_data['killers']
        for killer in killers:
            terror_radius = TerrorRadius(**killer.pop('terror_radius'))
            release_date = datetime.strptime(killer.pop('release_date'), '%Y-%m-%d').date()
            perks = []
            for perk in killer.pop('perks'):
                perks.append(Perk(**perk))
            character = Killer(
                release_date=release_date,
                perks=perks,
                terror_radius=terror_radius,
                **killer
            )
            session.add(character)
            print(character.name + ' added to db')
    session.commit()
