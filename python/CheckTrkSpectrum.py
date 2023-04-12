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

# Sort tracks in terms of pT
def sortPt(x, 
	   sortColName,
	   trklist): 	
	   # np.array of object dtype of 
	   # np.array of various dtypes
	   # single event (row)
	x_trklist 	= x[trklist]
	sortedIdx 	= x_trklist[sortColName].argsort()[::-1]
	for trkCol in trklist:
		x_trklist[trkCol] = x_trklist[trkCol][sortedIdx]
	return(x_trklist)


# Select on high purity tracks
def cutHP( x, 
	   cutColName,
	   trklist): 	
	   # np.array of object dtype of 
	   # np.array of various dtypes
	   # single event (row)
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



def matchTrksRealReso( 	x1, # to check
		x2, # to ref.
		threshold=2 ): 	# 2 sigma
		# single event (row)
	matchVarArr = ['relTrkPt', 'relTrkDxy1', 'relTrkDz1']
	x1['relTrkPt'] 	= x1['trkPt']/x1['trkPtError']
	x2['relTrkPt'] 	= x2['trkPt']/x2['trkPtError']
	x1['relTrkDxy1']= x1['trkDxy1']/x1['trkDxyError1']
	x2['relTrkDxy1']= x2['trkDxy1']/x2['trkDxyError1']
	x1['relTrkDz1'] = x1['trkDz1']/x1['trkDzError1']
	x2['relTrkDz1'] = x2['trkDz1']/x2['trkDzError1']
	
	# print(x1.nEv, x2.nEv)
	x1_trklist 	= np.array([ ele for ele in x1[matchVarArr]])
	x2_trklist 	= np.array([ ele for ele in x2[matchVarArr]])
	x1_out 		= np.zeros(x1_trklist.shape[1])
	if (x2_trklist.shape[1]==0): return(x1_out)
	for it in range(x1_trklist.shape[1]):
		# if (it==10): sys.exit()
		trkParam = x1_trklist[:,it][:,None] ### column vector
		# print(trkParam)
		x1_out[it] = np.sum( np.multiply.reduce( abs(x2_trklist-trkParam) < threshold, axis=0 ) )
		# print(x2_trklist)
		# print(abs(x2_trklist-trkParam) < threshold)
		# print(np.multiply.reduce( abs(x2_trklist-trkParam) < threshold, axis=0 ))
		# print(x1_out[it])
	# print(x1_trklist)
	# print(x2_trklist)
	return(x1_out)

