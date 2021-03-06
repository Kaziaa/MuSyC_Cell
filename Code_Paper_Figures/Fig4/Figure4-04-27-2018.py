#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 12:11:38 2017

@author: xnmeyer
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
font = {'family' : 'normal',
        'weight':'normal',
        'size'   : 8}
axes = {'linewidth': 2}
rc('font', **font)
rc('axes',**axes)
from scipy.stats import pearsonr
from matplotlib import rc
font = {'family' : 'arial',
        'weight':'normal',
        'size'   : 8}
axes = {'linewidth': 2}
rc('font', **font)
rc('axes',**axes)
from adjustText import adjust_text

########################################################################
####Find genes which coorelate with BRAFi from gene expression data from 
####the CCLE which were differentially expressed between the subclones 
####(as identified by anova).
########################################################################


df = pd.read_csv('../../Data/CCLE_DepMap_18Q1_RNAseq_RPKM_20180214.gct',sep='\t',header=2)
symb = pd.read_csv('../../Data/DEGs_by_ANOVA.csv')
#Subset by degs
df = df.set_index('Description')
df = df.loc[symb.T.values.tolist()[0]]
df = df.loc[~np.isnan(df.mean(axis=1))]
df = df.loc[~df.index.duplicated(keep='first')]
dip_rates = pd.read_csv('../../Data/CCLE_expression_selected_cells.csv')
dip_rates = dip_rates.set_index('cell')
dip_rates = dip_rates['rates']

df = df[dip_rates.index]
#log normalize
df[df==0] = np.min(df[df!=0]).min()/10
df = np.log10(df)

c = pd.DataFrame(np.zeros((len(df),2)),columns=['r','p'],index=df.index)
for e,ind in enumerate(df.index):
    r,p = pearsonr(np.array(dip_rates),np.array(df.loc[ind]))   
    c.set_value(ind,'r',r)
    c.set_value(ind,'p',p)
    
plt.figure(figsize=(2,2))
ax = plt.subplot(111)
plt.hist(c['r'],bins=10)
plt.xlabel('pearson-r')
plt.ylabel('frequency')
plt.vlines(max(c['r'][(c['p']<.05)&(c['r']<0.)]),plt.ylim()[0],plt.ylim()[1],linestyle='--',color='r')
plt.vlines(min(c['r'][(c['p']<.05)&(c['r']>0.)]),plt.ylim()[0],plt.ylim()[1],linestyle='--',color='r')
plt.savefig('Corrlation_plot.pdf')

ind = ['NOX5']
cl = [j.split('_')[0] for j in list(df)]
for i in ind:
    plt.figure(figsize = (1.5,1.5))
    x = np.array(dip_rates)
    y = np.array(df.loc[i])
    text = []
    for e in range(len(y)):
        plt.scatter(x[e],y[e],s=2,c='b',edgecolor='k',lw=2)
        text.append(plt.text(x[e],y[e],cl[e]))
#    adjust_text(text)
    plt.xlabel('DIP Rate (8uM PLX)')
    plt.ylabel('log(RPKM)' + i)
    plt.savefig('DIP_corr_'+i+'.pdf')

sc_dg = pd.read_csv('../../Data/DEGs_SC10_vs_SC01.csv')
plt.figure(figsize=(1.5,1.5),dpi=300)
plt.scatter(np.log10(sc_dg['baseMean']),sc_dg['log2FoldChange'],c = [.5,.5,.5],alpha=.5,s=3,rasterized=True)
sd_dg = sc_dg.set_index('symbol')
sc_dg = sd_dg.loc[df.index]
plt.scatter(np.log10(sc_dg['baseMean']),sc_dg['log2FoldChange'],c = 'k',s=3,rasterized=True)
xlim = plt.xlim()
plt.plot(xlim,[0,0],'k--',lw=1)
plt.plot(xlim,[2,2],'r--',lw=1)
plt.plot(xlim,[-2,-2],'r--',lw=1)
ind = ['NOX5']
for i in ind:
    plt.text(np.log10(sc_dg['baseMean'].loc[i]),sc_dg['log2FoldChange'].loc[i],i)
    plt.scatter(np.log10(sc_dg['baseMean'].loc[i]),sc_dg['log2FoldChange'].loc[i],c= 'tab:green',s=5)
plt.xlabel('log10(mean expression)')
plt.ylabel('log2(Fold Change)')    
plt.savefig('scatter-degs_SC10_v_SC01.pdf')

c = c.sort_values(by='r',ascending=False)
c['r'] = c['r'].astype('float').round(3).astype('string')
c['p'] = c['p'].astype('float').round(3).astype('string')
c = c.rename(columns={'p':'p-val'})
f = open('../Tables/DEGs_corr_CCLE.txt','w')
f.write(c.to_latex(escape=False))
f.close()




########################################################################
####Make figure of gene set enrichment
########################################################################
import glob
import matplotlib.pyplot as plt
from matplotlib import rc
from adjustText import adjust_text
import pandas as pd
import numpy as np
font = {'family' : 'normal',
        'weight':'normal',
        'size'   : 8}
axes = {'linewidth': 3}
rc('font', **font)
rc('axes',**axes)
fils = glob.glob('../../Data/Enriched*.csv')

fig = plt.figure(figsize=(7.5,6))
ax = []
ax.append(plt.subplot2grid((2,2),(0,0)))
ax.append(plt.subplot2grid((2,2),(1,0)))
ax.append(plt.subplot2grid((2,2),(0,1)))
ax.append(plt.subplot2grid((2,2),(1,1)))
plt.subplots_adjust(wspace=.1,hspace=.2)
df = []
for f in fils:
    df.append(pd.read_csv(f))
    
string = ['GO Biological Process','GO Molecular Function','GO Cellular Component','KEGG Pathways']

df = [i.sort_values(by='Adjusted.P.value').reset_index(drop=True) for i in df]
df = [i.loc[0:9] for i in df]
df = [i[['Adjusted.P.value','Term']] for i in df]

