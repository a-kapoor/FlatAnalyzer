import awkward as ak, coffea, copy
from coffea import hist, analysis_tools
from modules.selection import *
import modules.ExpressoTools as ET
import modules.objects as obj
from coffea.analysis_tools import PackedSelection
import numpy.ma as ma
import numpy as np
from modules.hcoll import binning
    ############################# KEEP THIS BLOCK ##################
histograms = {
    ############################# KEEP THIS BLOCK ##################
    'Meeg':hist.Hist("Events",hist.Cat('process', 'process'),hist.Bin("Meeg", "Mllg", 200,100,200)),
    'Mmmg':hist.Hist("Events",hist.Cat('process', 'process'),hist.Bin("Mmmg", "Mllg", 200,100,200)),
    'Mttg':hist.Hist("Events",hist.Cat('process', 'process'),hist.Bin("Mttg", "Mllg", 200,100,200))


    ############################# KEEP THIS BLOCK ##################
}
    ############################# KEEP THIS BLOCK ##################


############################# KEEP THIS BLOCK ##################
def myanalysis(pars, logger, h, ev, doweight=True):

    dataset,isData,histAxisName,year=pars['dataset'],pars['isData'],pars['histAxisName'],pars['year']
    xsec,sow,pass_options,analysis_point=pars['xsec'],pars['sow'],pars['passoptions'],pars['analysispoint']

    from modules.hcoll import hcoll,binning
    hists = hcoll(h, isData, xsec, sow, doweight, process=histAxisName)
    ET.autolog(f"{len(ev)} Events at the start of your analysis", logger, 'i')
