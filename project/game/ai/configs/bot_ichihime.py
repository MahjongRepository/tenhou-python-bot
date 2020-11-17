from game.ai.configs.default import BotDefaultConfig
from game.ai.placement import PlacementHandler


class IchihimeConfig(BotDefaultConfig):
    name = "Ichihime"

    PLACEMENT_HANDLER_CLASS = PlacementHandler