colors = ['#b3e2cd','#fdcdac','#cbd5e8','#f4cae4']
for i in range(4):
    plt.sca(ax[i])
    plt.title(string[i])
    ax[i].barh(np.linspace(9,0,10),-np.log10(df[i]['Adjusted.P.value']),align='center',color=colors[i],ecolor='black',alpha=.5)
    ax[i].spines['right'].set_visible(False)
    ax[i].spines['top'].set_visible(False)
    ax[i].set_yticks(range(10))
    if i!=3:
        tick_labs = [j[0][0:-2] for j in df[i]['Term'].str.split('GO:')]
        go_labs = ['GO:' + j[1][0:-1] for j in df[i]['Term'].str.split('GO:')]
        tick_labs = [tick_labs[j] for j in np.linspace(9,0,10).astype('int')]
        go_labs = [go_labs[j] for j in np.linspace(9,0,10).astype('int')]
    else:
        tick_labs = [j[0] for j in df[i]['Term'].str.split('_H')]
        tick_labs = [tick_labs[j] for j in np.linspace(9,0,10).astype('int')]        
    ax[i].set_yticklabels([])
    tick_labs = [j.upper() for j in tick_labs]
    if i !=1:
        for j in range(10):
            plt.text(.4,j-.15,tick_labs[j],weight='bold')
    else:
        for j in range(10):
            if j!=2:
                plt.text(.2,j-.15,tick_labs[j],weight='bold',size=6)
            else:
                plt.text(.2,j-.15,tick_labs[j][0:45],weight='bold',size=6)
    ax[i].tick_params(axis="y",direction='in',pad=.01)
    ax[i].set_xlabel('-log10(adj-pval)')
plt.tight_layout()
plt.savefig('Plots/Enrichment Ontologies DEGs.pdf')


fig = plt.figure(figsize=(3,2))
ax= plt.subplot(111)
num = [3,3,1,3]
tick_labs = []
for i in range(4):
    if i == 0:
        ax.barh(np.linspace(num[i]-1,0,num[i]),-np.log10(df[i]['Adjusted.P.value'][0:num[i]]),align='center',color=colors[i],ecolor='black',alpha=.5,label=string[i])
    else:
        ax.barh(np.linspace(sum(num[0:i+1])-1,sum(num[0:i]),num[i]),-np.log10(df[i]['Adjusted.P.value'][0:num[i]]),align='center',color=colors[i],ecolor='black',alpha=.5,label=string[i])       
    tl = [j[0][0:-2] for j in df[i]['Term'].str.split('GO:')][0:num[i]]
    tick_labs.append([tl[j] for j in np.linspace(num[i]-1,0,num[i]).astype('int')])

tick_labs = [item for sublist in tick_labs for item in sublist]
tick_labs = [item if 'Homo' not in item else item.split('_')[0] for item in tick_labs]
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_yticks(range(sum(num))) 
ax.set_yticklabels([])
tick_labs = [j.lower() for j in tick_labs]
for j in range(len(tick_labs)):
    plt.text(.4,j-.1,tick_labs[j],weight='normal')
ax.tick_params(axis="y",direction='in',pad=.01)
ax.set_xlabel('-log10(adj-pval)')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.3),
          ncol=2, fancybox=False, shadow=False,handletextpad=.1)
plt.tight_layout()
plt.savefig('Plots/Subset Enrichment Ontologies.pdf')




#######################################################################
###Make surface plot for A2058
#######################################################################
import pandas as pd
import numpy as np
from pylab import *
from mpl_toolkits.mplot3d import *
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import ListedColormap
import matplotlib.cm as cm
from scipy import interpolate
rc('text', usetex=False)
font = {'family' : 'normal',
        'weight':'normal',
        'size'   : 8}
axes = {'linewidth': 2}
rc('font', **font)
rc('axes',**axes)
##########################################
### D E F I N E   F U N C T I O N S
##########################################

def get_params(df):
    e0 = np.float(df['E0'])
    e1 = np.float(df['E1'])
    e2 = np.float(df['E2'])
    e3 = np.float(df['E3'])

    h1 = np.float(df['h1'])
    h2 = np.float(df['h2'])

    r1 = np.float(df['r1'])
    r2 = np.float(df['r2'])

    ec50_1 = np.power(10.,np.float(df['log_C1']))
    ec50_2 = np.power(10.,np.float(df['log_C2']))

    r1r = r1*np.power(ec50_1,h1)
    r2r = r2*np.power(ec50_2,h2)

    alpha_1 = np.power(10.,np.float(df['log_alpha1']))
    alpha_2 = np.power(10.,np.float(df['log_alpha2']))
    beta = np.float(df['beta'])/(e0-np.min((e1,e2)))
    beta_obs = np.float(df['beta_obs'])/(e0-df[['E1_obs','E2_obs']].min())

    
    concentration_1_min = np.log10(np.float(df['min_conc_d1']))
    concentration_2_min = np.log10(np.float(df['min_conc_d2']))
    
    concentration_1_max = np.log10(np.float(df['max_conc_d1']))
    concentration_2_max = np.log10(np.float(df['max_conc_d2']))
    
    model_level = str(df['model_level'])
    
    drug1_name = str(df['drug1_name'])
    drug2_name = str(df['drug2_name'])

    expt = str(df['expt'])
    
    return e0, e1, e2, e3, h1, h2, r1, r1r, r2, r2r, ec50_1, ec50_2, alpha_1, alpha_2, beta, beta_obs, concentration_1_min, concentration_1_max, concentration_2_min, concentration_2_max, model_level, drug1_name, drug2_name, expt