############################# KEEP THIS BLOCK ##################

    # Start your analysis``
    #-------------------------------------------------------------------------------------------------------

    if not isData:
         if pass_options=='Xsecweight':
            genw = ev["genWeight"]
            ev["weight_norm"] = (xsec / sow) * genw
            #ev["weight_norm"] =1
         else:
            
            ev["weight_norm"]=1

    ev["recoEle"]=ev.Electron[(ev.Electron.cutBased >=3) & (ev.Electron.pt > 0) & (abs(ev.Electron.eta)<2.5)]
    ev["recoMu"]=ev.Muon[(ev.Muon.mediumId==True) & (ev.Muon.pt > 20) & (abs(ev.Muon.eta)<2.1)]
    #ev["recoTau"]=ev.Tau[(ev.Tau.idDecayModeOldDMs==True) & (ev.Tau.idAntiMu>=1) & (ev.Tau.idAntiEle>=1)
                                 #& (ev.Tau.pt > 30) &  (abs(ev.Tau.eta)<2.5)]  ##idAntiMu is important else it gives muons --> ask Anshul if Chao Chen applies it # AK: My tree did not have the anti variables with the same name, so just commenting, but just a matter of using different nano version.
    ev["recoTau"]=ev.Tau[(ev.Tau.idDecayModeOldDMs==True) & (ev.Tau.pt > 30) &  (abs(ev.Tau.eta)<2.5)]  ##idAntiMu is important else it gives muons --> ask Anshul if Chao Chen applies it

    ev["Photon","cutBasedBitmap"]=ev.Photon.vidNestedWPBitmap # adding because my nano is v9 and the name is vidNestedWPBitmap
    ev["recoPho"]=ev.Photon[(ev.Photon.cutBasedBitmap >=2) & (ev.Photon.pt > 20) & (abs(ev.Photon.eta)<2.5)]

    ev["recoEle2"] = (ak.num(ev.recoEle) >= 2) & (ak.num(ev.recoPho) >= 1)
    ev["recoMu2"] = (ak.num(ev.recoMu) >= 2) & (ak.num(ev.recoPho) >= 1)
    ev["recoTau2"] = (ak.num(ev.recoTau) >= 2) & (ak.num(ev.recoPho) >= 1)

    events_2Ele = ev[ev.recoEle2==True]
    events_2Mu = ev[ev.recoMu2==True]
    events_2Tau = ev[ev.recoTau2==True]
    
    events_2Ele["dRl1g"] = events_2Ele.Photon[:,0].delta_r(events_2Ele.Electron[:,0])
    events_2Ele["dRl2g"] = events_2Ele.Photon[:,0].delta_r(events_2Ele.Electron[:,1])
    events_2Mu["dRl1g"] = events_2Mu.Photon[:,0].delta_r(events_2Mu.Muon[:,0])
    events_2Mu["dRl2g"] = events_2Mu.Photon[:,0].delta_r(events_2Mu.Muon[:,1])
    events_2Tau["dRl1g"] = events_2Tau.Photon[:,0].delta_r(events_2Tau.Tau[:,0])
    events_2Tau["dRl2g"] = events_2Tau.Photon[:,0].delta_r(events_2Tau.Tau[:,1])
    
    ###select events with dR > 0.4 of the photon with at least one of the electron
    events_2Ele["passdR_eg"] = (events_2Ele.dRl1g > 0.4) & (events_2Ele.dRl2g > 0.4) 
    events_2Mu["passdR_mg"] = (events_2Mu.dRl1g > 0.4) & (events_2Mu.dRl2g > 0.4)
    events_2Tau["passdR_tg"] = (events_2Tau.dRl1g > 0.4) & (events_2Tau.dRl2g > 0.4)

    events_2Ele_passdR = events_2Ele[events_2Ele.passdR_eg==True]
    events_2Mu_passdR = events_2Mu[events_2Mu.passdR_mg==True]
    events_2Tau_passdR = events_2Tau[events_2Tau.passdR_tg==True]

    ####Mass of 3 body object
    events_2Ele_passdR["llg"]= events_2Ele_passdR.Electron[:,0] + events_2Ele_passdR.Electron[:,1] + events_2Ele_passdR.Photon[:,0]
    events_2Mu_passdR["llg"]= events_2Mu_passdR.Muon[:,0] + events_2Mu_passdR.Muon[:,1] + events_2Mu_passdR.Photon[:,0]
    events_2Tau_passdR["llg"]= events_2Tau_passdR.Tau[:,0] + events_2Tau_passdR.Tau[:,1] + events_2Tau_passdR.Photon[:,0]

    ####Condition on mass 
    events_2Ele_passdR["massWindow"] = (events_2Ele_passdR.llg.mass > 120) & (events_2Ele_passdR.llg.mass < 130)
    events_2Mu_passdR["massWindow"] = (events_2Mu_passdR.llg.mass > 120) & (events_2Mu_passdR.llg.mass < 130)
    events_2Tau_passdR["massWindow"] = (events_2Tau_passdR.llg.mass > 120) & (events_2Tau_passdR.llg.mass < 130)
    
    events_Ele_final_MW = events_2Ele_passdR[events_2Ele_passdR.massWindow==True]
    events_Mu_final_MW = events_2Mu_passdR[events_2Mu_passdR.massWindow==True]
    events_Tau_final_MW = events_2Tau_passdR[events_2Tau_passdR.massWindow==True]


    ###################################################

    ##My hist is a wrapper around original hist to also include a selection right at the time of storing plot.
    ##Added a very basic selection for now, which selects all events
    #basically
    ##  hists.fill(nameofhistogram,normalization,verybasicselection, event_object_whose_attribute_you_want_to_access,axisname="attribute")
    
    hists.fill('Meeg',events_Ele_final_MW.weight_norm,(events_Ele_final_MW.event>0), events_Ele_final_MW.llg,Meeg="mass")
    hists.fill('Mmmg',events_Mu_final_MW.weight_norm,(events_Mu_final_MW.event>0), events_Mu_final_MW.llg, Mmmg="mass")
    hists.fill('Mttg',events_Tau_final_MW.weight_norm,(events_Tau_final_MW.event>0), events_Tau_final_MW.llg, Mttg="mass")

    ############################# KEEP THIS BLOCK ##################
    ET.autolog(f"{len(ev)} Events at the end of your analysis", logger, 'i')
    return hists.get()
    ############################# KEEP THIS BLOCK ##################
