from game.ai.configs.default import BotDefaultConfig
from game.ai.placement import PlacementHandler


class KaaviConfig(BotDefaultConfig):
    name = "Kaavi"

    PLACEMENT_HANDLER_CLASS = PlacementHandler
