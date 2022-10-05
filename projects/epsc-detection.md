---
layout: page
title: Open-source tool for EPSC signal detection
permalink: /projects/epsc-detection
invisible: true

---

This is a spin-off of the project "EPSC data management and analysis pipeline for large datasets". I plan to write an open-source program for EPSC signal detection as an alternative to commercial programs. The tool will include both manual and automatic detection of EPSC signals. This tool is also developed in MATLAB as its parent project.

For automatic detection, I am using a simple yet efficient approach to detect peaks: computing the first derivative of a signal and look for the transition of signs (i.e. signal direction). The detected peaks are then filtered by user-defined thresholds such as the peak amplitude or the magnitude of the rising slope. For the detection of miniature EPSC signals, automatic detection is a challenging task as the signal-to-noise ratio is low. Some studies have suggested employing machine learning (ML) in the detection, but such tools are not adopted in most research labs probably because of technical obstacles. Besides, using ML to identify miniature signals may not be necessary because the signal shape can be defined mathematically. Though ML can be a useful approach for noisy data, using mathematical approach to detect signals is likely more efficient in many scenarios. 

The core code for automatic detection has been written. I will add an user interface for manual detection and manual inspection of detected signals.