def dip(d1, d2, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r):
#    d1 = 1.*d1
#    d2 = 1.*d2
    d1 = np.power(10.,d1)
    d2 = np.power(10.,d2)
    h1 = 1.*h1
    h2 = 1.*h2
    alpha1 = 1.*alpha1
    alpha2 = 1.*alpha2
    r1 = 1.*r1
    r1r = 1.*r1r
    r2 = 1.*r2
    r2r = 1.*r2r
    
    U = r1r*r2r*(r1*(alpha2*d1)**h1 + r1r + r2*(alpha1*d2)**h2 + r2r)/(d1**h1*r1**2*r2*(alpha1*d2)**h2*(alpha2*d1)**h1 + d1**h1*r1**2*r2r*(alpha2*d1)**h1 + d1**h1*r1*r1r*r2*(alpha1*d2)**h2 + d1**h1*r1*r1r*r2r + d1**h1*r1*r2*r2r*(alpha1*d2)**h2 + d1**h1*r1*r2r**2 + d2**h2*r1*r1r*r2*(alpha2*d1)**h1 + d2**h2*r1*r2**2*(alpha1*d2)**h2*(alpha2*d1)**h1 + d2**h2*r1*r2*r2r*(alpha2*d1)**h1 + d2**h2*r1r**2*r2 + d2**h2*r1r*r2**2*(alpha1*d2)**h2 + d2**h2*r1r*r2*r2r + r1*r1r*r2r*(alpha2*d1)**h1 + r1r**2*r2r + r1r*r2*r2r*(alpha1*d2)**h2 + r1r*r2r**2)

    A1 = r1*r2r*(d1**h1*r1*(alpha2*d1)**h1 + d1**h1*r1r + d1**h1*r2r + d2**h2*r2*(alpha2*d1)**h1)/(d1**h1*r1**2*r2*(alpha1*d2)**h2*(alpha2*d1)**h1 + d1**h1*r1**2*r2r*(alpha2*d1)**h1 + d1**h1*r1*r1r*r2*(alpha1*d2)**h2 + d1**h1*r1*r1r*r2r + d1**h1*r1*r2*r2r*(alpha1*d2)**h2 + d1**h1*r1*r2r**2 + d2**h2*r1*r1r*r2*(alpha2*d1)**h1 + d2**h2*r1*r2**2*(alpha1*d2)**h2*(alpha2*d1)**h1 + d2**h2*r1*r2*r2r*(alpha2*d1)**h1 + d2**h2*r1r**2*r2 + d2**h2*r1r*r2**2*(alpha1*d2)**h2 + d2**h2*r1r*r2*r2r + r1*r1r*r2r*(alpha2*d1)**h1 + r1r**2*r2r + r1r*r2*r2r*(alpha1*d2)**h2 + r1r*r2r**2)

    A2 = r1r*r2*(d1**h1*r1*(alpha1*d2)**h2 + d2**h2*r1r + d2**h2*r2*(alpha1*d2)**h2 + d2**h2*r2r)/(d1**h1*r1**2*r2*(alpha1*d2)**h2*(alpha2*d1)**h1 + d1**h1*r1**2*r2r*(alpha2*d1)**h1 + d1**h1*r1*r1r*r2*(alpha1*d2)**h2 + d1**h1*r1*r1r*r2r + d1**h1*r1*r2*r2r*(alpha1*d2)**h2 + d1**h1*r1*r2r**2 + d2**h2*r1*r1r*r2*(alpha2*d1)**h1 + d2**h2*r1*r2**2*(alpha1*d2)**h2*(alpha2*d1)**h1 + d2**h2*r1*r2*r2r*(alpha2*d1)**h1 + d2**h2*r1r**2*r2 + d2**h2*r1r*r2**2*(alpha1*d2)**h2 + d2**h2*r1r*r2*r2r + r1*r1r*r2r*(alpha2*d1)**h1 + r1r**2*r2r + r1r*r2*r2r*(alpha1*d2)**h2 + r1r*r2r**2)

    A12 = r1*r2*(d1**h1*r1*(alpha1*d2)**h2*(alpha2*d1)**h1 + d1**h1*r2r*(alpha1*d2)**h2 + d2**h2*r1r*(alpha2*d1)**h1 + d2**h2*r2*(alpha1*d2)**h2*(alpha2*d1)**h1)/(d1**h1*r1**2*r2*(alpha1*d2)**h2*(alpha2*d1)**h1 + d1**h1*r1**2*r2r*(alpha2*d1)**h1 + d1**h1*r1*r1r*r2*(alpha1*d2)**h2 + d1**h1*r1*r1r*r2r + d1**h1*r1*r2*r2r*(alpha1*d2)**h2 + d1**h1*r1*r2r**2 + d2**h2*r1*r1r*r2*(alpha2*d1)**h1 + d2**h2*r1*r2**2*(alpha1*d2)**h2*(alpha2*d1)**h1 + d2**h2*r1*r2*r2r*(alpha2*d1)**h1 + d2**h2*r1r**2*r2 + d2**h2*r1r*r2**2*(alpha1*d2)**h2 + d2**h2*r1r*r2*r2r + r1*r1r*r2r*(alpha2*d1)**h1 + r1r**2*r2r + r1r*r2*r2r*(alpha1*d2)**h2 + r1r*r2r**2)
    
    return U*e0 + A1*e1 + A2*e2 + A12*e3
    
