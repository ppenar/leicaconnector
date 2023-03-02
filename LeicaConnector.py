import tkinter as tk
from tkinter import ttk

import logging
import configparser
import App 


CONFIG_FILE = "config.ini"
def initConfig():
        """Czyta plik konfiguracyjny
           Przydatne: https://docs.python.org/3/library/configparser.html
        """
        cfg=configparser.ConfigParser()
        cfg.read(CONFIG_FILE)
        if cfg.has_option('NAME','NameConfigFile')==True:
           # self.log.info("Read config file: %s",self.cfg['NAME']['NameConfigFile'])
            return cfg

        else:
            return None
def initLogger():
        """
        Inicjalizacja logów dla konsoli.
        Zapis logów w pliku odbywa się poprzez dodanie kolejnego uchwytu do logera
        (przykład: https://docs.python.org/3/library/logging.handlers.html , 
        https://www.toptal.com/python/in-depth-python-logging )
        """

        #definicja uchwytu loggera dla konsoli (wyjścia standarowego)
        consoleLogHandler = logging.StreamHandler()    
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s')
        consoleLogHandler.setFormatter(formatter)
        consoleLogHandler.setLevel(logging.INFO)
    
        #definicja logów
        log = logging.getLogger("LeicaConnectorLogger")
        log.setLevel(logging.INFO)
        log.addHandler(consoleLogHandler)
        log.info("Init logger")
        return log



if __name__ == "__main__":
    log = initLogger()
    cfg = initConfig()
    if cfg != None:
        log.info("Read config file: %s",cfg['NAME']['NameConfigFile'])
        
        root = tk.Tk()
        root.tk.call("source", cfg['GUI']['TclFile'])
        root.tk.call("set_theme", cfg['GUI']['GuiTheme'])
        root.title(string=cfg['GUI']['WindowTitle'])

        app = App.App(root,cfg,log)
        app.pack(fill="both", expand=True)
        # Set a minsize for the window, and place it in the middle
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())
        x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
        y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
        root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))
        root.mainloop()

    else:
        log.error("Config file not exists")
