from TrackerInterface import *
from LeicaTCPServerClient import *
from utils import *
class TrackerCommand:
    """Klasa implementuje komendy wydawane do trackera. Wykonywana komenda jest określona przez kod ramki komendy. 
    To przypisanie określono w pliku konfiguracyjnym. Wybranie odpowiedniej komendy, będącej metodą w tej klasie, jest realizowane
    w metodzie exec.
    """
    def __init__(self,_trackerInterface: TrackerInterface,_cfg,_log: logging) -> None:
        """Konstruktor

        :param _tracker: obiekt trackera
        :type _tracker: TrackerInterface
        :param _cfg: obiekt reprezentujący plik konfiguracyjny
        :type _cfg: ConfigParser
        :param _log: obiekt loggera
        :type _log: logging
        """
        self.trackerInterface = _trackerInterface
        self.cfg = _cfg
        self.log=_log

    def exec(self,client:LeicaTCPServerClient,frame:LeicaFrame):
        """Metoda sprawdzająca błedy i wybierająca komendę na podstawie kodu ramki danych

        :param client: klient TCP
        :type client: LeicaTCPServerClient
        :param frame: ramka danych
        :type frame: LeicaFrame
        :return: zwraca wartość logiczną 1
        :rtype: Boolean
        """

        sendFrame = None
        #sprawdza czy połączono z trackerem. Jeśli nie, to wysyła błąd ogólny
        if (self.trackerInterface.isConnect==False):
            sendFrame = getGeneralErrorFrameByCode(self.cfg['GENERAL_ERROR']['TrackerDisconnect'])
            client.sock.sendall(sendFrame.toBytes())
            self.log.info("Tracker command: GENERAL_ERROR (TrackerDisconnect)")
            self.log.info("Tracker command: Send {0}".format(sendFrame))
            return True

        #sprawdza czy klient ma prawo roota (połączył się jako pierwszy). Jeśli nie ma
        #wysyła ramkę błędu
        if (client.isRoot==False):
            sendFrame =  getGeneralErrorFrameByCode(self.cfg['GENERAL_ERROR']['NotRoot'])
            client.sock.sendall(sendFrame.toBytes())
            self.log.info("Tracker command: GENERAL_ERROR (NotRoot)")
            self.log.info("Tracker command: Send {0}".format(sendFrame))
            return True

        #sprawdza czy ramka jest poprawna i czy istnieje kod odczytany z ramki 
        commandStr = frame.toCommandStr()
        if frame.code == -1 or self.cfg.has_option('COMMAND',commandStr) == False:
            sendFrame = getGeneralErrorFrameByCode(self.cfg['GENERAL_ERROR']['CommandUnsupported'])
            client.sock.sendall(sendFrame.toBytes())
            self.log.info("Tracker command: Send GENERAL_ERROR (CommandUnsupported)")
            self.log.info("Tracker command: Send {0}".format(sendFrame))
            return True
        
        methodStr =self.cfg['COMMAND'][commandStr]
            #wywołuje metodę o określonej nazwie
        getattr(self,methodStr)(client,frame)
        return True

    def SelectStationaryProfileCommand(self,client:LeicaTCPServerClient,frame: LeicaFrame):
        """Metoda (komenda) ustawia na Trackerze profil stacjonarny 
        :param client: klient TCP
        :type client: LeicaTCPServerClient
        :param frame: ramka danych
        :type frame: LeicaFrame
        :return: zwraca wartość logiczną 1
        :rtype: Boolean
        """
        
        #wybór profilu stacjonarnego
        self.log.info("TrackerCommand: Exec SelectStationaryProfileCommand")
        self.trackerInterface.selectProfile('Stationary',-1)
        
        cond =self.trackerInterface.getSelectedMeasurementProfile() == 'Stationary'
        ackErrorFrame = getAckOrErrorCommandFrame(cond,frame)
        client.sock.sendall(ackErrorFrame.toBytes())
        self.log.info("TrackerCommand: Send {0}".format(ackErrorFrame))
        return True

    def SelectContinuousTimeProfileCommand(self,client:LeicaTCPServerClient,frame: LeicaFrame):
        """Metoda (komenda) ustawia na Trackerze profil pomiaru ciągłego 
        :param client: klient TCP
        :type client: LeicaTCPServerClient
        :param frame: ramka danych
        :type frame: LeicaFrame
        :return: zwraca wartość logiczną 1
        :rtype: Boolean
        """
        
        #wybór profilu stacjonarnego
        self.log.info("TrackerCommand: Exec SelectContinuousTimeProfileCommand")
        value = int(frame.data1)
        self.trackerInterface.selectProfile('Continuous Time',value)
        
        cond =self.trackerInterface.getSelectedMeasurementProfile() == 'Continuous Time'
        ackErrorFrame = getAckOrErrorCommandFrame(cond,frame)
        client.sock.sendall(ackErrorFrame.toBytes())
        self.log.info("TrackerCommand: Send {0}".format(ackErrorFrame))
        return True


    def SelectContinuousDistanceProfileCommand(self,client:LeicaTCPServerClient,frame: LeicaFrame):
        """Metoda (komenda) ustawia na Trackerze profil pomiaru ciągłego wywoływany przesunięciem
        :param client: klient TCP
        :type client: LeicaTCPServerClient
        :param frame: ramka danych
        :type frame: LeicaFrame
        :return: zwraca wartość logiczną 1
        :rtype: Boolean
        """
        
        #wybór profilu stacjonarnego
        self.log.info("TrackerCommand: Exec SelectContinuousDistanceProfileCommand")
        value = int(frame.data1)
        self.trackerInterface.selectProfile('Continuous Distance',value)
        
        cond =self.trackerInterface.getSelectedMeasurementProfile() == 'Continuous Distance'
        ackErrorFrame = getAckOrErrorCommandFrame(cond,frame)
        client.sock.sendall(ackErrorFrame.toBytes())
        self.log.info("TrackerCommand: Send {0}".format(ackErrorFrame))
        return True

    def SelectTouchTriggerProfileCommand(self,client:LeicaTCPServerClient,frame: LeicaFrame):
        """Metoda (komenda) ustawia na Trackerze profil w którym pomiar jest wywoływany dotykiem
        :param client: klient TCP
        :type client: LeicaTCPServerClient
        :param frame: ramka danych
        :type frame: LeicaFrame
        :return: zwraca wartość logiczną 1
        :rtype: Boolean
        """
        
        #wybór profilu stacjonarnego
        self.log.info("TrackerCommand: Exec SelectTouchTriggerProfileCommand")
        value = int(frame.data1)
        self.trackerInterface.selectProfile('Touch Trigger',value)
        
        cond =self.trackerInterface.getSelectedMeasurementProfile() == 'Touch Trigger'
        ackErrorFrame = getAckOrErrorCommandFrame(cond,frame)
        client.sock.sendall(ackErrorFrame.toBytes())
        self.log.info("TrackerCommand: Send {0}".format(ackErrorFrame))
        return True

    def StartMeasurment(self,client:LeicaTCPServerClient,frame:LeicaFrame):
        """Metoda (komenda) wyzwala pomiar w profilu stacjonarnym lub rozpoczyna pomiar
        cykliczny w profilu ciągłym

        :param client: klient TCP
        :type client: LeicaTCPServerClient
        :param frame: ramka danych
        :type frame: LeicaFrame
        :return: zwraca wartość logiczną 1
        :rtype: Boolean
        """

        self.log.info("TrackerCommand: Exec StartMeasurment command")
        self.trackerInterface.startMeasurement()
        
        return True
   
    def StopMeasurment(self,client:LeicaTCPServerClient,frame:LeicaFrame):
        """Metoda (komenda) kończy pomiar

        :param client: klient TCP
        :type client: LeicaTCPServerClient
        :param frame: ramka danych
        :type frame: LeicaFrame
        :return: zwraca wartość logiczną 1
        :rtype: Boolean
        """
        
        self.log.info("TrackerCommand: Exec StopMeasurment command")
        self.trackerInterface.stopMeasurement()
        cond =True
        ackErrorFrame = getAckOrErrorCommandFrame(cond,frame)
        client.sock.sendall(ackErrorFrame.toBytes())
        self.log.info("TrackerCommand: Send {0}".format(ackErrorFrame))
        return True

