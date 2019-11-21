def make_message(self, message, size=300, color='#ff9999', bcolor='k', bwidth=1, alpha=None, label=None):
    return Message(message, size=size, color=color, bcolor=bcolor, bwidth=bwidth, alpha=alpha, label=label)

class AbstractMessage:
    SHAPE = 's'

    def __init__(self, message, size=300, color='#ff9999', bcolor='k', bwidth=1, alpha=None, label=None):
        self.__msg = message
        self.size = size
        self.color = color
        self.label = label
        self.border_color = bcolor
        self.border_width = bwidth
        self.transparency = alpha

    def message(self):
        return self.__msg

class Message(AbstractMessage):
    def __init__(self, message, size=300, color='#ff9999', bcolor='k', bwidth=1, alpha=None, label=None):
        super().__init__(message, size=size, color=color, bcolor=bcolor, bwidth=bwidth, alpha=alpha, label=label)




