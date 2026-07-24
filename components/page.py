from abc import ABC
from abc import abstractmethod

from components.layout import Layout


class BasePage(ABC):

    title = ""

    subtitle = ""

    icon = "📄"

    def render(self):

        Layout.page(self.title)

        self.header()

        self.toolbar()

        self.statistics()

        self.content()

        self.footer()

    def header(self):
        pass

    def toolbar(self):
        pass

    def statistics(self):
        pass

    @abstractmethod
    def content(self):
        ...

    def footer(self):
        pass