def plot_surface(mcmc_data, hts_data, drug_id, drug, N=50, elev=20, azim=19, fname=None, zlim=None,zero_conc=1):
    e0, e1, e2, e3, h1, h2, r1, r1r, r2, r2r, ec50_1, ec50_2, alpha1, alpha2, beta, beta_obs, d1_min, d1_max, d2_min, d2_max, model_level, drug1_name, drug2_name, expt = get_params(mcmc_data)
    fig = figure(figsize=(11,6))
    ax = fig.gca(projection='3d')
    #ax.set_axis_off()
    y = linspace(d1_min-zero_conc, d1_max ,N)
    t = linspace(d2_min-zero_conc, d2_max ,N)
    yy, tt = meshgrid(y, t)
    zz = dip(yy,tt, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r)
    zmin = np.min(zz)
    zmax = np.max(zz)

    if np.abs(zmin) > np.abs(zmax): zmax = np.abs(zmin)
    else: zmin = -np.abs(zmax)

    # Plot it once on a throwaway axis, to get cbar without alpha problems
    my_cmap_rgb = plt.get_cmap('bwr')(np.arange(256))
    alpha = 0.8

    for i in range(3): # Do not include the last column!
        my_cmap_rgb[:,i] = (1 - alpha) + alpha*my_cmap_rgb[:,i]
    my_cmap = ListedColormap(my_cmap_rgb, name='my_cmap')
    surf = ax.plot_surface(tt, yy, zz, cstride=1, rstride=1, cmap = my_cmap, vmin=zmin, vmax=zmax, linewidth=0)
    cbar = fig.colorbar(surf)
    cbar.solids.set_rasterized(True)
    cbar.solids.set_edgecolor("face")

    cla()
    # Plot the surface for real, with appropriate alpha
    surf = ax.plot_surface(tt, yy, zz, cstride=1, rstride=1, alpha=alpha, cmap = cm.bwr, vmin=zmin, vmax=zmax, linewidth=0)
    
    # colored curves on left and right
    lw = 5
    ax.plot(d2_min*ones(y.shape)-zero_conc, y, dip(y,d2_min-zero_conc, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), linewidth=lw)
    ax.plot(d2_max*ones(y.shape), y, dip(y,d2_max, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), linewidth=lw)

    ax.plot(t, d1_min*ones(y.shape)-zero_conc, dip(d1_min-zero_conc,t, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), linewidth=lw)
    ax.plot(t, d1_max*ones(y.shape), dip(d1_max,t, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), linewidth=lw)
    
    
    # light grey grid across surface
    for ttt in linspace(d2_min-zero_conc,d2_max,10):
        ax.plot(ttt*ones(y.shape), y, dip(y,ttt, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), '-k', linewidth=1, alpha=0.1)
        ax.plot(ttt*ones(y.shape), y, dip(y,ttt, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), '-k', linewidth=1, alpha=0.1)
        ax.plot(ttt*ones(y.shape), y, dip(y,ttt, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), '-k', linewidth=1, alpha=0.1)

    for yyy in linspace(d1_min-zero_conc, d1_max,10):
        ax.plot(t, yyy*ones(y.shape), dip(yyy,t, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), '-k', linewidth=1, alpha=0.1)
        ax.plot(t, yyy*ones(y.shape), dip(yyy,t, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), '-k', linewidth=1, alpha=0.1)
        ax.plot(t, yyy*ones(y.shape), dip(yyy,t, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r), '-k', linewidth=1, alpha=0.1)

    # Set the view
    ax.view_init(elev=elev, azim=azim)


    ax.set_ylabel("log(%s)[M]"%mcmc_data['drug1_name'].values[0])
    ax.set_xlabel("log(%s)[M]"%mcmc_data['drug2_name'].values[0])
    ax.set_zlabel("DIP " + r'$h^{-1}$')


    # Scatter points, and get error_bars
    scat_d1 = np.log10(hts_data['drug1.conc'])
    scat_d1.loc[scat_d1==-np.inf] = scat_d1.loc[scat_d1!=-np.inf].min()-zero_conc
    scat_d2 = np.log10(hts_data['drug2.conc'])
    scat_d2.loc[scat_d2==-np.inf] = scat_d2.loc[scat_d2!=-np.inf].min()-zero_conc
    scat_dip = hts_data['rate']
    scat_erb = hts_data['rate.95ci']
    ax.scatter(scat_d2, scat_d1, scat_dip, s=5, depthshade=True)

    # Plot error bars
    for _d1, _d2, _dip, _erb in zip(scat_d1, scat_d2, scat_dip, scat_erb):
        ax.plot([_d2,_d2], [_d1,_d1], [_dip-_erb, _dip+_erb], 'k-', alpha=0.3,linewidth=1)


    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])

    # Plane of DIP=0
    c_plane = colorConverter.to_rgba('k', alpha=0.2)
    verts = [array([(d2_min-zero_conc,d1_min-zero_conc), (d2_min-zero_conc,d1_max), (d2_max,d1_max), (d2_max,d1_min-zero_conc), (d2_min-zero_conc,d1_min-zero_conc)])]
    poly = PolyCollection(verts, facecolors=c_plane)
    ax.add_collection3d(poly, zs=[0], zdir='z')

    # Plot intersection of surface with DIP=0 plane
    CS = contour(tt,yy,zz,levels=[0], linewidths=3, colors='k')

    # If needed, manually set zlim
    if zlim is not None: ax.set_zlim(zlim)

    # Save plot, or show it
    if fname is None: show()
    else: plt.savefig(fname)
    clf()
    plt.close()

