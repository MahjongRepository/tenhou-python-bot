from game.ai.placement import PlacementHandler
from game.ai.riichi import Riichi


class BotDefaultConfig:
    # all features that we are testing should starts with FEATURE_ prefix
    # with that it will be easier to track these flags usage over the code
    FEATURE_DEFENCE_ENABLED = True

    PLACEMENT_HANDLER_CLASS = PlacementHandler
    RIICHI_HANDLER_CLASS = Riichi

    TUNE_DANGER_BORDER_TEMPAI_VALUE = 0
    TUNE_DANGER_BORDER_1_SHANTEN_VALUE = 0
    TUNE_DANGER_BORDER_2_SHANTEN_VALUE = 0
