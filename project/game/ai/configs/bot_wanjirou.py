from game.ai.configs.default import BotDefaultConfig
from game.ai.placement import DummyPlacementHandler


class WanjirouConfig(BotDefaultConfig):
    name = "Wanjirou"

    PLACEMENT_HANDLER_CLASS = DummyPlacementHandler