def plot_slices(mcmc_data, hts_data, drug_id, drug, N=50, fname=None, lw=1,zero_conc=1):
    e0, e1, e2, e3, h1, h2, r1, r1r, r2, r2r, ec50_1, ec50_2, alpha1, alpha2, beta, beta_obs, d1_min, d1_max, d2_min, d2_max, model_level, drug1_name, drug2_name, expt = get_params(mcmc_data)
    fig = figure(figsize=(1.5,1))
    y = linspace(d1_min-zero_conc, d1_max, N)
    t = linspace(d2_min-zero_conc, d2_max, N)    
    dip1_0 = dip(y,-10**zero_conc, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r)
    dip1_1 = dip(y,d2_max, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r)
    dip2_0 = dip(-10**zero_conc,t, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r)
    dip2_1 = dip(d1_max,t, e0, e1, e2, e3, h1, h2, alpha1, alpha2, r1, r1r, r2, r2r)    
    dip_max = np.max(np.asarray([dip1_0, dip1_1, dip2_0, dip2_1]))
    dip_min = np.min(np.asarray([dip1_0, dip1_1, dip2_0, dip2_1]))
    dip_min = min(dip_min, 0)
    dip_range = 0.05*(dip_max - dip_min)
    
    if drug_id == "drug2":
        left_drug = mcmc_data['drug1_name'].values[0]
        right_drug = drug    
    else:
        left_drug = drug
        right_drug = mcmc_data['drug2_name'].values[0]
    
    ax = fig.add_subplot(111)
    ax.plot(y, dip1_0, c="#ff7f0e", linewidth=lw, label="0uM %s"%right_drug)
    ax.plot(y, dip1_1, c="#2ca02c", linewidth=lw, label="%duM %s"%(np.power(10.,d2_max)*10**6, right_drug))
    ax.plot(y, 0*y, 'k--', alpha=0.7)
    ax.set_ylim(dip_min-dip_range, dip_max+dip_range)
    ax.set_xlim(y[0],y[-1])
    f = interpolate.interp1d(dip1_0,y)
    y1 = (max(dip1_0)-(max(dip1_0)-min(dip1_0))/2)
    x1 = f(y1)    
    plt.scatter(x1,y1,s=20,marker= 'o',color='#ff7f0e',zorder=100)
    plt.plot((x1,x1),(ax.get_ylim()),color = '#ff7f0e',linestyle='--')
    f = interpolate.interp1d(dip1_1,y)
    y1 = (max(dip1_1)-(max(dip1_1)-min(dip1_1))/2)
    x1 = f(y1)    
    plt.scatter(x1,y1,s=20,marker='o',color='#2ca02c',zorder=100)
    plt.plot((x1,x1),(ax.get_ylim()),color = '#2ca02c',linestyle='--')
    ax.set_ylabel(r'DIP ($h^{-1}$)')
    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.55),
          fancybox=False, shadow=False, ncol=1,handletextpad=0.01)
    ax.set_xlabel(r'log(%s)[M]'%left_drug)

    if fname is None: show()
    else: plt.savefig(right_drug+'_slices_'+fname)
    
    fig = figure(figsize=(1.5,1))
    ax = fig.add_subplot(111)
    ax.plot(t, dip2_0, c="#d62728", linewidth=lw, label="0uM %s"%left_drug)
    ax.plot(t, dip2_1, c="#9467bd", linewidth=lw, label="%duM %s"%(np.power(10.,d1_max)*10**6, left_drug))
    ax.plot(t, 0*t, 'k--', alpha=0.7)
    ax.set_ylim(dip_min-dip_range, dip_max+dip_range)
    ax.set_xlim(t[0],t[-1])
    
    f = interpolate.interp1d(dip2_0,t)
    y1 = (max(dip2_0)-(max(dip2_0)-min(dip2_0))/2)
    x1 = f(y1)    
    plt.scatter(x1,y1,s=20,marker= 'o',color='#d62728',zorder=100)
    plt.plot((x1,x1),(ax.get_ylim()),color = '#d62728',linestyle='--')
    f = interpolate.interp1d(dip2_1,t)
    y1 = (max(dip2_1)-(max(dip2_1)-min(dip2_1))/2)
    x1 = f(y1)    
    plt.scatter(x1,y1,s=20,marker='o',color='#9467bd',zorder=100)
    plt.plot((x1,x1),(ax.get_ylim()),color = '#9467bd',linestyle='--')
    
    ax.set_xlabel("log(%s)[M]"%right_drug)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.55),
          fancybox=False, shadow=False, ncol=1,handletextpad=0.01)
  #    
    if fname is None: show()
    else: plt.savefig(left_drug+'_slices_'+fname)

    
    return dip1_0, dip1_1, dip2_0, dip2_1


###Start Script

mcmc_data = pd.read_csv("../../Data/MasterResults_plx_dpi_melPanel.csv")
hts_data = pd.read_csv('../../Data/03-27-2018-dpi+plx_cm_bp_timeavg_preCalcDIP_timSub.csv')
#mcmc_data = mcmc_data.loc[mcmc_data['cell_line']=='SKMEL5_SC10']
mcmc_data = mcmc_data[mcmc_data['cell_line']=='A2058']
hts_data = hts_data[hts_data['cell.line']=='A2058']
mcmc_data['min_conc_d2']=min(hts_data['drug2.conc'][hts_data['drug2.conc']!=0])
mcmc_data['min_conc_d1']=min(hts_data['drug1.conc'][hts_data['drug1.conc']!=0])
drug = 'dpi'
drug_id = 'drug2'
plot_surface(mcmc_data, hts_data, drug_id, drug, fname="%s.pdf"%drug, zlim = (-0.01, 0.042),zero_conc=4)
plot_slices(mcmc_data, hts_data, drug_id, drug, fname="%s_slices.pdf"%drug,zero_conc=4)


########################################################################
####Surface plot interactive surface plots
########################################################################


#Import modules
#Either need the pydrc library in the same folder or add to search path...
#os.sys.path.append('/home/xnmeyer/Documents/Lab/Repos/pyDRC')
###Or for ACCRE
import numpy as np
import pandas as pd  #Make sure this is version 0.20.3 or higher
import plotly.graph_objs as go
from plotly.offline import  plot
import os

# 1D Hill function for fitting
def Edrug1D(d,E0,Em,C,h):
    return Em + (E0-Em) / (1 + (d/C)**h)

# 2D Hill function for fitting
def Edrug2D_DB(d,E0,E1,E2,E3,C1,C2,h1,h2,alpha):
    d1 = d[0]
    d2 = d[1]
    Ed = ( C1**h1*C2**h2*E0 + d1**h1*C2**h2*E1 + C1**h1*d2**h2*E2 + alpha**h2*d1**h1*d2**h2*E3 ) / \
                ( C1**h1*C2**h2 + d1**h1*C2**h2 + C1**h1*d2**h2 + alpha**h2*d1**h1*d2**h2 )
    return Ed
    
