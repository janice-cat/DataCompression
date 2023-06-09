#! /usr/bin/env python3
import numpy as np
from root_pandas import read_root
import pandas as pd
import argparse
from glob import glob

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os, sys
sys.path.append('utils/')
import DfNtupleMgr as dnm
import PlotUtils as pu

from  itertools import chain

############# op's on single row #############
def sort( x, 
	  sortColName,
	  trklist): 	
	x_trklist 	= x[trklist]
	sortedIdx 	= x_trklist[sortColName].argsort()[::-1]
	for trkCol in trklist:
		x_trklist[trkCol] = x_trklist[trkCol][sortedIdx]
	return(x_trklist)


# Select on high purity tracks
def cut( x, 
	  cutColName,
	  trklist): 	
	x_trklist 	= x[trklist]
	cutIdx 		= x_trklist[cutColName]
	for trkCol in trklist:
		x_trklist[trkCol] = x_trklist[trkCol][cutIdx]
	return(x_trklist)

def matchTrks( 	x1, # to check
		x2, # to ref.
		# matchVarArr,
		threshold=0.01 ): 	
		# single event (row)
	# print(x1.nEv, x2.nEv)
	matchVarArr = ['trkPt', 'trkEta', 'trkPhi']
	x1_trklist 	= np.array([ ele for ele in x1[matchVarArr]])
	x2_trklist 	= np.array([ ele for ele in x2[matchVarArr]])
	x1_out 		= np.zeros(x1_trklist.shape[1])
	if (x2_trklist.shape[1]==0): return(x1_out)
	for it in range(x1_trklist.shape[1]):
		trkParam = x1_trklist[:,it][:,None] ### column vector
		x1_out[it] = np.sum( np.multiply.reduce( abs((x2_trklist-trkParam)/trkParam) < threshold, axis=0 ) )
	# print(x1_trklist)
	# print(x2_trklist)
	return(x1_out)
############# op's on single row #############

def unnesting(df, explode):
	idx = df.index.repeat(df[explode[0]].str.len())
	df1 = pd.concat([
		pd.DataFrame({x: np.concatenate(df[x].values)}) for x in explode], axis=1 )
	df1.index = idx
	return df1.join(df.drop(explode, 1), how='left')


