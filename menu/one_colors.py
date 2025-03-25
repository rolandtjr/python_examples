from colors import ColorsMeta

class OneColors(metaclass=ColorsMeta):
    BLACK = "#282C34"
    GUTTER_GREY = "#4B5263"
    COMMENT_GREY = "#5C6370"
    WHITE = "#ABB2BF"
    DARK_RED = "#BE5046"
    LIGHT_RED = "#E06C75"
    DARK_YELLOW = "#D19A66"
    LIGHT_YELLOW = "#E5C07B"
    GREEN = "#98C379"
    CYAN = "#56B6C2"
    BLUE = "#61AFEF"
    MAGENTA = "#C678DD"

    @classmethod
    def as_dict(cls):
        """
        Returns a dictionary mapping every NORD* attribute
        (e.g. 'NORD0') to its hex code.
        """
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not callable(getattr(cls, attr)) and
            not attr.startswith("__")
        }
