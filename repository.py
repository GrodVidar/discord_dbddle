import json
from datetime import datetime

from sqlalchemy import update
from sqlalchemy.orm import backref, joinedload

from models import Killer, Perk, Survivor, TerrorRadius


def populate_database(session, filename):
    with open(filename, "r", encoding="utf-8") as f:
        characters_data = json.load(f)
        survivors = characters_data["survivors"]
        for survivor in survivors:
            instance = (
                session.query(Survivor)
                .options(joinedload(Survivor.perks))
                .filter(Survivor.name == survivor["name"])
                .first()
            )
            if instance:
                update_perks(instance.perks, survivor["perks"], session)
            else:
                release_date = datetime.strptime(
                    survivor.pop("release_date"), "%Y-%m-%d"
                ).date()
                perks = []
                for perk in survivor.pop("perks"):
                    perks.append(Perk(**perk))
                character = Survivor(release_date=release_date, perks=perks, **survivor)
                session.add(character)
                print(character.name + " added to db")
        killers = characters_data["killers"]
        for killer in killers:
            instance = (
                session.query(Killer)
                .options(joinedload(Killer.perks))
                .filter(Killer.name == killer["name"])
                .first()
            )
            if instance:
                update_perks(instance.perks, killer["perks"], session)
            else:
                terror_radius = TerrorRadius(**killer.pop("terror_radius"))
                release_date = datetime.strptime(
                    killer.pop("release_date"), "%Y-%m-%d"
                ).date()
                perks = []
                for perk in killer.pop("perks"):
                    perks.append(Perk(**perk))
                character = Killer(
                    release_date=release_date,
                    perks=perks,
                    terror_radius=terror_radius,
                    **killer
                )
                session.add(character)
                print(character.name + " added to db")
        session.commit()


def update_perks(current_perks, updated_perks, session):
    for perk in current_perks:
        for updated_perk in updated_perks:
            if perk.name == updated_perk["name"]:
                stmt = (
                    update(Perk)
                    .where(Perk.pk == perk.pk)
                    .values(popularity=updated_perk["popularity"])
                )
                session.execute(stmt)