#2D dose response surface function not assuming detail balance but assuming proliferation 
# is << than the rate of transition between the different states.
def Edrug2D_NDB(d,E0,E1,E2,E3,r1,r2,C1,C2,h1,h2,alpha1,alpha2):
    d1 = d[0]
    d2 = d[1]
    Ed = (E3*r1*(alpha1*d2)**h2*(alpha2*d1**2)**h1 + 
          E3*r2*(alpha2*d1)**h1*(alpha1*d2**2)**h2 + 
          C2**h2*E0*r1*(C1*alpha2*d1)**h1 + 
          C1**h1*E0*r2*(C2*alpha1*d2)**h2 + 
          C2**h2*E1*r1*(alpha2*d1**2)**h1 + 
          C1**h1*E2*r2*(alpha1*d2**2)**h2 + 
          E3*d2**h2*r1*(C1*alpha2*d1)**h1 + 
          E3*d1**h1*r2*(C2*alpha1*d2)**h2 + 
          C1**(2*h1)*C2**h2*E0*r1 + 
          C1**h1*C2**(2*h2)*E0*r2 + 
          C1**(2*h1)*E2*d2**h2*r1 + 
          C2**(2*h2)*E1*d1**h1*r2 + 
          E1*r2*(C2*d2)**h2*(alpha2*d1)**h1 + 
          E2*r1*(C1*d1)**h1*(alpha1*d2)**h2 +
          C2**h2*E1*r1*(C1*d1)**h1 +
          C1**h1*E2*r2*(C2*d2)**h2)/  \
         (r1*(alpha1*d2)**h2*(alpha2*d1**2)**h1 + 
          r2*(alpha2*d1)**h1*(alpha1*d2**2)**h2 + 
          C2**h2*r1*(C1*alpha2*d1)**h1 +
          C1**h1*r2*(C2*alpha1*d2)**h2 + 
          C2**h2*r1*(alpha2*d1**2)**h1 + 
          C1**h1*r2*(alpha1*d2**2)**h2 + 
          d2**h2*r1*(C1*alpha2*d1)**h1 + 
          d1**h1*r2*(C2*alpha1*d2)**h2 + 
          C1**(2*h1)*C2**h2*r1 + 
          C1**h1*C2**(2*h2)*r2 + 
          C1**(2*h1)*d2**h2*r1 + 
          C2**(2*h2)*d1**h1*r2 + 
          r1*(C1*d1)**h1*(alpha1*d2)**h2 + 
          r2*(C2*d2)**h2*(alpha2*d1)**h1 + 
          C2**h2*r1*(C1*d1)**h1 + 
          C1**h1*r2*(C2*d2)**h2)
         
    return Ed

#####################################
#Function to plot the combination surface plots in plotly    
############################################################
def DosePlots_PLY(d1,d2,dip,dip_sd,drug1_name,drug2_name,popt3,which_model,target_cell_line,expt,metric_name):
    #To plot doses on log space
    t_d1 = d1.copy()
    t_d2 = d2.copy()
    t_d1[t_d1==0] = min(t_d1[t_d1!=0])/10
    t_d2[t_d2==0] = min(t_d2[t_d2!=0])/10

    trace1 = go.Scatter3d(x=np.log10(t_d1),y=np.log10(t_d2),z=dip,mode='markers',
                        marker=dict(size=3,color = dip,colorscale = 'coolwarm',
                                    line=dict(
                                              color='rgb(0,0,0)',width=1)),
                        )    
    #Plot the fit
    conc1 = 10**np.linspace(np.log10(min(t_d1)),np.log10(max(t_d1)), 30)
    conc2 = 10**np.linspace(np.log10(min(t_d2)), np.log10(max(t_d2)), 30)
    conc3 = np.array([(c1,c2) for c1 in conc1 for c2 in conc2])
    if which_model == 'DB':
        twoD_fit = np.array([Edrug2D_DB(d,*popt3) for d in conc3])
    elif which_model=='NDB':
        twoD_fit = np.array([Edrug2D_NDB(d,*popt3) for d in conc3])
        
    zl = [min(twoD_fit),max(twoD_fit)]
    twoD_fit = np.resize(twoD_fit, (len(conc1),len(conc2)))
    
    [X,Y] = np.meshgrid(np.log10(conc1), np.log10(conc2))

    trace2 = go.Surface(x=X,y=Y,z=twoD_fit.transpose(),
                      colorscale = 'coolwarm',
                      opacity=.8,
                      contours  = dict( 
                                        y = dict(highlight=False,show=False,color='#444',width=1),
                                        x = dict(highlight=False,show=False,color='#444',width = 1 ),
                                        z = dict(highlight=True,show=True,highlightwidth=4,width=3,usecolormap=False)
                                        ))

                      
    
    layout = go.Layout(
                       scene = dict(
                                    xaxis=dict(    
                                               range = [np.log10(min(t_d1)),np.log10(max(t_d1))],
                                               title = 'log(' + drug1_name + ')',
                                               autorange=True,
                                               showgrid=True,
                                               zeroline=False,
                                               showline=False,
                                               ticks='',
                                               showticklabels=True,
                                               gridwidth = 5,
                                               gridcolor = 'k'
                                    ),
                                    yaxis=dict(    
                                               range = [np.log10(min(t_d1)),np.log10(max(t_d1))],
                                               title = 'log(' + drug2_name + ')',
                                               autorange=True,
                                               showgrid=True,
                                               zeroline=False,
                                               showline=False,
                                               ticks='',
                                               showticklabels=True,
                                               gridwidth = 5,
                                               gridcolor = 'k'
                                    ),
                                    zaxis=dict(
                                               range = zl,
                                               title = metric_name,
                                               autorange=True,
                                               tick0=np.min(twoD_fit),
                                               dtick=(np.max(twoD_fit)-np.min(twoD_fit))/5,
                                               showgrid=True,
                                               zeroline=True,
                                               zerolinewidth=5,
                                               showline=False,
                                               ticks='',
                                               showticklabels=True,
                                               gridwidth=5,
                                               gridcolor = 'k'
                                    )
                                    ),
                    margin=dict(
                                l=0,
                                r=0,
                                b=0,
                                t=0
                    ),
                    showlegend=False,
                    font=dict(family='Arial', size=18),
                    title = target_cell_line
    )
        
                    
    data = [trace1,trace2]


    for e,i in enumerate(dip_sd):
        x = np.log10(t_d1[e])*np.ones((2,))
        y = np.log10(t_d2[e])*np.ones((2,))
        z = np.array([dip[e]+i,dip[e]-i])
        trace = go.Scatter3d(
            x=x, y=y, z=z,
            mode = 'lines',
            line=dict(
                color='#1f77b4',
                width=2
            )
        )
        data.append(trace)
    
    fig = go.Figure(data=data,layout=layout)
    
    camera = dict(
                  up=dict(x=0,y=0,z=1),
                  center=dict(x=0,y=0,z=0),
                  eye = dict(x=1.25,y=-1.25,z=1.25))
    fig['layout'].update(scene=dict(camera=camera))
    s_idx = expt.rfind(os.sep)
    expt = expt[s_idx+1:-4]
    plot(fig,filename = 'Plots/{}_{}_{}_{}_{}_plotly_doseResponseSurface.html'.format(target_cell_line,drug1_name,drug2_name,which_model,expt),auto_open=False)






