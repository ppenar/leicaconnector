from cgitb import text
from time import sleep
import tkinter as tk
from tkinter import DISABLED, ttk
from PIL import Image, ImageTk
import logging
import configparser

import tkinter.font as tkFont
from LeicaTCPServerClient import LeicaTCPServerClient

from TextWidgetHandler import TextWidgetHandler
from TrackerCommand import TrackerCommand
from TrackerInfoFrame import TrackerInfoFrame
from TrackerInterface import TrackerInterface
from utils import *

CONFIG_FILE = "config.ini"

class App(ttk.Frame):
    def __init__(self,parent,cfg,log):
        ttk.Frame.__init__(self)

        self.log=log
        self.cfg = cfg
        self.textW  = None
        self.serverFrame=None
        self.serverIpLabel =None
        self.serverIpLabelValue=None
        self.serverStatusLabel=None
        self.serverStatusLabelValue=None
        self.serverClientListLabel=None
        self.serverClientList=None
        self.trackerConnectionFrame = None
        self.discoverTrackersBtn = None
        self.trackerComboBox = None        
        self.connectTrackerBtn = None
        self.trackerStatusLabel = None
        self.trackerStatusLabelValue = None
        self.trackerSettingsFrame = None
        self.trackerControlFrame = None
        self.startMeasurementBtn = None
        self.stopMeasurementBtn = None
        
        self.targetsLabel = None
        self.targetsComboBox = None

        self.tipLabel = None
        self.tipComboBox = None
        self.profileLabel=None
        self.profileComboBox=None
        self.constProfileLabel = None
        self.constProfileValue = None
        self.trackerInfoFrame=None





        self.hide=False
        self.trackerInterface = TrackerInterface(self.log)
        self.trackerCommand = TrackerCommand(self.trackerInterface,self.cfg,self.log)
        self.setupWidgets()

        from LeicaTCPServer import LeicaTCPServer
        self.leicaServer = LeicaTCPServer(self)
        self.leicaServer.startServerThread()



    def updateTCPClientList(self,clients):
        """Aktualizuje liste klientów w polu ListBox 

        :param clients: lista obiektów klasy LeicaTCPServerClient
        :type clients: list<LeicaTCPServerClient>
        """
        self.log.info("GUI: Update client list")
        n=self.serverClientList.size()
        self.serverClientList.delete(0,n)
        for i in range(len(clients)):
            self.serverClientList.insert(i+1,clients[i])


    def connectTrackerCall(self):
        ipAddr = self.trackerComboBox.get()
        self.trackerInterface.connect(ipAddr)
        if self.trackerInterface.isConnect:
            self.trackerStatusLabelValue['text']="Connect"
            self.trackerStatusLabelValue['foreground']='#0f0'

            targetList = self.trackerInterface.getTargetsList()
            self.targetsComboBox['values']=targetList
            self.targetsComboBox.current(0)
            self.targetChanges(None)

            tipsList = self.trackerInterface.getTips()
            self.tipComboBox['values']=tipsList
            self.tipComboBox.set(self.trackerInterface.getSelectedTips())
           # self.probeFaceComboBox.current(0)

            measurementProfiles = self.trackerInterface.getMeasurementProfiles()
            self.profileComboBox['values']= measurementProfiles
            self.profileComboBox.set(self.trackerInterface.getSelectedMeasurementProfile())
            self.trackerInfoFrame.update()

            #self.trackerInterface.setMeasurementEvent(self.OnMeasurementArrived)
            self.trackerInterface.tracker.Measurement.Status.Changed += self.OnMeasurementStatus
            self.trackerInterface.tracker.Measurement.MeasurementArrived += self.OnMeasurementArrived
          
        else:
            self.trackerStatusLabelValue['text']="Disconnect"
            self.trackerStatusLabelValue['foreground']='#f00'

    def discoverTrackerCall(self):
        self.log.info("GUI: Discover Tracker")
        ipTrackersList = self.trackerInterface.discoverTrackers()
        self.log.info("Discover {0} trackers".format(len(ipTrackersList)))
        self.trackerComboBox.delete(0, 'end')
        ipTrackersList.append(self.cfg['TRACKER']['Ip'])
        self.trackerComboBox['values']=ipTrackersList
        self.trackerComboBox.current(0)
        self.log.info("GUI: Update tracker list")


    def targetChanges(self,event):
        currentName = self.targetsComboBox.get()
        self.trackerInterface.selectTarget(currentName)
        self.updateTrackerSettingsFrame()
        self.trackerInfoFrame.update()

    def tipChanges(self,event):
        currentName = self.tipComboBox.get()
        self.trackerInterface.selectTip(currentName)
        sleep(1)
        self.updateTrackerSettingsFrame()
        self.trackerInfoFrame.update()

    def profileChanges(self,event):
        currentName = self.profileComboBox.get()
        value = int(self.constProfileValue.get())
        self.trackerInterface.selectProfile(currentName,value)
        self.updateTrackerSettingsFrame()
        self.trackerInfoFrame.update()

    def startMeasurementCall(self):
        self.log.info("[GUI] Start Measurement button clicked")
        if self.trackerInterface.isConnect:
            self.trackerInterface.startMeasurement()
            self.log.info("Start Measurement")
    def stopMeasurementCall(self):
        self.log.info("[GUI] Stop Measurement button clicked")
        if self.trackerInterface.isConnect:
            self.trackerInterface.stopMeasurement()
            self.log.info("Stop Measurement")
    def clearTextCall(self):
        self.textW.delete(1.0,tk.END)

    def updateTrackerSettingsFrame(self):
        self.targetsComboBox.set(self.trackerInterface.getSelectedTarget())
        self.tipComboBox.set(self.trackerInterface.getSelectedTips())
        self.profileComboBox.set(self.trackerInterface.getSelectedMeasurementProfile())

        
    def leicaFrameRecived(self,client:LeicaTCPServerClient, frame:LeicaFrame):
        """Metoda wywoływana przez instancje LeicaTCPServer, gdy klient odbierze ramkę Leica. 
        Metoda aktualizuje opis profilu trackera w GUI

       :param client: instancja klienta TCP
       :type client: LeicaTCPServerClient
       :param frame: ramka danych
       :type frame: LeicaFrame
       """
        self.log.info("GUI: %s",frame)
        #wykonanie komendy przypisanej do kodu statusu ramki
        self.trackerCommand.exec(client,frame)
        if self.trackerInterface.isConnect:
            self.trackerInfoFrame.update()
            self.updateTrackerSettingsFrame()

        #if self.trackerInterface.isConnect==True:
         #   self.updateLeicaDesc()

    def OnMeasurementStatus(self,sender,newValue):
        prevStatusName = self.trackerInterface.currentMeasurementStatusName
        newStatusName = self.trackerInterface.getMeasurementStatusName(newValue)
        self.trackerInfoFrame.updateMeasurmentStatus(newStatusName)
        self.log.info("Measurment status: {0}".format(newStatusName))

        if newStatusName == 'NotReady' and prevStatusName == 'MeasurementInProgress':
            clients=self.leicaServer.clients
            for c in clients:
                frame = getGeneralErrorFrameByCode(self.cfg['GENERAL_ERROR']['MeasurementBreak'])
                c.sendFrame(frame)
                self.log.info("[GENERAL ERROR] Meas. not ready. Send  %s to client %s",frame,c)


    def OnMeasurementArrived(self,sender, paramMeasurements,exept):
        """[EVENT] Metoda wywoływana po wyzwoleniu pomiaru. W zależności od profilu event 
        jest wywoływany raz bądź cyklicznie. Jej zadaniem jest wysyłanie ramki z pomiarami  (pomiar rzeczywisty x1000 w celu rzutowania na int32) do klientów TCP.

        :param sender: instancja klasy MeasurementSettings (klasa z API Leica). Klasa pobiera i ustawie opcje dla pomiarów .
        :type sender: MeasurementSettings (API Leica)
        :param paramMeasurements: Kolekcja obiektów klasy Measurement
        :type paramMeasurements: MeasurementCollection (API Leica)
        :param paramException: wyjątek
        :type paramException: LmfException (API Leica)
        """
       
        currentMeasStatus=self.trackerInterface.getMeasurementStatusValue()
        cond1 = int(currentMeasStatus) == int(self.cfg['MeasurementStatusValues']['ReadyToMeasure'])
        cond2 = int(currentMeasStatus) == int(self.cfg['MeasurementStatusValues']['MeasurementInProgress'])
        if cond1 or cond2:
            clients=self.leicaServer.clients
            for c in clients:
                pp=0
                for m in paramMeasurements:
                   
                    position = m.Position
                    gainPoz = int(self.cfg['TRACKER']['GainPoz'])

                    valX=int(position.Coordinate1.Value*gainPoz)
                    valY=int(position.Coordinate2.Value*gainPoz)
                    valZ=int(position.Coordinate3.Value*gainPoz)
                    if hasattr(m,"Rotation"):
                        rotation = m.Rotation
                        gainRot = int(self.cfg['TRACKER']['GainRot'])
                        q0 = int(rotation.Value0.Value*gainRot)
                        q1 = int(rotation.Value1.Value*gainRot)
                        q2 = int(rotation.Value2.Value*gainRot)
                        q3 = int(rotation.Value3.Value*gainRot)
                        frame =TMacFrame(int(self.cfg['CODE']['codeTMacFrame'])+pp,valX,valY,valZ,q0,q1,q2,q3)
                    else:
                        frame= LeicaFrame(int(self.cfg['CODE']['codeLeicaFrame'])+pp,valX,valY,valZ)
                    c.sendFrame(frame)
                    self.log.info("Measurement position: Send  %s to client %s",frame,c)
                    #if hasattr(m,"Rotation"):
                     #   rotation = m.Rotation
                     #   q0 = int(rotation.Value0.Value*10000)
                     #   q1 = int(rotation.Value1.Value*10000)
                     #   q2 = int(rotation.Value2.Value*10000)
                     #   q3 = int(rotation.Value3.Value*10000)
                     #   frame = LeicaFrame(500+pp,q0,q1,q2,q3)
                     #   self.log.info(frame)
                     #   c.sendFrame(frame)
                     #   self.log.info("Measurement rotation: Send  %s to client %s",frame,c)
                    pp=pp+1 
            return True
        frame = LeicaFrame(int(self.cfg['GENERAL_ERROR']['MeasurmentNotAvailable']),0,0,0,0)
        for c in clients:
            c.sendFrame(frame)
            self.log.info("Measurement error: Send  %s to client %s",frame,c)

        return True

    def setupWidgets(self):

        self.normalFont = tkFont.Font(family=self.cfg['GUI']['FontFamily'], size=14)
        self.smallFont = tkFont.Font(family=self.cfg['GUI']['FontFamily'], size=10)
        # Inicjalizacja grid-u
        for index in [0, 1, 2, 3]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)
        
        #Log TextWidget
        self.textW = tk.Text(self, width=80, height=10)
        self.textW.grid(row=2, column=2,padx=5, pady=10, sticky="nsew",rowspan=2, columnspan=2)

        textWLogHandler = TextWidgetHandler(self.textW)
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s')
        textWLogHandler.setFormatter(formatter)
        self.log.addHandler(textWLogHandler)
        self.log.info("Add widget handler")

        #logo programu
        image = Image.open(self.cfg['GUI']['LogoFile'])       
        python_image = ImageTk.PhotoImage(image)
        self.imageLabel = ttk.Label(self,image=python_image)
        self.imageLabel.image = python_image
        self.imageLabel.grid(row=0, column=0,padx=5, pady=5, sticky="NSEW",)



        ########################
        #Serwer frame
        ## Separator
        self.separator = ttk.Separator(self)
        self.separator.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="ew")

        self.serverFrame = ttk.LabelFrame(self, text="Server", padding=(20, 10))
        self.serverFrame.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="nsew")

        self.serverIpLabel = ttk.Label(
            self.serverFrame,
            text=self.cfg['GUI']['ServerIpLabel'],
            justify="left",
            font=self.smallFont,
        )
        self.serverIpLabel.grid(row=0, column=0, padx=5, pady=1, sticky="nsew")

        self.serverIpLabelValue = ttk.Label(
            self.serverFrame,
            text=f"{self.cfg['TCP']['Ip']}:{self.cfg['TCP']['Port']}",
            justify="center",
            font=self.normalFont,
        )
        self.serverIpLabelValue.grid(row=1, column=0, padx=10, pady=1, sticky="nsew")

        self.serverStatusLabel = ttk.Label(
            self.serverFrame,
            text=self.cfg['GUI']['ServerStatusLabel'],
            justify="left",
            font=self.smallFont,
        )
        self.serverStatusLabel.grid(row=2, column=0, padx=5, pady=1, sticky="nsew")
        
        self.serverStatusLabelValue = ttk.Label(
            self.serverFrame,
            text="Is running",
            justify="left",
            foreground='#0f0',
            font=self.normalFont,
        )
        self.serverStatusLabelValue.grid(row=3, column=0, padx=10, pady=1, sticky="nsew")

        self.serverClientListLabel = ttk.Label(
            self.serverFrame,
            text=self.cfg['GUI']['ServerClientListLabel'],
            justify="left",
            font=self.smallFont,
        )
        self.serverClientListLabel.grid(row=4, column=0, padx=5, pady=1, sticky="nsew")

        self.serverClientList = tk.Listbox(self.serverFrame)
        self.serverClientList.grid(row=5, column=0, padx=10, pady=1, sticky="nsew")
