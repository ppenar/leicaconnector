
import profile
import tkinter as tk
from tkinter import ttk

from TrackerInterface import TrackerInterface


class TrackerInfoFrame(ttk.LabelFrame):



    def __init__(self, _root,_cfg,_trackerInterface: TrackerInterface,_font,_padding,_row,_column):
        super().__init__(master=_root,text=_cfg['TRACKERINFO']['Title'], padding=_padding)
        super().grid(row=_row, column=_column, padx=(20, 10), pady=10, sticky="nsew")

        self.font=_font
        self.cfg=_cfg
        self.trackerInterface = _trackerInterface
        
        self.selectedTargetLabel = ttk.Label(
            self,
            text=self.cfg['TRACKERINFO']['SelectedTargetLabel'],
            justify="left",
            font=self.font,
        )
        self.selectedTargetLabel.grid(row=0, column=0, padx=5, pady=1, sticky="nsew")
        
        self.selectedTargetValue = ttk.Label(
            self,
            text="-",
            justify="left",
            font=self.font,
        )
        self.selectedTargetValue.grid(row=1, column=0, padx=10, pady=1, sticky="nsew")

        self.selectedProbeFaceLabel = ttk.Label(
            self,
            text=self.cfg['TRACKERINFO']['SelectedProbeFaceLabel'],
            justify="left",
            font=self.font,
        )
        self.selectedProbeFaceLabel.grid(row=0, column=1, padx=5, pady=1, sticky="nsew")
        
        self.selectedProbeFaceValue = ttk.Label(
            self,
            text="-",
            justify="left",
            font=self.font,
        )
        self.selectedProbeFaceValue.grid(row=1, column=1, padx=10, pady=1, sticky="nsew")
        
        self.selectedTipsLabel = ttk.Label(
            self,
            text=self.cfg['TRACKERINFO']['SelectedTipsLabel'],
            justify="left",
            font=self.font,
        )
        self.selectedTipsLabel.grid(row=2, column=0, padx=5, pady=1, sticky="nsew")
        
        self.selectedTipsValue = ttk.Label(
            self,
            text="-",
            justify="left",
            font=self.font,
        )
        self.selectedTipsValue.grid(row=3, column=0, padx=10, pady=1, sticky="nsew")

        self.selectedMeasurmentProfileLabel = ttk.Label(
            self,
            text=self.cfg['TRACKERINFO']['SelectedMeasurmentProfileTipsLabel'],
            justify="left",
            font=self.font,
        )
        self.selectedMeasurmentProfileLabel.grid(row=2, column=1, padx=5, pady=1, sticky="nsew")
        
        self.selectedMeasurmentProfileValue = ttk.Label(
            self,
            text="-",
            justify="left",
            font=self.font,
        )
        self.selectedMeasurmentProfileValue.grid(row=3, column=1, padx=10, pady=1, sticky="nsew")
        ####################
        self.measurmentStatusLabel = ttk.Label(
            self,
            text=self.cfg['TRACKERINFO']['MeasurmentStatusLabel'],
            justify="left",
            font=self.font,
        )
        self.measurmentStatusLabel.grid(row=4, column=0, padx=5, pady=1, sticky="nsew")
        
        self.measurmentStatusValue = ttk.Label(
            self,
            text="-",
            justify="left",
            font=self.font,
        )
        self.measurmentStatusValue.grid(row=5, column=0, padx=10, pady=1, sticky="nsew")




    def update(self):
        selectedTargetName = self.trackerInterface.getSelectedTarget()
        self.selectedTargetValue['text']=selectedTargetName
        selectedProbeFace = self.trackerInterface.getSelectedProbeFace()
        self.selectedProbeFaceValue['text']=selectedProbeFace
        selectedTips = self.trackerInterface.getSelectedTips()
        self.selectedTipsValue['text'] = selectedTips
        selectedProfile = self.trackerInterface.getSelectedMeasurementProfile()
        self.selectedMeasurmentProfileValue['text'] = selectedProfile
        if selectedProfile == 'Continuous Time':
            value = self.trackerInterface.getTimeSeparationValue()
            self.selectedMeasurmentProfileValue['text'] = "{profile} | {val} ms".format(profile=selectedProfile,val=value)
        if selectedProfile == 'Continuous Distance':
            value = self.trackerInterface.getDistanceSeparationValue()
            self.selectedMeasurmentProfileValue['text'] = "{profile} | {val} ms".format(profile=selectedProfile,val=value)

        self.measurmentStatusValue['text'] = self.trackerInterface.getMeasurementStatus()

    def updateMeasurmentStatus(self,name):
        self.measurmentStatusValue['text'] = name