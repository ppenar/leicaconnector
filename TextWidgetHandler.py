from logging import StreamHandler

class TextWidgetHandler(StreamHandler):

    def __init__(self,_textWidget):
        StreamHandler.__init__(self)
        self.textWidget = _textWidget

    def emit(self,record):
        msg = self.format(record)
        self.textWidget.insert('1.0',f"{msg}\n")