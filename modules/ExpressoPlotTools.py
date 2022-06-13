import gzip
import pickle
#import hist
import coffea.hist as hist
import matplotlib.pyplot as plt
import mplhep as hep
from hist.intervals import ratio_uncertainty
import numpy as np
def get_hist_from_pkl(path_to_pkl,allow_empty=True):
        h = pickle.load( gzip.open(path_to_pkl) )
        if not allow_empty:
            h = {k:v for k,v in h.items() if v.values() != {}}
        return h


def dictprint(di):
        for key, value in di.items():
                print(key, ' : ', value)

def dictplotratio(histodict,outputfolder):
    
    for hiname in histodict.keys():
        histo=histodict[hiname]
        fig, ax = plt.subplots()
        hep.style.use('CMS')
        hep.cms.label('', data=False)
        for k in histo.keys():
            dicty1=histo[k][0]
            dicty2=histo[k][1]
            h1=get_hist_from_pkl(outputfolder+'/'+dicty1['file'])[dicty1['label']].project(dicty1['axis'])
            h2=get_hist_from_pkl(outputfolder+'/'+dicty2['file'])[dicty2['label']].project(dicty2['axis'])
            hist.plotratio(
                    num=h2,
                    denom=h1,
                    clear=False,
                    error_opts={'color': histo[k][2]['color'], 'marker': '.'},
                    unc='num',ax=ax,label=dicty1['label'])
            #(h2/h1).plot(ax=ax, lw=3,label=dicty1['label'])
        ax.legend()
        plt.legend(loc='best')
        plt.savefig(f'{outputfolder}/{hiname}_ratio.pdf', dpi=200)

def dictplot2Dratio(histodict,outputfolder):
    
    for hiname in histodict.keys():
        histo=histodict[hiname]
        fig, ax = plt.subplots(figsize=(36,20))
        hep.style.use('CMS')
        hep.cms.label('', data=False)
        dicty1=histo[0]
        dicty2=histo[1]
        x1=dicty1['xaxis']
        y1=dicty1['yaxis']
        x2=dicty2['xaxis']
        y2=dicty2['yaxis']
        h1=get_hist_from_pkl(outputfolder+'/'+dicty1['file'])[dicty1['label']].project(y1,x1)
        h2=get_hist_from_pkl(outputfolder+'/'+dicty2['file'])[dicty2['label']].project(y2,x2)
        ratio = (h1.to_hist()/h2.to_hist())
        err_up, err_down = ratio_uncertainty(h1.to_hist().values(), h2.to_hist().values(), 'poisson-ratio')
        labels = []
        for ra, u, d in zip(ratio.values().ravel(), err_up.ravel(), err_down.ravel()):
                ra, u, d = f'{ra:.3f}', f'{u:.1e}', f'{d:.1e}'
                st = '$'+ra+'_{-'+d+'}^{+'+u+'}$'
                labels.append(st)
        labels = np.array(labels).reshape(5,8)

        hep.hist2dplot(ratio, labels=labels, cmap='cividis',ax=ax)
        #ax.tick_params(labelsize=10)
        #hist.plot2d(hist=ratio,xaxis=x1,ax=ax,clear=True)
        ax.legend()
        plt.legend(loc='best')
        plt.savefig(f'{outputfolder}/{hiname}_2Dratio.pdf', dpi=200)
                
def dictplotnormal(histodict,outputfolder):
    
            for hiname in histodict.keys():
                histo=histodict[hiname]
                fig, ax = plt.subplots()
                hep.style.use('CMS')
                hep.cms.label('', data=False)
                nostack=[]
                stack=[]
                nostacklabels=[]
                stacklabels=[]
                for k in histo.keys():
                    dicty=histo[k]
                    scale=1.0
                    if 'scale' in histo[k].keys():
                        scale=histo[k]['scale']
                        
                    thist=get_hist_from_pkl(outputfolder+"/"+histo[k]['file'])[k]
                    thist.scale(scale)
                    #histo[k]['h']=get_hist_from_pkl(histo[k]['file'])[k].to_hist().project(histo[k]['axis'])
                    histo[k]['h']=thist.to_hist().project(histo[k]['axis'])
                    if(histo[k]['stack']==True):
                        stack.append(histo[k]['h'])
                        stacklabels.append(histo[k]['label'])
                    if(histo[k]['stack']==False):
                        nostack.append(histo[k]['h'])
                        nostacklabels.append(histo[k]['label'])
                if len(stack)!=0:
                        hep.histplot(stack,ax=ax,lw=3,stack=True,histtype='fill',label=stacklabels)
                if len(nostack)!=0:
                        hep.histplot(nostack,ax=ax,lw=3,stack=False,histtype='step',label=nostacklabels, yerr=True)
                plt.legend(loc='best')
                plt.savefig(f'{outputfolder}/{hiname}_normal.pdf', dpi=200)


def dictplot(histodictall,outputfolder):
    
    for allkey in histodictall.keys():
        if allkey=='normal':
            dictplotnormal(histodictall[allkey],outputfolder)
        if allkey=='ratio':
            dictplotratio(histodictall[allkey],outputfolder)
        if allkey=='2Dratio':
            dictplot2Dratio(histodictall[allkey],outputfolder)

                
