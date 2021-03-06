#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo for testing basic version of imitpp on synthetic dataset
"""

import sys
import arrow
import utils
import random
import numpy as np
import tensorflow as tf

from ppgrl import RL_Hawkes_Generator
from stppg import HawkesLam, GaussianMixtureDiffusionKernel, StdDiffusionKernel, SpatialTemporalPointProcess

# Avoid error msg [OMP: Error #15: Initializing libiomp5.dylib, but found libiomp5.dylib already initialized.]
# Reference: https://github.com/dmlc/xgboost/issues/1715
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

def exp_simulation():
	data   = np.load('../Spatio-Temporal-Point-Process-Simulator/results/spatial-variant-gaussian-b.npy')
	params = np.load('../Spatio-Temporal-Point-Process-Simulator/data/simulation-1-gcomp-b.npz')
	mu     = params['mu']
	beta   = params['beta']
	kernel = GaussianMixtureDiffusionKernel(
		n_comp=1, layers=[10], C=1., beta=beta, 
		SIGMA_SHIFT=.1, SIGMA_SCALE=.5, MU_SCALE=.01,
		Wss=params['Wss'], bss=params['bss'], Wphis=params['Wphis'])
	lam    = HawkesLam(mu, kernel, maximum=1e+3)
	print("mu", mu)
	print("beta", beta)
	# plot kernel parameters over the spatial region.
	utils.plot_spatial_kernel("results/learned-kernel-svgau-b.pdf", kernel.gdks[0], S=[[-1., 1.], [-1., 1.]], grid_size=50)

def exp_real_with_1_comp():
	# REAL
	data   = np.load('data/real/SCEDC-1999-2019-24hrs.npy')
	data   = data[:, 1:, :3]
	params = np.load('results/real-24hrs-1-gcomp.npz')
	da     = utils.DataAdapter(init_data=data)
	mu     = params['mu']
	beta   = params['beta']
	kernel = GaussianMixtureDiffusionKernel(
		n_comp=1, layers=[10], C=1., beta=beta, 
		SIGMA_SHIFT=.1, SIGMA_SCALE=.5, MU_SCALE=.01,
		Wss=params['Wss'], bss=params['bss'], Wphis=params['Wphis'])
	lam    = HawkesLam(mu, kernel, maximum=1e+3)
	print("mu", mu)
	print("beta", beta)
	utils.plot_spatial_kernel("results/learned-kernel-SCEDC-1999-2019-24hrs.pdf", kernel.gdks[0], S=[[-1., 1.], [-1., 1.]], grid_size=50)
	utils.spatial_intensity_on_map(
		"results/map-SCEDC-1999-2019-24hrs.html", da, lam, data, seq_ind=3000, t=8.0, 
		# xlim=[-23.226, -22.621],
		# ylim=[-43.868, -43.050],
		# ngrid=200)
		xlim=da.xlim, ylim=da.ylim, ngrid=200)

def exp_real_with_2_comp():
	# REAL
	data   = np.load('../Spatio-Temporal-Point-Process-Simulator/data/rescale.ambulance.perday.npy')
	data   = data[:, 1:, :3]
	params = np.load('../Spatio-Temporal-Point-Process-Simulator/data/rescale_ambulance_mle_gaussian_mixture_params.npz')
	da     = utils.DataAdapter(init_data=data)
	mu     = .1 # params['mu']
	beta   = params['beta']
	kernel = GaussianMixtureDiffusionKernel(
		n_comp=1, layers=[5], C=1., beta=beta, 
		SIGMA_SHIFT=.1, SIGMA_SCALE=.5, MU_SCALE=.01,
		Wss=params['Wss'], bss=params['bss'], Wphis=params['Wphis'])
	lam    = HawkesLam(mu, kernel, maximum=1e+3)
	print("mu", mu)
	print("beta", beta)
	print(params['Wphis'].shape)
	pp     = SpatialTemporalPointProcess(lam)
    # generate points
	points, sizes = pp.generate(
		T=[0., 10.], S=[[-1., 1.], [-1., 1.]], 
		batch_size=100, verbose=True)
	results = da.restore(points)
	print(results)
	print(sizes)
	np.save('results/ambulance-simulation.npy', results)


if __name__ == "__main__":

	exp_real_with_2_comp()

	# for t in np.arange(3.0, 4.0, .01):
	# 	# ngrid should be smaller than 100, due to the computational 
	# 	# time is too large when n > 100.
	# 	utils.spatial_intensity_on_map(
	# 		"results/intensity_map_at_%f.html" % t, da, lam, data, seq_ind=0, t=t, 
	# 		# crime range
	# 		# xlim=[33.70, 33.87],
	# 		# ylim=[-84.50, -84.30],
	# 		# # earthquake range
	# 		# xlim=[25.692, 49.687],
	# 		# ylim=[-129.851, -111.094],
	# 		# ambulance range
	# 		xlim=[-23.226, -22.621],
	# 		ylim=[-43.868, -43.050],
	# 		ngrid=200)
	# 		# xlim=da.xlim, ylim=da.ylim, ngrid=200)
