from typing import Any, Union, Dict, Optional, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from aiogram_i18n import I18nMiddleware, I18nContext
from aiogram_i18n.lazy.base import BaseLazyFilter


class LanguageCallbackFilter(BaseLazyFilter):
    keyboard: "LanguageInlineMarkup"
    len: int

    def __init__(self, keyboard: "LanguageInlineMarkup"):
        self.keyboard = keyboard
        self.len = len(keyboard.prefix)

    async def startup(self, middleware: "I18nMiddleware"):
        await self.keyboard.startup(middleware=middleware)

    async def __call__(self, callback: CallbackQuery) -> Union[bool, Dict[str, Any]]:
        if not callback.data or not callback.data.startswith(self.keyboard.prefix):
            return False
        return {self.keyboard.param: callback.data[self.len:]}


class LanguageInlineMarkup:
    def __init__(
        self,
        key: str,
        row: int = 3,
        hide_current: bool = False,
        prefix: str = "__lang__",
        param: str = "lang",
        keyboard: List[List[InlineKeyboardButton]] = None
    ):
        self.key = key
        self.row = row
        self.hide_current = hide_current
        self.prefix = prefix
        self.param = param
        self.filter = LanguageCallbackFilter(
            keyboard=self
        )
        self.keyboards: Dict[str, List[List[InlineKeyboardButton]]] = {

        }
        self.keyboard = keyboard or tuple()

    def reply_markup(self, locale: Optional[str] = None) -> InlineKeyboardMarkup:
        if locale is None:
            locale = I18nContext.get_current(False).locale
        return InlineKeyboardMarkup(
            inline_keyboard=self.keyboards.get(locale)
        )

    async def startup(self, middleware: "I18nMiddleware"):
        if self.keyboards:
            return
        for locale in middleware.core.available_locales:
            button = InlineKeyboardButton(
                text=middleware.core.get(self.key, locale),
                callback_data=f"{self.prefix}{locale}"
            )
            for _locale in middleware.core.available_locales:
                if self.hide_current and locale == _locale:
                    continue

                if _locale not in self.keyboards:
                    self.keyboards[_locale] = [[]]

                if len(self.keyboards[_locale][-1]) == self.row:
                    self.keyboards[_locale].append([])

                self.keyboards[_locale][-1].append(
                    button
                )
        for keyboard in self.keyboards.values():
            keyboard.extend(self.keyboard)
