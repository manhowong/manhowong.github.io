---
layout: page
title: EPSC data management and analysis pipeline for large datasets
permalink: /projects/epsc-pipeline
invisible: true

---

## Background

The analysis of EPSC signals from single-neuron recordings involves multiple processes, such as signal detection, signal characterization, model fitting and statistical analysis. Different tools are required for different processes and most tools available in the neuroscience community are not suited for the automated processing of large datasets.

## Current development

I created this project because of the lack of suitable tools to analyze my data, but I decided to expand the project and to create a streamlined data analysis pipeline for EPSC data. At the moment, the analysis pipeline includes automatic reading of EPSC signal data, sample grouping and filtering by custom variables, common statistical tests (e.g. ANOVA), bootstrapping, distribution fitting and processed data exporting for analysis with specialized tools. The pipeline also includes computation of electrical properties of neuronal membranes such as resistance and capacitance.

Most of the pipeline's functions are traditionally done manually in my field and this pipeline makes the analysis of large datasets possible (or at least much more efficient). To faccilitate data sharing within the community and thus making data mining from large amount of shared data possible, another goal of this project is to share my data with a standardized data format with the neuroscience community (this will be done after my work is published, probably in 2023). 

## Future plan

The pipeline is developed in MATLAB. Although it is the most established language in the neuroscience field, I plan to add a simple user interface to make the tool accessible to more people.

This work will hopefully be published soon in 2023. It will be an open source project. In the mean time, any suggestions are welcome and I am happy to share the demo code upon request. In the future, I may convert the code to Python if there is a demand, as it is probably more suitable for cloud computing when large amount of data is involved.