# print(matchTrksRealReso(df1_badReco.iloc[0], df2_badReco.loc[ df2_badReco.nEv==df1_badReco.iloc[0].nEv ].iloc[0]))
# sys.exit()


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
	df1_wellReco = df1[ df1.xVtx.values == df2.xVtx.values ]
	df2_wellReco = df2[ df1.xVtx.values == df2.xVtx.values ]
	df1_badReco  = df1[ ~(df1.xVtx.values == df2.xVtx.values) ]
	df2_badReco  = df2[ ~(df1.xVtx.values == df2.xVtx.values) ]
	print(df1_wellReco[['nEv', 'xVtx']])
	print(df2_wellReco[['nEv', 'xVtx']])
	print(df1_badReco[['nEv', 'trkPt']])
	print(df2_badReco[['nEv', 'trkPt']])


	################################################
	# 3. Track-level op: 
	################################################ 

	################################################ 
	# 3.0 Sort pT & cut HP
	################################################ 
	df1_badReco.loc[:,trklist] = df1_badReco.apply(lambda x: sortPt(x, 'trkPt', trklist), axis=1)
	df2_badReco.loc[:,trklist] = df2_badReco.apply(lambda x: sortPt(x, 'trkPt', trklist), axis=1)
	# print(df1_badReco[['nEv', 'trkPt', 'trkPtError', 'highPurity']].head(5).to_string())
	# print(df2_badReco[['nEv', 'trkPt', 'trkPtError', 'highPurity']].head(5).to_string())


	df1_badReco.loc[:,trklist] = df1_badReco.apply(lambda x: cutHP(x, 'highPurity', trklist), axis=1)
	df2_badReco.loc[:,trklist] = df2_badReco.apply(lambda x: cutHP(x, 'highPurity', trklist), axis=1)
	# print(df1_badReco[['nEv', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']].head(5).to_string())
	# print(df2_badReco[['nEv', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']].head(5).to_string())

	################################################ 
	# 3.1 Track matching
	################################################ 
	print('Doing track matching (for RAW) ... ')
	df1_badReco['trkMatched'] = df1_badReco.apply(lambda x: matchTrks(x, df2_badReco.loc[ x.nEv ]), axis=1)
	print('Doing track matching (for RAW\') ... ')
	df2_badReco['trkMatched'] = df2_badReco.apply(lambda x: matchTrks(x, df1_badReco.loc[ x.nEv ]), axis=1)
	# print(df1_badReco[['nEv', 'trkMatched', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']].head(5).to_string())
	# print(df2_badReco[['nEv', 'trkMatched', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']].head(5).to_string())
	
	################################################ 
	# 3.2 Flatten & calculate the canonical track parameters
	################################################ 
	df1_badReco = unnesting(df1_badReco, trklist+['trkMatched'])
	df2_badReco = unnesting(df2_badReco, trklist+['trkMatched'])

	def getTrackParam( df ):
		df['residChi2'] = df['trkChi2']/df['trkNdof']
		df['relTrkDxy1']= df['trkDxy1']/df['trkDxyError1']
		df['relTrkDz1'] = df['trkDz1']/df['trkDzError1']

	getTrackParam(df1_badReco)
	getTrackParam(df2_badReco)
	print(df1_badReco[['nEv', 'trkMatched', 'trkEta', 'trkPhi', 'trkPt', 'highPurity']])

	### bad vtx, well reco trk
	dnm.plotVarsState([['matched (RAW)',  df1_badReco[ df1_badReco.eval('trkMatched==1') ] ],
			   # ['matched (RAW\')',  df2_badReco[ df2_badReco.eval('trkMatched==1') ] ],
			   ['unmatched (RAW)',  df1_badReco[ df1_badReco.eval('trkMatched==0') ] ],
			   ['unmatched (RAW\')',  df2_badReco[ df2_badReco.eval('trkMatched==0') ] ]],
			[[ 'trkPt', 'trkPt', (0, 5)],
			 [ 'trkPtError', 'trkPtError', (0, 5)],
			 [ 'highPurity', 'highPurity', (0, 1)],
			 
			 [ 'trkNHit', 'trkNHit', (0, 30)],
			 [ 'trkEta', 'trkEta', (-5, 5)],
			 [ 'trkPhi', 'trkPhi', (-np.pi, np.pi)],

			 [ 'trkNlayer', 'trkNlayer', (0, 20)],
			 [ 'tight', 'tight', (0, 1)],
			 [ 'loose', 'loose', (0, 1)]],
			 'img/trkStatus_badVtx_trkRecoDetailed.pdf')
	pu.Send2Dropbox('img/trkStatus_badVtx_trkRecoDetailed.pdf')

	dnm.plotVarsState([['matched (RAW)',  df1_badReco[ df1_badReco.eval('trkMatched==1') ] ],
			   # ['matched (RAW\')',  df2_badReco[ df2_badReco.eval('trkMatched==1') ] ],
			   ['unmatched (RAW)',  df1_badReco[ df1_badReco.eval('trkMatched==0') ] ],
			   ['unmatched (RAW\')',  df2_badReco[ df2_badReco.eval('trkMatched==0') ] ]],
			[[ 'trkChi2', 'trkChi2', (0, 100)],
			 [ 'trkNdof', 'trkNdof', (0, 50)],
			 [ 'trkDxy1', 'trkDxy1', (-5, 5)],
			 
			 [ 'trkDxyError1', 'trkDxyError1', (0, 5)],
			 [ 'trkDz1', 'trkDz1', (-5, 5)],
			 [ 'trkDzError1', 'trkDzError1', (0, 5)],
			
			 [ 'trkFake', 'trkFake', (0, 1)],
			 [ 'trkAlgo', 'trkAlgo', (0, 25)],
			 [ 'trkOriginalAlgo', 'trkOriginalAlgo', (0, 25)]], 
			 'img/trkStatus_badVtx_trkRecoDetailed2.pdf')
	pu.Send2Dropbox('img/trkStatus_badVtx_trkRecoDetailed2.pdf')

	dnm.plotVarsState([['matched (RAW)',  df1_badReco[ df1_badReco.eval('trkMatched==1') ] ],
			   # ['matched (RAW\')',  df2_badReco[ df2_badReco.eval('trkMatched==1') ] ],
			   ['unmatched (RAW)',  df1_badReco[ df1_badReco.eval('trkMatched==0') ] ],
			   ['unmatched (RAW\')',  df2_badReco[ df2_badReco.eval('trkMatched==0') ] ]],
			[[ 'trkPt', 'trkPt (log-scale)', (0, 1e4), True],
			 [ 'trkPtError', 'trkPtError (log-scale)', (0, 1e4), True]],
			 'img/trkStatus_badVtx_trkRecoPt.pdf')
	pu.Send2Dropbox('img/trkStatus_badVtx_trkRecoPt.pdf')


	df1_badReco_wellRecoTrk = df1_badReco[ df1_badReco.eval('trkMatched==1') ][:30000]
	# print(df1_badReco_wellRecoTrk.to_string())
	with open('out/df1_badReco_flatten_wellRecoTrk.txt', 'w') as f:
		f.write(df1_badReco_wellRecoTrk.to_string())

	df1_badReco_badRecoTrk = df1_badReco[ df1_badReco.eval('trkMatched==0') ][:30000]
	# print(df1_badReco_badRecoTrk.to_string())
	with open('out/df1_badReco_flatten_badRecoTrk.txt', 'w') as f:
		f.write(df1_badReco_badRecoTrk.to_string())

	df2_badReco_wellRecoTrk = df2_badReco[ df2_badReco.eval('trkMatched==1') ][:30000]
	# print(df2_badReco_wellRecoTrk.to_string())
	with open('out/df2_badReco_flatten_wellRecoTrk.txt', 'w') as f:
		f.write(df2_badReco_wellRecoTrk.to_string())

	df2_badReco_badRecoTrk = df2_badReco[ df2_badReco.eval('trkMatched==0') ][:30000]
	# print(df2_badReco_badRecoTrk.to_string())
	with open('out/df2_badReco_flatten_badRecoTrk.txt', 'w') as f:
		f.write(df2_badReco_badRecoTrk.to_string())




	##### less info
	lessinfoArr = [ 'nEv', 'nVtx', 'nTrk', 'xVtx', 'yVtx', 'zVtx',
			'trkPt', 'trkEta', 'trkNHit', 'trkNlayer', 'highPurity' ]
	# print(df1_badReco_wellRecoTrk[ lessinfoArr ].to_string())
	with open('out/df1_badReco_flatten_wellRecoTrk_lessinfo.txt', 'w') as f:
		f.write(df1_badReco_wellRecoTrk[ lessinfoArr ].to_string())

	# print(df1_badReco_badRecoTrk[ lessinfoArr ].to_string())
	with open('out/df1_badReco_flatten_badRecoTrk_lessinfo.txt', 'w') as f:
		f.write(df1_badReco_badRecoTrk[ lessinfoArr ].to_string())

	# print(df2_badReco_wellRecoTrk[ lessinfoArr ].to_string())
	with open('out/df2_badReco_flatten_wellRecoTrk_lessinfo.txt', 'w') as f:
		f.write(df2_badReco_wellRecoTrk[ lessinfoArr ].to_string())

	# print(df2_badReco_badRecoTrk[ lessinfoArr ].to_string())
	with open('out/df2_badReco_flatten_badRecoTrk_lessinfo.txt', 'w') as f:
		f.write(df2_badReco_badRecoTrk[ lessinfoArr ].to_string())


if __name__ == '__main__':
	main()


