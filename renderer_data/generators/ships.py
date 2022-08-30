import json
import polib
import os

from polib import MOFile, MOEntry
from typing import Dict
from renderer_data.gameparams import get_data
from renderer_data.utils import LOGGER


def create_ships_data():
    LOGGER.info("Creating ships data...")
    dict_ships = {}
    list_ships = get_data("Ship")
    list_units = get_data("Unit")
    units_name_to_id = {unit.name: unit.id for unit in list_units}

    for ship in list_ships:
        dict_ships[ship.id] = ship

    mo_file = os.path.join(os.getcwd(), "resources", "global.mo")
    mo_strings: MOFile = polib.mofile(mo_file)
    dict_strings = {}

    for mo_string in mo_strings:
        mo_string: MOEntry
        dict_strings[mo_string.msgid] = mo_string.msgstr

    dict_ships_info: Dict[int, dict] = {}

    for ship in dict_ships.values():
        hulls = {}
        components = {}

        for key, value in ship.ShipUpgradeInfo.__dict__.items():
            try:
                if value.ucType == "_Hull":
                    hull_name = value.components["hull"][0]
                    hull = getattr(ship, hull_name)
                    hulls[units_name_to_id[key]] = [
                        len(hull.burnNodes),
                        len(hull.floodNodes),
                    ]
                elif value.ucType == "_Artillery":
                    for comp in value.components["artillery"]:
                        components[comp] = {
                            "maxDist": getattr(ship, comp).maxDist
                        }
                elif value.ucType == "_Suo":
                    for comp in value.components["fireControl"]:
                        components[comp] = {
                            "maxDistCoef": getattr(ship, comp).maxDistCoef
                        }

            except AttributeError:
                continue

        si = {
            "index": ship.index,
            "name": dict_strings[f"IDS_{ship.index}"].upper(),
            "species": ship.typeinfo.species,
            "level": ship.level,
            "hulls": hulls,
            "components": components
        }

        dict_ships_info[ship.id] = si

    with open(os.path.join(os.getcwd(), "generated", "ships.json"), "w") as f:
        json.dump(dict_ships_info, f)
