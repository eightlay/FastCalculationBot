from telegram.ext.filters import MessageFilter


class InputFilter(MessageFilter):
    def __init__(self, min_val: int):
        self.min_val = min_val

    def filter(self, message):
        try:
            return int(message.text) >= self.min_val
        except:
            return False
