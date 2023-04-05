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

def main():
	parser = argparse.ArgumentParser(prog='CheckVtxTrk.py')
	# parser.add_argument('-f1', 	help='***.root (RAW root path)')
	# parser.add_argument('-f2', 	help='***.root (RAWPrime root path)')
	args = parser.parse_args()

	f1 = '/eos/cms/store/group/phys_heavyions_ops/abaty/Dec6_afterTestRunChecks/Forests/RAW.root'
	f2 = '/eos/cms/store/group/phys_heavyions_ops/abaty/Dec6_afterTestRunChecks/Forests/RAWPrime.root'


	### event level ###
	evtlist 	= [ 'nEv', 'nRun', 'nLumi', 'nVtx', 'nTrk', 'N']

	### vertex level ###
	vtxlist 	= [ 
			'xVtx', 'yVtx', 'zVtx',
			'xVtxErr', 'yVtxErr', 'zVtxErr' ]
	### track level ###
	trklist 	= [ 'trkPt', 'trkPtError', 'highPurity', 'trkNHit' ]

	Ntuple1evt = dnm.read(f1, 'ppTrack/trackTree', evtlist)
	Ntuple2evt = dnm.read(f2, 'ppTrack/trackTree', evtlist)

	Ntuple1vtx = dnm.read(f1, 'ppTrack/trackTree', evtlist+vtxlist, branchesflat=vtxlist)
	Ntuple2vtx = dnm.read(f2, 'ppTrack/trackTree', evtlist+vtxlist, branchesflat=vtxlist)
	
	Ntuple1trk = dnm.read(f1, 'ppTrack/trackTree', evtlist+trklist, branchesflat=trklist)
	Ntuple2trk = dnm.read(f2, 'ppTrack/trackTree', evtlist+trklist, branchesflat=trklist)

	def plot(Ntuple1evt, Ntuple2evt, 
		 Ntuple1vtx, Ntuple2vtx, 
		 Ntuple1trk, Ntuple2trk,
		 tagname ):

		print('RAW (evt):\n', Ntuple1evt)
		print('RAW prime (evt):\n', Ntuple2evt)
		print('RAW (vtx):\n', Ntuple1vtx)
		print('RAW prime (vtx):\n', Ntuple2vtx)

		### event level info
		dnm.plotVarsState([['RAW',   Ntuple1evt],
				   ['RAW\'', Ntuple2evt]],
				[[ 'nEv', 'Event', (0, 200*1e6)],
				 [ 'nRun', 'Run', (362320, 362323)],
				 [ 'nLumi', 'Lumi', (0, 400)],
				 [ 'nTrk', 'nTrk', (0, 14000)],
				 [ 'nVtx', 'nVtx', (0, 7)],
				 [ 'N', 'N', (0, 4000)],
				 [ 'nTrk', 'nTrk (log-scale)', (0, 14000), True],
				 [ 'nVtx', 'nVtx (log-scale)', (0, 10), True],
				 [ 'N', 'N (log-scale)', (0, 4000), True]],
				 'img/eventStatus'+tagname+'.pdf')
		pu.Send2Dropbox('img/eventStatus'+tagname+'.pdf')

		### vertex level info
		dnm.plotVarsState([['RAW',   Ntuple1vtx],
				   ['RAW\'', Ntuple2vtx]],
				[[ 'xVtx', 'Vertex X', (-0.4, 0.8)],
				 [ 'yVtx', 'Vertex Y', (-0.6, 0.6)],
				 [ 'zVtx', 'Vertex Z', (-20, 20)],
				 [ 'xVtxErr', 'X Error', (0, 0.03)],
				 [ 'yVtxErr', 'Y Error', (0, 0.03)],
				 [ 'zVtxErr', 'Z Error', (0, 0.03)]],
				 'img/vtxStatus'+tagname+'.pdf')
		pu.Send2Dropbox('img/vtxStatus'+tagname+'.pdf')

		### track level info
		dnm.plotVarsState([['RAW',   Ntuple1trk],
				   ['RAW\'', Ntuple2trk]],
				[[ 'trkPt', 'trkPt', (0, 5)],
				 [ 'trkPtError', 'trkPtError', (0, 5)],
				 [ 'highPurity', 'highPurity', (0, 1)],
				 [ 'trkPt', 'trkPt (log-scale)', (0, 5), True],
				 [ 'trkPtError', 'trkPtError (log-scale)', (0, 5), True]],
				 'img/trkStatus'+tagname+'.pdf')
		pu.Send2Dropbox('img/trkStatus'+tagname+'.pdf')


		### vertex level info
		dnm.plotVarsState([['RAW',   Ntuple1vtx],
				   ['RAW\'', Ntuple2vtx]],
				[[ 'xVtx', 'Vertex X', (-0.4, 0.8), True],
				 [ 'yVtx', 'Vertex Y', (-0.6, 0.6), True],
				 [ 'zVtx', 'Vertex Z', (-20, 20), True],
				 [ 'xVtxErr', 'X Error', (0, 0.03), True],
				 [ 'yVtxErr', 'Y Error', (0, 0.03), True],
				 [ 'zVtxErr', 'Z Error', (0, 0.03), True]],
				 'img/vtxStatus-logy'+tagname+'.pdf')
		pu.Send2Dropbox('img/vtxStatus-logy'+tagname+'.pdf')

	################## plot & output ##################
	os.makedirs('out/', exist_ok=True)
	os.makedirs('img/', exist_ok=True)

	plot(	Ntuple1evt, Ntuple2evt, 
		Ntuple1vtx, Ntuple2vtx, 
		Ntuple1trk, Ntuple2trk, '' )


	# plot(	Ntuple1evt[ Ntuple1evt.eval('nTrk > 10650') ], Ntuple2evt[ Ntuple2evt.eval('nTrk > 10650') ], 
	# 	Ntuple1vtx[ Ntuple1vtx.eval('nTrk > 10650') ], Ntuple2vtx[ Ntuple2vtx.eval('nTrk > 10650') ], 
	# 	Ntuple1trk[ Ntuple1trk.eval('nTrk > 10650') ], Ntuple2trk[ Ntuple2trk.eval('nTrk > 10650') ], '-nTrk_gt_10650' )


	# plot(	Ntuple1evt[ Ntuple1evt.eval('nVtx > 6') ], Ntuple2evt[ Ntuple2evt.eval('nVtx > 6') ], 
	# 	Ntuple1vtx[ Ntuple1vtx.eval('nVtx > 6') ], Ntuple2vtx[ Ntuple2vtx.eval('nVtx > 6') ], 
	# 	Ntuple1trk[ Ntuple1trk.eval('nVtx > 6') ], Ntuple2trk[ Ntuple2trk.eval('nVtx > 6') ], '-nVtk_gt_6' )


	###### scan the set difference
	### set difference on nEv: RAW - RAW'
	d_R_RP_evt = pd.concat([Ntuple1evt, Ntuple2evt, Ntuple2evt]).drop_duplicates(subset=['nEv'],keep=False)
	print(Ntuple1evt)
	print(Ntuple2evt)
	print(d_R_RP_evt.to_string())
	with open('out/d_R_RP_evt.txt', 'w') as f:
		f.write(d_R_RP_evt.to_string())

	d_R_RP_vtx = Ntuple1vtx[ Ntuple1vtx.apply(lambda x: x.nEv in d_R_RP_evt.nEv.values, axis=1) ]
	### slicing the vtx set of RAW selecting the nEv in the difference set (d_R_RP_evt)
	print(Ntuple1vtx)
	print(Ntuple2vtx)
	print(d_R_RP_vtx.to_string())
	with open('out/d_R_RP_vtx.txt', 'w') as f:
		f.write(d_R_RP_vtx.to_string())

	d_R_RP_trk = Ntuple1trk[ Ntuple1trk.apply(lambda x: x.nEv in d_R_RP_evt.nEv.values, axis=1) ]
	### slicing the trk set of RAW selecting the nEv in the difference set (d_R_RP_evt)
	print(Ntuple1trk)
	print(Ntuple2trk)
	print(d_R_RP_trk.to_string())
	with open('out/d_R_RP_trk.txt', 'w') as f:
		f.write(d_R_RP_trk.to_string())


	### set difference on nEv: RAW' - RAW
	d_RP_R_evt = pd.concat([Ntuple2evt, Ntuple1evt, Ntuple1evt]).drop_duplicates(subset=['nEv'],keep=False)
	print(Ntuple1evt)
	print(Ntuple2evt)
	print(d_RP_R_evt.to_string())
	with open('out/d_RP_R_evt.txt', 'w') as f:
		f.write(d_RP_R_evt.to_string())

	d_RP_R_vtx = Ntuple2vtx[ Ntuple2vtx.apply(lambda x: x.nEv in d_RP_R_evt.nEv.values, axis=1) ]
	### slicing the vtx set of RAW' selecting the nEv in the difference set (d_RP_R_evt)
	print(Ntuple1vtx)
	print(Ntuple2vtx)
	print(d_RP_R_vtx.to_string())
	with open('out/d_RP_R_vtx.txt', 'w') as f:
		f.write(d_RP_R_vtx.to_string())

	d_RP_R_trk = Ntuple2trk[ Ntuple2trk.apply(lambda x: x.nEv in d_RP_R_evt.nEv.values, axis=1) ]
	### slicing the trk set of RAW' selecting the nEv in the difference set (d_RP_R_evt)
	print(Ntuple1trk)
	print(Ntuple2trk)
	print(d_RP_R_trk.to_string())
	with open('out/d_RP_R_trk.txt', 'w') as f:
		f.write(d_RP_R_trk.to_string())

if __name__ == '__main__':
	main()


