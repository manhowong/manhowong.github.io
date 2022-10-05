---
layout: page
title: EPSC kinetics analysis
permalink: /projects/kinetics
invisible: true

---

[GitHub Repo](https://github.com/manhowong/ephys-analysis-doc)

The decay of miniature EPSC signals (mEPSCs) from single-neuron recordings contains useful information about the ion channel properties. This project consists of two parts: (1) decay time analysis; and (2) non-stationary fluctuation analysis (NSFA) of mEPSCs.

## 1. Decay time analysis

The decay time constant of each mEPSC event can be computed by fitting the decay phase to a first-order exponential decay model by non-linear least squares approach.

## 2. non-stationary fluctuation analysis (NSFA)

The fluctuation of current amplitudes at different time points during an mEPSC event is stochastic in nature and is determined by ion channel properties. Ion channel properties such as single-channel conductance and ion channel number, which are difficult to observe empirically, can be computed statistically by NSFA. Briefly, the variance-mean relationship of EPSC amplitude is fitted with a parabola function based on a binomial model for quantal neurotransmitter release.

The above analyses are very sensitive to noise because of the low signal-to-noise ratio of miniature signals. To cope with this, we developed a MATLAB tool to detect and remove noisy signals automatically. In addition, we also developed tools to perform the analyses efficiently on large datasets.