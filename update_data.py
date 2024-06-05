import json


def get_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        with open('perk_data.json', 'r', encoding='utf-8') as p_d:
            perk_data = json.load(p_d)
            for character in data['survivors']:
                for perk in character['perks']:
                    perk['popularity'] = perk_data[perk['name']]
            for character in data['killers']:
                for perk in character['perks']:
                    perk['popularity'] = perk_data[perk['name']]
        return data


if __name__ == '__main__':
    data = get_data()
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)
