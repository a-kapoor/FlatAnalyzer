from coffea import processor,hist
import modules.ExpressoTools as ET
import modules.IHEPProcessor as IHEPProcessor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import json

class IHEPAnalysis:
    
    def __init__(self):
        self.a=0
        self.hists={}
        self.samples=[]
        self.SampleList=[]
        
    
    def preprocess(self,preprocessor):
        self.preprocess=preprocessor

    def preselection(self,preselection):
        self.preselect=preselection
    
    def SetHists(self,histfile):
        with open(histfile, 'r') as json_file:
            self.hists = json.load(json_file)
            print(self.hists)
    
    def GetSamples(self):
        for sami in self.SampleList:
            self.samples.append(ET.parse_yml(sami))
            
    def SetAnalysis(self,analysis):
        self.analysis=analysis
    
    def run(self,xrootd="root://cmsxrootd.fnal.gov//",chunksize=100,maxchunks=1):
        for sample in self.samples:
            sample["files"]=[xrootd + file for file in sample["files"]]
            
            result= processor.run_uproot_job({sample["histAxisName"]:sample["files"]},sample["treeName"],
                                             IHEPProcessor.IHEPProcessor(self.preprocess,self.preselect,self.analysis,self.hists,sample),
                                             processor.futures_executor,{"schema": NanoAODSchema, 'workers':16} , chunksize=chunksize, maxchunks=maxchunks)

            
            
        return result
                       
                         
                          
                         