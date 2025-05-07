import json
import os

config_path = "config.json"

# Значения по умолчанию
config = {
    "music_volume": 0.5,
    "sound_volume": 0.5,
    "fullscreen": False
}

# Загрузка
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        try:
            config.update(json.load(f))
        except json.JSONDecodeError:
            pass

# Сохранение
def save_config():
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)