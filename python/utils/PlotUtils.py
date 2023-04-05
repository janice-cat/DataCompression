import os
import matplotlib.pyplot as plt

style_fontsize  = 20
style_x_offset  = 0.

### Python2
def RegisterPltStyle(style_fontsize=style_fontsize):
	plt.rcParams.update({'font.size': style_fontsize})

	plt.rcParams['figure.titlesize'] = style_fontsize
	plt.rcParams['axes.titlesize']   = style_fontsize
	# plt.rcParams['axes.labelsize']   = style_fontsize
	plt.rcParams['axes.labelpad']    = style_x_offset

	plt.rcParams['lines.linewidth'] = 2

# ### Python3
# def RegisterPltStyle3(style_fontsize=style_fontsize):
# 	plt.rcParams.update({'font.size': style_fontsize})

# 	plt.rcParams['figure.titlesize'] = style_fontsize
# 	plt.rcParams['axes.titlesize']   = style_fontsize
# 	# plt.rcParams['axes.labelsize']   = style_fontsize
# 	plt.rcParams['axes.labelpad']    = style_x_offset

# 	plt.rcParams['lines.linewidth'] = 2

def RegisterROCStyle():
	plt.rcParams["figure.subplot.left"]   	= 0.20 # python3; 0.17 (python2)
	plt.rcParams["figure.subplot.bottom"]  	= 0.13
	plt.rcParams["figure.subplot.top"]  	= 0.87

def PaperColorStyle(tagger): ### red, orange, cyan, violet, green
	color_wheel = ['#ea0000', '#ff9224', '#00a600', '#00caca', '#6f00d2']
	# color_wheel = ['#C05640', '#EDD170', '#1ECFD6', '#0878A4', '#003D73']
	# color_wheel = ['#A53A3B', '#D96B0C', '#EDD170', '#5398D9', '#14325C']
	# return( color_wheel[0] if tagger=="cut-based" else \
	# 	color_wheel[1] if tagger==r"single-$\kappa$ BDT" else \
	# 	color_wheel[2] if tagger==r"multi-$\kappa$ BDT" else \
	# 	color_wheel[3] if tagger=="CNN" else \
	# 	color_wheel[4] if tagger==r"CNN$ ^2$" else \
	# 	(0,0,0) )
	return( color_wheel[0] if "cut-based" in tagger else \
		color_wheel[1] if r"single-$\kappa$ BDT" in tagger else \
		color_wheel[2] if r"multi-$\kappa$ BDT" in tagger else \
		color_wheel[4] if r"CNN$ ^2$" in tagger else \
		color_wheel[3] if "CNN" in tagger else \
		(0,0,0) )

def BPhysicsStyle(tagger): ### red, purple, , dark blue
	# color_wheel = [(144,59,28), (105,100,23),(144,100,75),(33,30,85)]
	# color_wheel = [(144,59,28), (106,76,156),(144,100,75),(33,30,85)]
	# color_wheel = [(144,59,28), (106,76,156),(32,96,79),(33,30,85)]
	color_wheel = [(224,122,99), (115,66,157),(61,145,162),(41,25,91)]
	# color_wheel = [(224,122,99), (106,76,156),(13,102,81),(33,30,85)]
	return( RGBint2RGBfloat(color_wheel[0]) if "sig" in tagger else \
		RGBint2RGBfloat(color_wheel[1]) if "qq" in tagger else \
		RGBint2RGBfloat(color_wheel[2]) if "rare" in tagger else \
		RGBint2RGBfloat(color_wheel[3]) if "all" in tagger else \
		(0,0,0) )

def RGBint2RGBfloat(rgb):
	return( tuple([i/255. for i in rgb]) )
def Send2Dropbox(filename):
	os.system('dropbox_uploader.sh upload {} tmp/'.format(filename))

def formatLegend(leg, textsize=0.055):
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(textsize)
	leg.SetFillStyle(0)
	leg.SetFillColor(0)
	leg.SetLineColor(0)


