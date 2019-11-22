def make_message(message, size=100, shape='o', color='#ff9999', bcolor='k', bwidth=1, alpha=1, label=None):
    return Message(message, size=size, shape=shape, color=color, bcolor=bcolor, bwidth=bwidth, alpha=alpha, label=label)

class AbstractMessage:
    def __init__(self, message, size=100, shape='o', color='#ff9999', bcolor='k', bwidth=1, alpha=1, label=None):
        self.__msg = message
        self.size = size
        self.shape = shape
        self.color = color
        self.label = label
        self.border_color = bcolor
        self.border_width = bwidth
        self.transparency = alpha

    def message(self):
        return self.__msg

    def attr_dict(self):
        return {'size': self.size, 'shape': self.shape, 'color': self.color, 'label': self.label,
                'bcolor': self.border_color, 'bwidth': self.border_width, 'alpha': self.transparency}

    def dict_for_scatter(self):
        return {'s': self.size, 'c': self.color, 'marker': self.shape, 'alpha':self.transparency,
                'linewidth': self.border_width, 'edgecolors': self.border_color}

    def to_networkx_node(self, messageid):
        return messageid, self.attr_dict()


class Message(AbstractMessage):
    def __init__(self, message, size=300, shape='o', color='#ff9999', bcolor='k', bwidth=1, alpha=None, label=None):
        super().__init__(message, size=size, shape=shape, color=color, bcolor=bcolor, bwidth=bwidth, alpha=alpha, label=label)