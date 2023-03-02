import logging
from time import sleep
from unicodedata import name
import clr
clr.AddReference("LMF.Tracker.Connection") # Works in case the LMF.Tracker.Connection.dll is in a place where Python
                                           # looks for it (here the same folder as this file. Alternatively adding it to the Search Paths in the project also works.).
from LMF.Tracker import *
from LMF.Tracker.Measurements.Profiles import StationaryMeasurementProfile # Using some C# elements from a different namespace as imported with "import *" above require a separate import
from LMF.Tracker.Measurements.Profiles import AreaScanProfile # Using some C# elements from a different namespace as imported with "import *" above require a separate import
from LMF.Tracker.Enums import EAccuracy, EMeasurementStatus
from LMF.Units import ERotationType
from LMF.Tracker.MeasurementResults import StationaryMeasurement3D, SingleShotMeasurement3D
from LMF.Tracker.ErrorHandling import LmfException
from System import Enum
from  LMF.Tracker.Simulator.Settings.Enums import SimERotationType

class TrackerInterface:
    """Klasa reprezentuje Tracker Leica
    """
    def __init__(self,_log:logging) -> None:
        self.log=_log
        self.isConnect =False
        self.selectedProfile=None
        self.currentMeasurementStatusName=''
        statusNames = Enum.GetNames(EMeasurementStatus)
        self.statusNamesTranslated = []
        for s in statusNames:
            self.statusNamesTranslated.append(s)

    def discoverTrackers(self):
        trackerFinder = TrackerFinder()
        trackerFinder.Refresh()
        availableTrackers = trackerFinder.Trackers
        listIp=[]
        for t in availableTrackers:
            listIp.append(t.IPAddress)
        return listIp

    def connect(self,ipAddress):
        """Metoda łączy z trackerem. 

        :param ipAddress: Adres trackera w formacie ip:port
        :type ipAddress: _type_
        """
        self.tracker = Connection().Connect(ipAddress)
        if self.tracker==None:
            self.log.info("Tracker: Tracker no found")
            return
        self.isConnect=True
        self.name = self.tracker.Name
        self.log.info("Tracker: Connect successful")
        self.selectedProfile = self.tracker.Measurement.Profiles.Selected
        self.tracker.Settings.RotationType=ERotationType.Quaternion # set RotationType.Quaternion
       
    def getTargetsList(self):

        list=[]
        for t in self.tracker.Targets:
            list.append(t.Name)
        self.log.info("Available targets: {0}".format(len(list)))

        return list

    def getSelectedTarget(self):
        if self.isConnect:
            return self.tracker.Targets.Selected.Name
        else:
            return ''
   
    def getSelectedProbeFace(self):
        selectProbe="-"
        if self.isConnect:
            selectedTarget =self.tracker.Targets.Selected #object
            if hasattr(selectedTarget,'ProbeFaces'):
                selectProbe ="Face {0}".format(selectedTarget.ProbeFaces.Selected.FaceID.Value)
        return selectProbe

        
    def selectTarget(self,name):
        for t in self.tracker.Targets:
            if(t.Name == name):
                try:
                    t.Select()
                    selectedTargetName = self.getSelectedTarget()
                    if selectedTargetName == name:
                        self.log.info("Selected {0} target".format(name))
                    else:
                        self.log.error("Selected {0} target".format(name))

                except LmfException as e:
                    self.log.error(e.Description)
    
    def selectTip(self,nameTip):
        if self.isConnect:
            selectedTarget =self.tracker.Targets.Selected #object
            if hasattr(selectedTarget,'Tips'):
                for tips in selectedTarget.Tips:
                    if tips.IsSelectable.Value:
                        tips.Deselect()
                self.log.info("Deselected all virtual tips")
                sleep(0.1)
                for tips in selectedTarget.Tips:
                    if tips.Name == nameTip and tips.IsSelectable.Value:
                        tips.Select()
                        self.log.info("Selected {0} tip".format(nameTip))
                sleep(0.1)
            else:
                self.log.error("Selected {0} tip".format(nameTip))

        else:
            self.log.error("Selected {0} tip".format(nameTip))
    def getTips(self):
        list =[]
        if self.isConnect:
            selectedTarget =self.tracker.Targets.Selected #object
            if hasattr(selectedTarget,'Tips'):
                for tips in selectedTarget.Tips:
                    list.append(tips.Name)
        return list
    def getSelectedTips(self):
        selectedTips =''
        if self.isConnect:
            selectedTarget =self.tracker.Targets.Selected #object
            if hasattr(selectedTarget,'Tips'):
                selectedTips=selectedTarget.Tips.Selected.Name
        return selectedTips


    def getMeasurementProfiles(self):
        list =[]
        if self.isConnect:
            profiles = self.tracker.Measurement.Profiles
            for p in profiles:
                list.append(p.Name)
        return list

    def getSelectedMeasurementProfile(self):
        profile=''
        if self.isConnect:
            profile = self.tracker.Measurement.Profiles.Selected.Name
        return profile
    def selectProfile(self,name,value):
        isSelect=False
        if self.isConnect:
            profiles = self.tracker.Measurement.Profiles
            for p in profiles:
                if p.Name == name:
                    if p.Name == 'Continuous Time':
                        p.TimeSeparation.Value=value
                    if p.Name == 'Continuous Distance':
                        p.DistanceSeparation.Value=value
                    p.Select()
                    isSelect = True
            if isSelect:
                self.log.info("Selected {0} measurment profile".format(name))
            else:
                self.log.error("Selected {0} measurment profile".format(name))
        else:
            self.log.error("Selected {0} measurment profile".format(name))

    def getTimeSeparationValue(self):
        value=-1
        if self.isConnect:
            profiles = self.tracker.Measurement.Profiles
            for p in profiles:
                if p.Name == 'Continuous Time':
                        value=p.TimeSeparation.Value
        return value

    def getDistanceSeparationValue(self):
        value=-1
        if self.isConnect:
            profiles = self.tracker.Measurement.Profiles
            for p in profiles:
                if p.Name == 'Continuous Distance':
                        value=p.DistanceSeparation.Value
        return value

    def startMeasurement(self):
        self.tracker.Measurement.StartMeasurement()

    def stopMeasurement(self):
        self.tracker.Measurement.StopMeasurement()


    def getMeasurementStatus(self):
        if self.isConnect:
            value = self.tracker.Measurement.Status.Value
            return self.getMeasurementStatusName(value)
        return ""

    def getMeasurementStatusValue(self):
        value=-1
        if self.isConnect:
            value = self.tracker.Measurement.Status.Value
            return value
        return value
    def setMeasurementEvent(self,event):
            self.tracker.Measurement.MeasurementArrived += event

    def getMeasurementStatusName(self,value):
        self.currentMeasurementStatusName= self.statusNamesTranslated[value]
        return self.currentMeasurementStatusName