import ROOT as r

def formatTPaveText(box, textsize=0.055):
	box.SetBorderSize(0)
	box.SetLineColor(0)
	# box.SetLineWidth(linewidth)
	box.SetTextFont(42)
	box.SetTextSize(textsize)
	box.SetTextColor(r.kBlack)
	box.SetFillStyle(0)
	box.SetFillColor(0)

def GlobalStyle(left=0.18, right=0.12, bottom=0.15, top=0.12,
		optStat=0, optTitle=0):
	r.gStyle.SetOptStat(optStat)
	r.gStyle.SetOptTitle(optTitle)

	# of title
	r.gStyle.SetTitleFontSize(0.08)

	# of axes
	r.gStyle.SetPadTickX(1)
	r.gStyle.SetPadTickY(1)

	# of line
	# r.gStyle.SetHistLineWidth(2)

	# of marker
	r.gStyle.SetMarkerStyle(20)
	r.gStyle.SetMarkerSize (0.9)

	# of error bars
	r.gStyle.SetEndErrorSize(0)
	r.gStyle.SetErrorX(0.001)
	r.gPad.SetMargin (left, right, bottom, top)


def PlotStyle(h1):
	x_title_size 	= 0.07
	y_title_size 	= 0.06

	x_title_offset 	= 0.95
	y_title_offset 	= 1.25

	label_size 	= 0.05
	label_offset 	= 0.013

	h1.GetYaxis().SetTitleOffset	(y_title_offset)
	h1.GetYaxis().SetTitleSize	(y_title_size)
	h1.GetYaxis().SetLabelOffset	(label_offset)
	h1.GetYaxis().SetLabelSize	(label_size)
	h1.GetYaxis().SetNdivisions(508)

	h1.GetXaxis().SetTitleOffset	(x_title_offset)
	h1.GetXaxis().CenterTitle()
	h1.GetXaxis().SetTitleSize	(x_title_size)
	h1.GetXaxis().SetLabelOffset	(label_offset)
	h1.GetXaxis().SetLabelSize	(label_size)
	h1.GetXaxis().SetNdivisions(508)

	h1.SetLineWidth(2)

# for FitPull pad and also ratios
def setFitPullPads(fatherpad, frame, frame_pull):
	GlobalStyle()

	fatherpad.Divide(1,2,0,0)
	sonpad1 = fatherpad.GetPad(1)
	sonpad2 = fatherpad.GetPad(2)

	sonpad1.SetPad( 0.0, 0.30, 1.0, 1.0 )
	sonpad2.SetPad( 0.0, 0.0, 1.0, 0.30 )

	sonpad1.SetMargin( 0.18, 0.12, 0.07, 0.12 )
	sonpad2.SetMargin( 0.18, 0.12, 0.40, 0.00 )

	sonpad2.SetGridy(1)

	sonpad1.Draw()
	sonpad2.Draw()

	PlotStyle(frame)
	PlotStyle(frame_pull)

	frame.GetXaxis().SetTitle("")

	frame_pull.SetTitle("")
	frame_pull.GetYaxis().SetTitle("pull")
	frame_pull.SetMaximum(5)
	frame_pull.SetMinimum(-5)
	frame_pull.GetXaxis().SetTitleSize(frame_pull.GetXaxis().GetTitleSize() / 0.4)
	frame_pull.GetXaxis().SetLabelSize(frame_pull.GetXaxis().GetLabelSize() / 0.4)
	frame_pull.GetYaxis().SetTitleSize(frame_pull.GetYaxis().GetTitleSize() / 0.4)
	frame_pull.GetYaxis().SetLabelSize(frame_pull.GetYaxis().GetLabelSize() / 0.4)
	frame_pull.GetXaxis().SetTitleOffset(frame_pull.GetXaxis().GetTitleOffset())
	frame_pull.GetYaxis().SetTitleOffset(frame_pull.GetYaxis().GetTitleOffset() * 0.42)
	frame_pull.GetYaxis().SetNdivisions(205)



