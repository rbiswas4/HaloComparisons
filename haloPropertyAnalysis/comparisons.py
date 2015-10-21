#!/usr/bin/env python
import os
import glob
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from .utils import fracPoissonErrors

__all__ = ['Sim', 'CompareSims']
class Sim(object):
    """
    Class to describe Simulation with Mass Functions


    Parameters
    ----------
    simulationDir : string, mandatory
        Directory in which Mass Function Results calculated by HaloPy are
        stored
    name : A Name given to the particular simulation


    """
    def __init__(self, simulationDir, name, filelist=None):
        self.simDir = simulationDir
        self.name = name
        if filelist is None:
            print(self.simDir)
            filelist = glob.glob(self.simDir + '/*_mf')
        self.filelist = filelist

    def mf_fname(self, stepnum):
        filelist = self.filelist
        #print filelist
        ind = map(lambda x: str(stepnum) in x, filelist).index(True)
        fname = filelist[ind]
        return fname

    def mf_results(self, stepnum):
        """

        Parameters
        ----------
        stepnum : 
        """
        fname = self.mf_fname(stepnum)
        names = ['FOF_Mass', 'numClusters', 'dndlnM', 'frac_Err', 'oneoversigma', 'f(sigma)', 'fsigma_fit', 'dn/dln_Mfit']
        df  = pd.DataFrame(np.loadtxt(fname)[:, :-1], columns=names, index=None)
        return df

    def massrange(self, stepnum):
        df = self.mf_results(stepnum)
        return min(df.FOF_Mass.values), max(df.FOF_Mass.values)

    def interpolated_MF(self, stepnum):
        df = self.mf_results(stepnum)
        mass, massfn = df['FOF_Mass'].values, df['dndlnM']
        return interp1d(np.log(mass), np.log(massfn))


class CompareSims(object):

    def __init__(self, Sim1, Sim2, steps=[499, 247, 163]):
        self.sim1 = Sim1
        self.sim2 = Sim2
        self.sim1name = Sim1.name
        self.sim2name = Sim2.name
        self.steps = steps
        #print (steps)

    @property
    def comparisons(self):
        steps = self.steps

        df = self.calcSuppression(steps[0])
        for step in steps[1:]:
            df = df.append(self.calcSuppression(step))

        return df
    def calcSuppression(self, stepnum):

        df1 = self.sim1.mf_results(stepnum)
        df2 = self.sim2.mf_results(stepnum)
        mass1 = df1.FOF_Mass.values
        mass2 = df2.FOF_Mass.values
        mf1 = df1.dndlnM.values
        mf2 = df2.dndlnM.values
        numClusters2 = df2.numClusters
        
        # Note interpolation is not possible if mass2 is outside the range
        # of mass1. So return np.nan values
        mf2interp = np.empty(len(mass1))
        mf2interp[:] = np.nan
        mask = (mass1 > min(mass2))& (mass1 < max(mass2))

        # Interpolation done in log space
        mf2interp[mask] = np.exp(self.sim2.interpolated_MF(stepnum)(np.log(mass1[mask])))
        names = [self.sim1name + '_mass',
                 self.sim1name + '_MF',
                 self.sim2name + '_mass',
                 self.sim2name + '_MF',
                 self.sim2name + '_InterpMF']
    
        dfdict = dict()
        dfdict[names[0]] = mass1
        dfdict[names[1]] = mf1
        dfdict[names[2]] = mass2
        dfdict[names[3]] = mf2
        dfdict[names[4]] = mf2interp
        dfdict['numClusters1'] = df1.numClusters.values
        dfdict['numClusters2'] = df2.numClusters.values
        fracErrors1 = fracPoissonErrors(dfdict['numClusters1'])
        fracErrors2 = fracPoissonErrors(dfdict['numClusters2'])
        combinederr = mf2interp * np.sqrt((fracErrors1 )**2 +
                                          (fracErrors2 )**2 ) / mf1
        dfdict['directRatio'] = mf2 / mf1
        dfdict['interpolatedRatio'] = mf2interp / mf1
        dfdict['ApproxErrorLow'] = combinederr[0, :]
        dfdict['ApproxErrorHigh'] = combinederr[1, :]
        # for key in dfdict.keys():
        #    print(key, len(dfdict[key]))
        df = pd.DataFrame(dfdict)
        df['stepNum'] = stepnum
        return df

    def plotSuppression(self):

        df = self.comparisons
        grouped  = df.groupby('stepNum')
        steps = np.sort(grouped.groups.keys())[::-1]
        numSteps = len(steps)

        fig, (ax) = plt.subplots(numSteps, 1, sharex=True)
        for ind, step in enumerate(steps):
            res = grouped.get_group(step)
            ax[ind].errorbar(res[self.sim1name + '_mass'],
                             res['interpolatedRatio'],
                             yerr=(res['ApproxErrorLow'], res['ApproxErrorHigh']),
                             fmt='bo')
            ax[ind].set_title("step = {0:3d}".format(step))
            ax[ind].plot(res[self.sim1name + '_mass'], res['directRatio'],'r+')
            ax[ind].set_xscale('log')
            ax[ind].set_ylim(0.65, 1.0)
            ax[ind].grid(True)

        ax[-1].set_xlabel(r'$\rm{Mass} (M_\odot/h)$')
        fig.tight_layout(pad=0.)
        ax[1].set_ylabel('dn/dlnM('+self.sim2name + ')/dn/dlnM(' + self.sim1name +')' )
        return fig
    
