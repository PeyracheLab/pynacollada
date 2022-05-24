# pynacollada 🍍 🥥 🍹
Collaborative platform for high-level analysis with pynapple. 


- [pynacollada](#pynacollada)
  * [Getting Started](#getting-started)
    + [Requirements](#requirements)
    + [Installation](#installation)
  * [Libraries](#libraries)
    + [Neural Ensembles](#neural-ensembles)
    + [Manifolds](#manifolds)
    + [EEG processing](#eeg-processing)
    + [PETH](#peth)
    + [Brain state scoring](#brain-state-scoring)
    + [Graphics](#graphics)
    + [Position tracking](#position-tracking)



## Getting Started


### Requirements

-   Python 3.6+
-   [pynapple](https://github.com/PeyracheLab/pynapple)
-   scikit-learn
-   seaborn

### Installation

<!-- pynacco can be installed with pip:

``` {.sourceCode .shell}
$ pip install pynapple==0.2.0a1
```
 -->
Directly from the source code:

``` {.sourceCode .shell}
$ # clone the repository
$ git clone https://github.com/PeyracheLab/pynacollada.git
$ cd pynacollada
$ # Install in editable mode with `-e` or, equivalently, `--editable`
$ pip install -e .
```

## Libraries
### Neural Ensembles

| Jupyter notebook / scripts | Description | Contributors
| :---                       |    :----:   |          :---
| [Neuralensemble_tutorial_replay1.ipynb](pynacollada/neural_ensemble/Neuralensemble_tutorial_replay1.ipynb)  <br/> [pynacollada_tutorial_replay_short.py](pynacollada/neural_ensemble/pynacollada_tutorial_replay_short.py) | This script shows how to use pynapple to compute sleep reactivation, step by step. | Adrien Peyrache

### Manifolds

| Jupyter notebook / scripts | Description | Contributors
| :---                       |    :----:   |          :---
| [Tutorial_manifold_ring.ipynb](pynacollada/neural_manifold/Tutorial_manifold_ring.ipynb) | This tutorial shows how to project a ring manifold with head-direction neurons. | Guillaume Viejo

### EEG processing

| Jupyter notebook / scripts | Description | Contributors
| :---                       |    :----:   |          :---
| [Tutorial_ripple_detection.ipynb](pynacollada/eeg_processing/Tutorial_ripple_detection.ipynb) <br/> [Tutorial_ripple_detection.py](pynacollada/eeg_processing/Tutorial_ripple_detection.ipynb) | This tutorial shows how to detect ripples in CA1 step by steps | Guillaume Viejo

### PETH

| Jupyter notebook / scripts | Description | Contributors
| :---                       |    :----:   |          :---
| [Tutorial_PETH_Ripples.ipynb](pynacollada/PETH/Tutorial_PETH_Ripples.ipynb) | This tutorial shows how to make a peri-event time histogramm and raster plots around ripples | Guillaume Viejo

### Position tracking

| Jupyter notebook / scripts | Description | Contributors
| :---                       |    :----:   |          :---
| [Tutorial_DeepLabCut_Path_Segmentation.ipynb](pynacollada/position_tracking/DLC_process_position.ipynb) | This tutorial shows how to segment the path of a mouse running in a radial-arm maze with position extracted with DeepLabCut. | Dhruv Mehrotra

### Brain state scoring

### Graphics