#        
############### Tracker connection frame
        self.trackerConnectionFrame = ttk.LabelFrame(self, text=self.cfg['GUI']['TrackerConnectFrameName'], padding=(20, 10))
        self.trackerConnectionFrame.grid(row=0, column=1, padx=(20, 10), pady=10, sticky="nsew")

        self.discoverTrackersBtn = ttk.Button(
            self.trackerConnectionFrame, 
            text=self.cfg['GUI']['DiscoverBtnName'],
            command = self.discoverTrackerCall)
        self.discoverTrackersBtn.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.trackerComboBox = ttk.Combobox(self.trackerConnectionFrame, values=[self.cfg['TRACKER']['Ip']],state='readonly')
        self.trackerComboBox.current(0)
        self.trackerComboBox.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        
        self.connectTrackerBtn = ttk.Button(
            self.trackerConnectionFrame, 
            text=self.cfg['GUI']['ConnectTrackerBtnName'], 
            style="Accent.TButton",
            command = self.connectTrackerCall
        )
        self.connectTrackerBtn.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")

        self.trackerStatusLabel = ttk.Label(
            self.trackerConnectionFrame,
            text=self.cfg['GUI']['TrackerStatusLabel'],
            justify="left",
            font=self.smallFont,
        )
        self.trackerStatusLabel.grid(row=3, column=0, padx=5, pady=1, sticky="nsew")
        
        self.trackerStatusLabelValue = ttk.Label(
            self.trackerConnectionFrame,
            text="Disconnect",
            justify="left",
            foreground='#f00',
            font=self.normalFont,
        )
        self.trackerStatusLabelValue.grid(row=4, column=0, padx=10, pady=1, sticky="nsew")


       
