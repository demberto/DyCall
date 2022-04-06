"""Translation-aware themed widgets."""

from ttkbootstrap import ttk
from ttkbootstrap.localization import MessageCatalog


def _tr(t: str) -> str:
    return MessageCatalog.translate(t)


class _TrButton(ttk.Button):
    def __init__(self, master=None, text: str = "", **kwargs):
        super().__init__(master=master, text=_tr(text), **kwargs)


class _TrLabel(ttk.Label):
    def __init__(self, master=None, text: str = "", **kwargs):
        super().__init__(master=master, text=_tr(text), **kwargs)


class _TrLabelFrame(ttk.Labelframe):
    def __init__(self, master=None, text: str = "", **kwargs):
        super().__init__(master=master, text=_tr(text), **kwargs)
