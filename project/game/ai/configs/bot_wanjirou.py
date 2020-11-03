# Use that config for bots battle
from game.ai.configs.default import BotDefaultConfig


class WanjirouConfig(BotDefaultConfig):
    name = "Wanjirou"

    FEATURE_DEFENCE_ENABLED = False
