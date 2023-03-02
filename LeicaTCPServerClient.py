

from asyncio.log import logger
from cmath import log
import logging
from socket import socket
import time

from utils import LeicaFrame, TMacFrame, bytesToLeicaFrame


class LeicaTCPServerClient:
    """Klasa implementuje socket dla klienta. 
    Metoda clientLoop działa jako kolejny wątek programu
    """
    def __init__(self,_conn:socket,_addr,_serv) -> None:
        """Konstruktor

        :param _conn: socket klienta
        :type _conn: socket
        :param _addr: (IP,PORT) dla klienta
        :type _addr: tuple
        :param _serv: instancja serwera
        :type _serv: LeicaTCPServer
        """
        self.sock = _conn
        self.clientAddress = _addr
        self.serv=_serv
        self.isRoot=False

    def clientLoop(self):
        
        while True:
            msg=self.sock.recv(1024)
            ii = len(msg)
            if len(msg)==0:
                #jeśli klient się rozłączył
                break
            self.serv.app.log.info("LeicaTCPServerClient: Client %s send data",str(self.clientAddress))
            frame = bytesToLeicaFrame(msg)
            self.serv.leicaFrameRecived(self,frame)
           # self.sock.sendall(msg)
        self.sock.close()
        #wywołanie metody w serwerze
        self.serv.stopClientThread(self)

    def sendFrame(self,frame):
        """Metoda wysyła ramkę danych do klienta

        :param frame: wysyłana ramka
        :type frame: LeicaFrame
        """
        self.sock.sendall(frame.toBytes())
        
    def __str__(self) -> str:
        """Klient oznaczony przez * może wydawać komendy. Inni klienci mogą tylko słuchać

        :return: reprezentacja obiektu jako str
        :rtype: str
        """
        if (self.isRoot==True):
            return "{0}*".format(self.clientAddress)
        else:
            return str(self.clientAddress)


    def __eq__(self, __o: object) -> bool:
        return str(self.clientAddress)==str(__o.clientAddress)

       