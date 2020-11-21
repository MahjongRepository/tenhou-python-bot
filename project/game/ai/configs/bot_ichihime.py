from game.ai.configs.default import BotDefaultConfig
from game.ai.placement import PlacementHandler


class IchihimeConfig(BotDefaultConfig):
    name = "Ichihime"

    PLACEMENT_HANDLER_CLASS = PlacementHandler

    TUNE_DANGER_BORDER_TEMPAI_VALUE = 0
    TUNE_DANGER_BORDER_1_SHANTEN_VALUE = 0
    TUNE_DANGER_BORDER_2_SHANTEN_VALUE = 0
