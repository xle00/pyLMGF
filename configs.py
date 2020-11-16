import json


def load_configs():
    with open('configs.json', 'r') as f:
        return json.loads(f.read())


def load_game_languages():
    with open('lang.json', 'r', encoding='utf-8') as f:
        return json.loads(f.read())
