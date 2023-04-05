#! /usr/bin/env python3
import math, sys
from root_pandas import read_root
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

import PlotUtils as pu

def read(filepath, key,
	branchCats='ALL',
	branchesflat=None,
	### flatten the information to 2D df, for the convenience of usage
	verbose=1):
	
	pd.set_option('max_rows', 20)

	branches = 0
	if (branchCats=='ALL'):
		branches 	= ['*']
		branchesflat 	= branchesflat if branchesflat is not None \
			     else ['*']
	else:
		assert(isinstance(branchCats, list))
		branches = branchCats

	if(verbose): print('read branches: ', branches)

	Ntuple 	= read_root(filepath, key=key, columns=branches, flatten=branchesflat)

	if(verbose): print('Ntuple loaded (df): \n', Ntuple)

	return(Ntuple)


############################################## utils ##############################################
def plotVarsState(dataSpec, plotSpec, figname,
		nbinsDefault=40, yMaxScale=1.3,
		density=None,
		col_arr=None,
		bbox_to_anchor=(1.0,1.0)
		):
	'''
	a general function to plot all vars given dataSpec, plotSpec

	@param dataSpec 	[[ legend_name, data_df ] ...]
	@param plotSpec 	[[ var_name, var_title, range_config (, logy) ] ...]
	@param density 		None: no normalization, 1: such that area is 1, 2: divide by the numEntries
	'''
	pu.RegisterPltStyle(style_fontsize=18)
	plt.rcParams["figure.subplot.bottom"] = 0.25

	nplots 	= len(plotSpec)
	ncols	= 3 if nplots>=3 else nplots
	nrows	= math.ceil(nplots/3.)

	fig = plt.figure(figsize=(6*ncols, 4.5*nrows))
	plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
	grid_space = plt.GridSpec(nrows, ncols, wspace=0.5, hspace=0.3)

	for iplot, plot in enumerate(plotSpec):
		var_name, var_title, range_config = plot[0], plot[1], plot[2]
		print('{}-th plot: {}, {}, {}'.format(iplot, var_name, var_title, range_config))

		ax = fig.add_subplot(grid_space[ iplot//ncols, iplot%ncols ])
		for idata, data in enumerate(dataSpec):
			[ legend_name, data_df ] = data
			# print(legend_name, data_df)
			nbins = nbinsDefault if len(range_config)==2 else range_config[2]
			data2plot = data_df.eval(var_name)
			weights = np.ones_like(data2plot)/float(len(data2plot)) if (density==2) else None
			if (legend_name == 'data'):
				y, bin_edges = np.histogram(data2plot, bins=nbins, range=range_config[0:2])
				bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
				yerr 	= y**0.5/float(len(data2plot))
				y 	= y/float(len(data2plot))
				ax.errorbar(
				    bin_centers,
				    y,
				    yerr = yerr,
				    marker = '.',
				    drawstyle = 'steps-mid', fmt='o',
				    color='red',
				    ecolor='lightgray', elinewidth=3, capsize=0,
				    label=legend_name
				)
			else:
				y, bin_edges, _ = ax.hist(data2plot, bins=nbins,  histtype='step', range=range_config[0:2], label=legend_name, 
					density=(density==1), weights=weights,
					color=col_arr[idata] if col_arr is not None else None,
					linewidth=2)
		if (len(dataSpec)>1 and iplot==0): ax.legend(frameon=False, bbox_to_anchor=bbox_to_anchor, loc='upper right')
		if (len(plot)>=4 and plot[3]==True): plt.yscale('log')
		ax.set_xlim([ *(range_config[0:2]) ])
		ax.set_ylim(top=ax.get_ylim()[1]*yMaxScale)
		ax.set_xlabel(var_title)

	plt.savefig(figname)
	pu.Send2Dropbox(figname)