####################################################
####################################################
####################################################    
####################################################
df = pd.read_csv('../../Data/MasterResults_plx_dpi_melPanel.csv')
for idx in df.index:
    ##Now plot the dose response slices...
    T = df.loc[idx].to_dict()
        
    #Should the dose response surfaces be plotted?
    to_plot = 1#Should the results be plotted?
    expt = '../../Data/' + T['expt']#Experiment file
    target_cell_line = T['cell_line']#The cell line to consider
    
    #Read in the data into a pandas data frame
    data = pd.read_table(expt, delimiter=',')
    data['cell.line'] = data['cell.line'].str.upper()
    data['drug1'] = data['drug1'].str.lower()
    data['drug2'] = data['drug2'].str.lower()
    #Subset by target cell line
    data = data[data['cell.line']==T['cell_line']]
    #data = data.reset_index()
    
    drug1_name = T['drug1_name']#Drug1 name to replace in array gen function
    drug2_name = T['drug2_name']#Drug2 name to replace in ArrayGen Function
    
    tmp_data = data[
                    ((data['drug1']=='control') & (data['drug2']=='control'))   | 
                    ((data['drug1']==drug1_name) & (data['drug2.conc']==0))    | 
                    ((data['drug2']==drug2_name) & (data['drug1.conc']==0))     |
                    ((data['drug2']==drug2_name) & (data['drug1']==drug1_name))
                    ]
    
    #tmp_data = tmp_data.reset_index() #Reset the data frame index
    d1 = tmp_data['drug1.conc'].values #Vector of drug 1 concentrations
    d2 = tmp_data['drug2.conc'].values #Vector of drug2 concentrations
    dip = tmp_data['rate'].values #Vector of the measured dip rate
    dip_95ci = tmp_data['rate.95ci'].values #Vector of the 95% confidence interval on the DIP fit.
    dip_sd = dip_95ci/(2*1.96)
        
    #Remove nan values
    d1      = d1[~np.isnan(dip)]
    d2      = d2[~np.isnan(dip)]
    dip_sd  = dip_sd[~np.isnan(dip)]
    dip     = dip[~np.isnan(dip)]
                  
    
    #Force all the drug names to lower case...
    drug1_name = drug1_name.lower()
    drug2_name = drug2_name.lower()
    #Force all the cell_line names to be upper case
    target_cell_line = target_cell_line.upper()
    
    
    mod_lev = T['model_level']           
    #If model level was less than 5, then it is some approximation of the Detail balance case.
    if mod_lev < 5:     
        popt3 = [ T['E0'],
                  T['E0_std'],
                  T['E1'],
                  T['E1_std'],
                  T['E2'],
                  T['E2_std'],
                  T['E3'],
                  T['E3_std'],
                  10**T['log_C1'],
                  np.log(10)*T['log_C1_std']*10**T['log_C1'],
                  10**T['log_C2'],
                  np.log(10)*T['log_C2_std']*10**T['log_C2'],
                  T['h1'],
                  T['h1_std'],
                  T['h2'],
                  T['h2_std'],
                  10**T['log_alpha1'],
                  np.log(10)*T['log_alpha1_std']*10**T['log_alpha1']]
        DosePlots_PLY(d1,d2,dip,dip_sd,drug1_name,drug2_name,popt3[0:17:2],'DB',target_cell_line,expt,'DIP rate (h-1)')
    elif mod_lev == 5: #It was best fit by a model which did not obey detail balance
        popt3 = [ T['E0'],
                  T['E0_std'],
                  T['E1'],
                  T['E1_std'],
                  T['E2'],
                  T['E2_std'],
                  T['E3'],
                  T['E3_std'],
                  T['r1'],
                  T['r1_std'],
                  T['r2'],
                  T['r2_std'],
                  10**T['log_C1'],
                  np.log(10)*T['log_C1_std']*10**T['log_C1'],
                  10**T['log_C2'],
                  np.log(10)*T['log_C2_std']*10**T['log_C2'],
                  T['h1'],
                  T['h1_std'],
                  T['h2'],
                  T['h2_std'],
                  10**T['log_alpha1'],
                  np.log(10)*T['log_alpha1_std']*10**T['log_alpha1'],
                  10**T['log_alpha2'],
                  np.log(10)*T['log_alpha2_std']*10**T['log_alpha2']]
        DosePlots_PLY(d1,d2,dip,dip_sd,drug1_name,drug2_name,popt3[0:23:2],'NDB',target_cell_line,expt,'DIP rate (h-1)')        
        
    else:
        popt3 = [ T['E0'],
                  T['E0_std'],
                  T['E1'],
                  T['E1_std'],
                  T['E2'],
                  T['E2_std'],
                  T['E3'],
                  T['E3_std'],
                  T['r1'],
                  T['r1_std'],
                  T['r2'],
                  T['r2_std'],
                  10**T['log_C1'],
                  np.log(10)*T['log_C1_std']*10**T['log_C1'],
                  10**T['log_C2'],
                  np.log(10)*T['log_C2_std']*10**T['log_C2'],
                  T['h1'],
                  T['h1_std'],
                  T['h2'],
                  T['h2_std'],
                  10**T['log_alpha1'],
                  np.log(10)*T['log_alpha1_std']*10**T['log_alpha1'],
                  10**T['log_alpha2'],
                  np.log(10)*T['log_alpha2_std']*10**T['log_alpha2'],
                  10**T['log_gamma1'],
                  np.log(10)*T['log_gamma1_std']*10**T['log_gamma1'],
                  10**T['log_gamma2'],
                  np.log(10)*T['log_gamma2_std']*10**T['log_gamma2']]
        DosePlots_PLY(d1,d2,dip,dip_sd,drug1_name,drug2_name,popt3[0:27:2],'NDB_hill',target_cell_line,expt,'DIP rate (h-1)')          
        