def main():
	parser = argparse.ArgumentParser(prog='CheckVtxMismatchTrk.py')
	# parser.add_argument('-f1', 	help='***.root (RAW root path)')
	# parser.add_argument('-f2', 	help='***.root (RAWPrime root path)')
	args = parser.parse_args()

	f1 = '/eos/cms/store/group/phys_heavyions_ops/abaty/Dec6_afterTestRunChecks/Forests/RAW.root'
	f2 = '/eos/cms/store/group/phys_heavyions_ops/abaty/Dec6_afterTestRunChecks/Forests/RAWPrime.root'


	### event level ###
	evtlist 	= [ 'nEv', 'nRun', 'nLumi', 'nVtx', 'nTrk', 'N']

	### vertex level ###
	vtxlist 	= [ 'xVtx', 'yVtx', 'zVtx', 
			    'xVtxErr', 'yVtxErr', 'zVtxErr' ]
	### track level ###
	trklist 	= [ 'trkPt', 'trkPtError', 'highPurity', 'trkNHit',
			    'trkNlayer', 'trkEta', 'trkPhi',
			    'trkCharge', 'trkNVtx',
			    'tight', 'loose',
			    'trkChi2', 'trkNdof', 'trkDxy1', 'trkDxyError1', 'trkDz1', 'trkDzError1',
			    'trkFake', 'trkAlgo', 'trkOriginalAlgo' ]


	################################################
	# 1. Event-level matching   : look at the common events btw RAW & RAW'
	################################################ 
	df1 = dnm.read(f1, 'ppTrack/trackTree', evtlist+vtxlist+trklist)#[:50]
	df2 = dnm.read(f2, 'ppTrack/trackTree', evtlist+vtxlist+trklist)#[:50]

	### speed up by looking at only nVtx==1 event
	### then vertex level info becomes event level
	df1 = df1[ df1.eval('nVtx==1') ]
	df2 = df2[ df2.eval('nVtx==1') ]
	df1 = unnesting(df1, vtxlist)
	df2 = unnesting(df2, vtxlist)

	### scan the overlap events
	df1 = df1[ df1.nEv.isin(df2.nEv) ]
	df2 = df2[ df2.nEv.isin(df1.nEv) ]
	df1 = df1.sort_values(by=['nEv'])
	df2 = df2.sort_values(by=['nEv'])
	df1 = df1.set_index('nEv', drop=False)
	df2 = df2.set_index('nEv', drop=False)

	################################################
	# 2. Vertex-level matching  : look at the disagreed vertices (badReco)
	################################################ 
	df1_wellReco = df1[ df1.xVtx.values == df2.xVtx.values ].copy(deep=True)
	df2_wellReco = df2[ df1.xVtx.values == df2.xVtx.values ].copy(deep=True)
	df1, df2  = df1[ ~(df1.xVtx.values == df2.xVtx.values) ], \
		    df2[ ~(df1.xVtx.values == df2.xVtx.values) ]
	print('RAW  , wellReco:\n', df1_wellReco[['nEv', 'xVtx']])
	print('RAW\', wellReco:\n', df2_wellReco[['nEv', 'xVtx']])
	print('RAW  , badReco:\n', df1[['nEv', 'trkPt']])
	print('RAW\', badReco:\n', df2[['nEv', 'trkPt']])


	################################################
	# 3. Track-level op: 
	################################################ 

	################################################ 
	# 3.0 Sort pT & cut HP
	################################################ 
	df1.loc[:,trklist] = df1.apply(lambda x: sort(x, 'trkPt', trklist), axis=1)
	df2.loc[:,trklist] = df2.apply(lambda x: sort(x, 'trkPt', trklist), axis=1)
	# print(df1[['nEv', 'trkPt', 'trkPtError', 'highPurity']].head(5).to_string())
	# print(df2[['nEv', 'trkPt', 'trkPtError', 'highPurity']].head(5).to_string())


	df1.loc[:,trklist] = df1.apply(lambda x: cut(x, 'highPurity', trklist), axis=1)
	df2.loc[:,trklist] = df2.apply(lambda x: cut(x, 'highPurity', trklist), axis=1)
	# print(df1[['nEv', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']].head(5).to_string())
	# print(df2[['nEv', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']].head(5).to_string())

	################################################ 
	# 3.1 Track matching
	################################################ 
	print('Doing track matching (for RAW) ... ')
	df1.loc[:,'trkMatched'] = df1.apply(lambda x: matchTrks(x, df2.loc[ x.nEv ]), axis=1)
	print('Doing track matching (for RAW\') ... ')
	df2.loc[:,'trkMatched'] = df2.apply(lambda x: matchTrks(x, df1.loc[ x.nEv ]), axis=1)
	# print(df1[['nEv', 'trkMatched', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']].head(5).to_string())
	# print(df2[['nEv', 'trkMatched', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']].head(5).to_string())
	
	################################################ 
	# 3.2 Flatten & calculate the canonical track parameters
	################################################ 
	df1 = unnesting(df1, trklist+['trkMatched'])
	df2 = unnesting(df2, trklist+['trkMatched'])

	def getTrackParam( df ):
		df['residChi2'] = df['trkChi2']/df['trkNdof']
		df['relTrkDxy1']= df['trkDxy1']/df['trkDxyError1']
		df['relTrkDz1'] = df['trkDz1']/df['trkDzError1']

	getTrackParam(df1)
	getTrackParam(df2)
	print(df1[['nEv', 'trkMatched', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']])
	print(df2[['nEv', 'trkMatched', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']])


	def plot(dataspec, 
		 col_arr=None, 
		 postfix=''):

		### bad vtx, well reco trk
		dnm.plotVarsState(dataspec,
				[[ 'trkPt', 'trkPt', (0, 5)],
				 [ 'trkPtError', 'trkPtError', (0, 5)],
				 [ 'highPurity', 'highPurity', (0, 1)],
				 
				 [ 'trkNHit', 'trkNHit', (0, 30)],
				 [ 'trkEta', 'trkEta', (-5, 5)],
				 [ 'trkPhi', 'trkPhi', (-np.pi, np.pi)],

				 [ 'trkNlayer', 'trkNlayer', (0, 20)],
				 [ 'tight', 'tight', (0, 1)],
				 [ 'loose', 'loose', (0, 1)]],
				 'img/trkStatus_badVtx_trkRecoDetailed'+postfix+'.pdf',
				 col_arr=col_arr)
		pu.Send2Dropbox('img/trkStatus_badVtx_trkRecoDetailed'+postfix+'.pdf')

		dnm.plotVarsState(dataspec,
				[[ 'trkChi2', 'trkChi2', (0, 100)],
				 [ 'trkNdof', 'trkNdof', (0, 50)],
				 [ 'trkDxy1', 'trkDxy1', (-5, 5)],
				 
				 [ 'trkDxyError1', 'trkDxyError1', (0, 5)],
				 [ 'trkDz1', 'trkDz1', (-5, 5)],
				 [ 'trkDzError1', 'trkDzError1', (0, 5)],
				
				 [ 'trkFake', 'trkFake', (0, 1)],
				 [ 'trkAlgo', 'trkAlgo', (0, 25)],
				 [ 'trkOriginalAlgo', 'trkOriginalAlgo', (0, 25)]], 
				 'img/trkStatus_badVtx_trkRecoDetailed2'+postfix+'.pdf',
				 col_arr=col_arr)
		pu.Send2Dropbox('img/trkStatus_badVtx_trkRecoDetailed2'+postfix+'.pdf')

		dnm.plotVarsState(dataspec,
				[[ 'trkPt', 'trkPt (log-scale)', (0, 1e4), True],
				 [ 'trkPtError', 'trkPtError (log-scale)', (0, 1e4), True]],
				 'img/trkStatus_badVtx_trkRecoPt'+postfix+'.pdf',
				 col_arr=col_arr)
		pu.Send2Dropbox('img/trkStatus_badVtx_trkRecoPt'+postfix+'.pdf')

		dnm.plotVarsState(dataspec,
				[[ 'trkPt', 'trkPt', (0, 5)],
				 [ 'trkEta', 'trkEta', (-5, 5)],
				 [ 'trkPhi', 'trkPhi', (-np.pi, np.pi)],

				 [ 'trkPtError', 'trkPtError', (0, 0.5)],
				 [ 'trkNHit', 'trkNHit', (0, 30)],
				 [ 'trkNlayer', 'trkNlayer', (0, 20)],

				 [ 'trkChi2', 'trkChi2', (0, 100)],
				 [ 'trkNdof', 'trkNdof', (0, 50)],
				 [ 'highPurity', 'highPurity', (0, 1)],
				 
				 [ 'residChi2', r'$\chi^2/{\rm NDF}$', (0, 5)],
				 [ 'trkAlgo', 'trkAlgo', (0, 25)],
				 [ 'trkOriginalAlgo', 'trkOriginalAlgo', (0, 25)],

				 [ 'relTrkDxy1', 'trkDxy1/trkDxyError1', (0, 5)],
				 [ 'relTrkDz1', 'trkDz1/trkDzError1', (0, 5)]],
				 'img/trkStatus_badVtx_trkRecoCanonical'+postfix+'.pdf',
				 col_arr=col_arr)
		pu.Send2Dropbox('img/trkStatus_badVtx_trkRecoCanonical'+postfix+'.pdf')



	plot( [ ['matched (RAW)',  df1[ df1.eval('trkMatched==1') ] ],
		['matched (RAW\')',  df2[ df2.eval('trkMatched==1') ] ],
		['unmatched (RAW)',  df1[ df1.eval('trkMatched==0') ] ],
		['unmatched (RAW\')',  df2[ df2.eval('trkMatched==0') ] ] ],
		col_arr=[(0.17254901960784313, 0.6274509803921569, 0.17254901960784313), 
			 (0.17254901960784313, 0.6274509803921569, 0.17254901960784313, 0.5), 
			 (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
			 (1.0, 0.4980392156862745, 0.054901960784313725)], 
		postfix='_wMatching' )
	plot( [ ['RAW', df1],
		['RAW\'', df2] ] )

	df1_wellRecoTrk = df1[ df1.eval('trkMatched==1') ][:30000]
	# print(df1_wellRecoTrk.to_string())
	with open('out/df1_badReco_flatten_wellRecoTrk.txt', 'w') as f:
		f.write(df1_wellRecoTrk.to_string())

	df1_badRecoTrk = df1[ df1.eval('trkMatched==0') ][:30000]
	# print(df1_badRecoTrk.to_string())
	with open('out/df1_badReco_flatten_badRecoTrk.txt', 'w') as f:
		f.write(df1_badRecoTrk.to_string())

	df2_wellRecoTrk = df2[ df2.eval('trkMatched==1') ][:30000]
	# print(df2_wellRecoTrk.to_string())
	with open('out/df2_badReco_flatten_wellRecoTrk.txt', 'w') as f:
		f.write(df2_wellRecoTrk.to_string())

	df2_badRecoTrk = df2[ df2.eval('trkMatched==0') ][:30000]
	# print(df2_badRecoTrk.to_string())
	with open('out/df2_badReco_flatten_badRecoTrk.txt', 'w') as f:
		f.write(df2_badRecoTrk.to_string())




	##### less info
	lessinfoArr = [ 'nEv', 'nVtx', 'nTrk', 'xVtx', 'yVtx', 'zVtx',
			'trkPt', 'trkEta', 'trkNHit', 'trkNlayer', 'highPurity' ]
	# print(df1_wellRecoTrk[ lessinfoArr ].to_string())
	with open('out/df1_badReco_flatten_wellRecoTrk_lessinfo.txt', 'w') as f:
		f.write(df1_wellRecoTrk[ lessinfoArr ].to_string())

	# print(df1_badRecoTrk[ lessinfoArr ].to_string())
	with open('out/df1_badReco_flatten_badRecoTrk_lessinfo.txt', 'w') as f:
		f.write(df1_badRecoTrk[ lessinfoArr ].to_string())

	# print(df2_wellRecoTrk[ lessinfoArr ].to_string())
	with open('out/df2_badReco_flatten_wellRecoTrk_lessinfo.txt', 'w') as f:
		f.write(df2_wellRecoTrk[ lessinfoArr ].to_string())

	# print(df2_badRecoTrk[ lessinfoArr ].to_string())
	with open('out/df2_badReco_flatten_badRecoTrk_lessinfo.txt', 'w') as f:
		f.write(df2_badRecoTrk[ lessinfoArr ].to_string())


if __name__ == '__main__':
	main()


