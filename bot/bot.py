import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from game.game import Game
from bot.filters import InputFilter


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data['game_params'] = []
    context.user_data['curr_min_val'] = Game.MIN_VALS['difficulty']
    context.user_data['curr_stage'] = 'max_multiplier'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Choose game difficulty (starts from {Game.MIN_VALS['difficulty']})",
    )
    return 'max_multiplier'


def ask_param(param_name: str, next_stage: str) -> callable:
    async def asker(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['game_params'].append(
            int(update.message.text)
        )
        context.user_data['curr_min_val'] = Game.MIN_VALS[param_name]
        context.user_data['curr_stage'] = next_stage
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Choose game {param_name} (starts from {Game.MIN_VALS[param_name]})",
        )
        return next_stage

    return asker


async def start_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    g = Game(
        *context.user_data['game_params'],
        int(update.message.text),
    )
    context.user_data.clear()
    context.user_data['game'] = g
    _, questions = g.get_questions()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions,
        parse_mode='MarkdownV2',
    )
    return "next_round"


async def next_round(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    results = context.user_data['game'].check_answers(update.message.text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=results,
        parse_mode='MarkdownV2',
    )

    finished, questions = context.user_data['game'].get_questions()

    if finished:
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Game finished.\nSend '/start' to start again.",
        )
        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions,
        parse_mode='MarkdownV2',
    )
    return "next_round"


async def wrong_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"You must choose integer value from {context.user_data['curr_min_val']}",
    )
    return context.user_data['curr_stage']


def run_bot():
    application = ApplicationBuilder().token(os.environ.get("TOKEN")).build()

    start_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            "max_multiplier": [MessageHandler(
                InputFilter(Game.MIN_VALS["difficulty"]),
                ask_param("max_multiplier", "problems_per_round"),
            )],
            "problems_per_round": [MessageHandler(
                InputFilter(Game.MIN_VALS["max_multiplier"]),
                ask_param("problems_per_round", "number_of_rounds"),
            )],
            "number_of_rounds": [MessageHandler(
                InputFilter(Game.MIN_VALS["problems_per_round"]),
                ask_param("number_of_rounds", "start_game"),
            )],
            "start_game": [MessageHandler(
                InputFilter(Game.MIN_VALS["number_of_rounds"]),
                start_game,
            )],
            "next_round": [MessageHandler(
                filters.TEXT,
                next_round,
            )],
        },
        fallbacks=[MessageHandler(
            filters.ALL,
            wrong_input,
        )]
    )
    application.add_handler(start_handler)

    application.run_polling()