############### Tracker settings frame
        self.trackerSettingsFrame = ttk.LabelFrame(self, text=self.cfg['GUI']['TrackerSettingsFrameName'], padding=(20, 10))
        self.trackerSettingsFrame.grid(row=2, column=1, padx=(20, 10), pady=10, sticky="nsew")

        self.targetsLabel = ttk.Label(
            self.trackerSettingsFrame,
            text=self.cfg['GUI']['TargetLabel'],
            justify="left",
            font=self.smallFont,
        )
        self.targetsLabel.grid(row=0, column=0, padx=5, pady=1, sticky="nsew")

        self.targetsComboBox = ttk.Combobox(self.trackerSettingsFrame,state='readonly')
        self.targetsComboBox.bind('<<ComboboxSelected>>',self.targetChanges)
        self.targetsComboBox.grid(row=1, column=0, padx=5, pady=10, sticky="ew")
        
       
        
        self.tipLabel = ttk.Label(
            self.trackerSettingsFrame,
            text=self.cfg['GUI']['TipLabel'],
            justify="left",
            font=self.smallFont,
        )
        self.tipLabel.grid(row=4, column=0, padx=5, pady=1, sticky="nsew")
       
        self.tipComboBox = ttk.Combobox(self.trackerSettingsFrame,state='readonly')
        self.tipComboBox.bind('<<ComboboxSelected>>',self.tipChanges)
        self.tipComboBox.grid(row=5, column=0, padx=5, pady=10, sticky="ew")

        self.profileLabel = ttk.Label(
            self.trackerSettingsFrame,
            text=self.cfg['GUI']['ProfileLabel'],
            justify="left",
            font=self.smallFont,
        )
        self.profileLabel.grid(row=7, column=0, padx=5, pady=1, sticky="nsew")
       
        self.profileComboBox = ttk.Combobox(self.trackerSettingsFrame,state='readonly')
        self.profileComboBox.bind('<<ComboboxSelected>>',self.profileChanges)
        self.profileComboBox.grid(row=8, column=0, padx=5, pady=10, sticky="ew")

        self.constProfileLabel = ttk.Label(
            self.trackerSettingsFrame,
            text=self.cfg['GUI']['ConstProfileLabel'],
            justify="left",
            font=self.smallFont,
        )
        self.constProfileLabel.grid(row=9, column=0, padx=5, pady=1, sticky="nsew")
       
        self.constProfileValue = ttk.Entry(self.trackerSettingsFrame)
        self.constProfileValue.insert(0, "10")
        self.constProfileValue.grid(row=10, column=0, padx=5, pady=10, sticky="ew")

        self.trackerInfoFrame = TrackerInfoFrame(
            _root = self,
            _cfg = self.cfg,
            _trackerInterface = self.trackerInterface,
            _font = self.smallFont,
            _padding = (20, 10),
            _row = 0,
            _column=2
        )

        ####### Tracker control
        self.trackerControlFrame = ttk.LabelFrame(self, text=self.cfg['GUI']['TrackerControlFrameName'], padding=(20, 10))
        self.trackerControlFrame.grid(row=0, column=3, padx=(20, 10), pady=10, sticky="nsew")

        self.startMeasurementBtn = ttk.Button(
            self.trackerControlFrame, 
            text=self.cfg['GUI']['StartMeasurementBtnLabel'], 
            style="Accent.TButton",
            command = self.startMeasurementCall
        )
        self.startMeasurementBtn.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.stopMeasurementBtn = ttk.Button(
            self.trackerControlFrame, 
            text=self.cfg['GUI']['StopMeasurementBtnLabel'], 
            style="Accent.TButton",
            command = self.stopMeasurementCall
        )
        self.stopMeasurementBtn.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

        self.clearTextBtn = ttk.Button(
            self.trackerControlFrame, 
            text=self.cfg['GUI']['ClearTextBtnLabel'], 
            command = self.clearTextCall
        )
        self.clearTextBtn.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")
        
        


        