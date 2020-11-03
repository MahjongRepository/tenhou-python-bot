# Use that config for bots battle
from game.ai.configs.default import BotDefaultConfig


class XeniaConfig(BotDefaultConfig):
    name = "Xenia"

    FEATURE_DEFENCE_ENABLED = False
