from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class StatsCallbacks:
    SHOW_OVERVIEW = "stats:overview"
    SHOW_BOT_STATS = "stats:bot"
    BACK = "stats:back"
    CLOSE = "stats:close"


def build_stats_keyboard(_, is_sudo: bool) -> InlineKeyboardMarkup:
    non_sudo_row = [
        InlineKeyboardButton(
            text=_["SA_B_1"],
            callback_data=StatsCallbacks.SHOW_OVERVIEW,
        )
    ]
    sudo_row = [
        InlineKeyboardButton(
            text=_["SA_B_2"],
            callback_data=StatsCallbacks.SHOW_BOT_STATS,
        ),
        InlineKeyboardButton(
            text=_["SA_B_3"],
            callback_data=StatsCallbacks.SHOW_OVERVIEW,
        ),
    ]
    rows = [
        sudo_row if is_sudo else non_sudo_row,
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=StatsCallbacks.CLOSE,
            )
        ],
    ]
    return InlineKeyboardMarkup(rows)


def build_back_keyboard(_) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data=StatsCallbacks.BACK,
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=StatsCallbacks.CLOSE,
            ),
        ]
    ]
    return InlineKeyboardMarkup(rows)