#####################################
#Function to plot the DSD for DPI+PLX 
############################################################
###Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from adjustText import adjust_text
font = {'family' : 'arial',
        'weight':'normal',
        'size'   : 8}
axes = {'linewidth': 3}
rc('font', **font)
rc('axes',**axes)

T = pd.read_csv('../../Data/MasterResults_plx_dpi_melPanel.csv')
cell_colors = {'SC01':'r','SC10':'b','SC07':(128./255.,0.,128./255.,1.),'A2058':'k','WM88':'k','SKMEL5':'k','WM115':'k','SKMEL5_2X':'k'}
plt.figure(figsize=(2.5,2),facecolor='w')
ax = []
ax.append(plt.subplot2grid((1,2),(0,0)))
ax.append(plt.subplot2grid((1,2),(0,1)))
plt.subplots_adjust(wspace=0,hspace=.4)
plt.sca(ax[0])
text = []
for i in T.index:
    plt.scatter(T['log_alpha2'].loc[i],T['beta_obs_norm'].loc[i],label=T['cell_line'].loc[i],zorder=-20,color=cell_colors[T['cell_line'].loc[i]])
    plt.errorbar(T['log_alpha2'].loc[i],T['beta_obs_norm'].loc[i],xerr=T['log_alpha2_std'].loc[i],yerr=T['beta_obs_norm_std'].loc[i],color='gray',capsize=0)
    text.append(plt.text(T['log_alpha2'].loc[i],T['beta_obs_norm'].loc[i],T['cell_line'].loc[i]))
x_lim = plt.xlim()
y_lim = plt.ylim()
y_lim = plt.ylim((y_lim[0]-.2,y_lim[1]))
plt.plot([0,0],y_lim,color='k',linestyle='--')
plt.plot(x_lim,[0,0],color='k',linestyle='--')
plt.xlabel('log($\\alpha_1$)\n(DPI potentiates PLX4720)')
plt.ylabel(r'$\beta_{obs}$')
ax[0].xaxis.set_ticks_position('bottom')
ax[0].yaxis.set_ticks_position('left')
adjust_text(text)

plt.sca(ax[1])
text = []
for i in T.index:
    plt.scatter(T['log_alpha1'].loc[i],T['beta_obs_norm'].loc[i],label=T['cell_line'].loc[i],zorder=-20,color=cell_colors[T['cell_line'].loc[i]])
    plt.errorbar(T['log_alpha1'].loc[i],T['beta_obs_norm'].loc[i],xerr=T['log_alpha1_std'].loc[i],yerr=T['beta_obs_norm_std'].loc[i],color='gray',capsize=0)
    text.append(plt.text(T['log_alpha1'].loc[i],T['beta_obs_norm'].loc[i],T['cell_line'].loc[i]))

y_lim = plt.ylim((y_lim[0],y_lim[1]))
x_lim = plt.xlim(x_lim)
ax[1].set_xticklabels([])
ax[1].set_yticks([])
plt.plot([0,0],y_lim,color='k',linestyle='--')
plt.plot(x_lim,[0,0],color='k',linestyle='--')
plt.xlabel('log($\\alpha_2$)\nPLX4720 potentiates DPI')
ax[1].xaxis.set_ticks_position('bottom')
ax[1].yaxis.set_ticks_position('left')
adjust_text(text)
plt.savefig('DSD_nox5_.pdf')

df = pd.read_csv('../../Data/nox5Expr.csv') 
df = df.rename(columns={'Cell':'cell_line'})
d = pd.merge(df,T,on='cell_line')
d[['beta_obs_norm','logN']].corr()


plt.figure(figsize=(2,2),facecolor='w')
import scipy.stats as stats
stats.pearsonr(d['beta_obs_norm'],d['logN'])
ax=plt.subplot(111)
for indx in d.index:
    ax.scatter(d['beta_obs_norm'].loc[indx],d['logN'].loc[indx],s=20,c='b',lw=2,zorder=-20)
    plt.errorbar(d['beta_obs_norm'].loc[indx],d['logN'].loc[indx],xerr=d['beta_obs_norm_std'].loc[indx],yerr=None,color='gray',capsize=0)
    plt.text(d['beta_obs_norm'].loc[indx],d['logN'].loc[indx],d['cell_line'].loc[indx])
plt.xlabel(r'$\beta_{obs}$')
plt.ylabel('NOX5 Expression')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
plt.savefig('syn_eff_NOX5_corr.pdf')


import scipy.stats as stats
stats.pearsonr(d['log_alpha2'],d['logN'])
plt.figure(figsize=(2,2),facecolor='w')
ax=plt.subplot(111)
for indx in d.index:
    ax.scatter(d['log_alpha2'].loc[indx],d['logN'].loc[indx],s=20,c='k',lw=2,edgecolor='k')
    plt.errorbar(d['log_alpha2'].loc[indx],d['logN'].loc[indx],xerr=d['log_alpha2'].loc[indx],yerr=None,color='gray',capsize=0)
    plt.text(d['log_alpha2'].loc[indx],d['logN'].loc[indx],d['cell_line'].loc[indx])
plt.xlabel(r'$log(\alpha_2)$')
plt.ylabel('NOX5 Expression')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xticks([-10,0,10])
ax.set_yticks([-2,0,2,4])
plt.xlim(-15,15)
plt.savefig('syn_potency_NOX5_corr.pdf')


#
#ind = ['NOX5']
#cl = [j.split('_')[0] for j in list(df)]
#for i in ind:
#    plt.figure(figsize = (1.5,1.5))
#    x = np.array(dip_rates)
#    y = np.array(df.loc[i])
#    text = []
#    for e in range(len(y)):
#        plt.scatter(x[e],y[e],s=2,c='b',edgecolor='k',lw=2)
#        text.append(plt.text(x[e],y[e],cl[e]))
##    adjust_text(text)
#    plt.xlabel('DIP Rate (8uM PLX)')
#    plt.ylabel('log(RPKM)' + i)
#    plt.savefig('DIP_corr_'+i+'.pdf')




