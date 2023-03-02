from concurrent.futures import thread
import socket
import logging
from urllib import request
from App import App
from LeicaTCPServerClient import LeicaTCPServerClient
import threading
from utils import LeicaFrame

class LeicaTCPServer:
    """Klasa implementuje serwer TCP o określonym adresie tworząc nowy wątek.
    Przydatne:
    - https://stackoverflow.com/questions/10810249/python-socket-multiple-clients
    - https://docs.python.org/3/library/socket.html
    - https://docs.python.org/3/library/threading.html

    """
    def __init__(self, _app: App):
        """Konstruktor

        :param _leicaConn: referencja do klasy głównej programu
        :type _leicaConn: LeicaConector
        """
        self.app =_app
        self.server_address =(self.app.cfg['TCP']['Ip'], int(self.app.cfg['TCP']['Port']))
      
        #lista klientów
        self.clients =[]
        self.app.log.info("LeicaServer: init Leica server: %s",self.server_address)
        return
    def serverLoop(self):
        """Pętla gniazda. Po połączeniu z klientem tworzy dla niego instancje klasy
        LeicaTCPServerClient i uruchamia nowy wątek do sprawdzania gniazda. Instancja nowego
        klienta zapisywana jest w polu clients. 
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        self.sock.listen(5)
        while True:
            newConnection, clientAddress = self.sock.accept()
            newClient = LeicaTCPServerClient(
                newConnection,
                clientAddress,
                self)
            if (len(self.clients)==0):
                newClient.isRoot=True
            self.clients.append(newClient)
            self.app.updateTCPClientList(self.clients)
            self.app.log.info('LeicaServer: Start thread for client %s',clientAddress)
            thread = threading.Thread(target = newClient.clientLoop)
            thread.start()
                
            
    def startServerThread(self):
        """Inicjuje wątek serwera
        """
        self.serverThread = threading.Thread(target=self.serverLoop)
        self.serverThread.setDaemon(True)
        self.app.log.info("LeicaServer: Start serwer %s thread",self.server_address)
        self.serverThread.start()



    def stopClientThread(self,client):
        """Metoda wywoływana w wątku klient, gdy ten zakończył połaczenie

        :param client: instancja klienta
        :type client: LeicaTCPServerClient
        """
        self.app.log.info("Client %s disconnected",client)
        self.clients.remove(client)
        if (len(self.clients)>=1):
            c=self.clients[0]
            c.isRoot=True
        self.app.updateTCPClientList(self.clients)


    def leicaFrameRecived(self,client:LeicaTCPServerClient, frame:LeicaFrame):
        """Metoda wywoływana przez instancje LeicaTCPServerClient po otrzymaniu od klienta danych, które
       są konwertowane (w klasie LeicaTCPServerClient) na obiekt klasy LeicaFrame. Ramka jest
       przekazywana do instancji klasy LeicaConector 

       :param client: instancja klienta
       :type client: LeicaTCPServerClient
       :param frame: ramka danych
       :type frame: LeicaFrame
       """
        self.app.leicaFrameRecived(client,frame)
      #  self.leicaConn.leicaFrameRecived(client,frame)
        

       
        

    

