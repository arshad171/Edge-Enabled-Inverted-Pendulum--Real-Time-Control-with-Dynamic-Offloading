import os
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import to_rgba
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import json
from matplotlib.patches import Patch
import altair as alt
from scipy.stats import gaussian_kde
import numpy as np
from typing import NamedTuple
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import ConnectionPatch
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FuncFormatter

CMAP_APPLICATIONS_E = cm.get_cmap("Set3")

FIGS_PATH = "/Users/arshadjaveed/My Data/Workspace/pa_res_alloc/results/figures_neuro"

plt.rcParams.update(
    {
        "legend.fontsize": 16,  # Legend font size
        "text.usetex": True,  # Use LaTeX to render text
        "font.family": "serif",  # Use a serif font family
        "font.serif": [
            "Computer Modern"
        ],  # Set the default LaTeX font to Computer Modern
        "axes.labelsize": "26",  # Font size for axis labels
        "axes.labelweight": "bold",
        "axes.labelweight": "bold",  # Make the label bold
        "axes.titleweight": "bold",  # Make the title bold
        "font.size": 12,  # General font size
        "legend.fontsize": 12,  # Font size for legends
        "xtick.labelsize": 22,  # Font size for x-tick labels
        "ytick.labelsize": 22,  # Font size for y-tick labels
        "lines.linewidth": 2,
        "lines.markersize": 8,
        "grid.linestyle": "--",
        "grid.color": "gray",
        "grid.alpha": 0.5,
    }
)


COLOR_PALETTE = {
    "cnn": "orange",
    "dnn": "red",
    "lstm": "purple",
    "rf": "green",
    ###
    "cnn-v1": "orange",
    "dnn-v1": "red",
    "lstm-v1": "purple",
    "rf-v1": "green",
    ###
    "cnn-v2": "orange",
    "dnn-v2": "red",
    "lstm-v2": "purple",
    "rf-v2": "green",
    ###
    "bert": "black",
    ###
    "scaloran": "skyblue",
    "scaloran-cons": "darkorange",
    "perx": "salmon",
    "perx++": "crimson",
    "perx++ (rel)": "black",
    "perx++ (rnd)": "crimson",
    "NeuRO (rel)": "black",
    "NeuRO (rnd)": "crimson",
    ###
    "neuro": "crimson",
    "NeuRO (rel) - m1": "black",
    "NeuRO (rnd) - m1": "crimson",
    "NeuRO (rel) - m2": "gray",
    "NeuRO (rnd) - m2": "teal",
    "neuro (l)": "gray",
    "neuro (h)": "black",
    ###
    "visual-servo": mcolors.to_hex(CMAP_APPLICATIONS_E(0)),
    "tclf-gcn": mcolors.to_hex(CMAP_APPLICATIONS_E(0)),
    "tclf-rf": mcolors.to_hex(CMAP_APPLICATIONS_E(1)),
    "tstr-lstm": mcolors.to_hex(CMAP_APPLICATIONS_E(2)),
    "kalman-gru": mcolors.to_hex(CMAP_APPLICATIONS_E(3)),
    "knet-gru": mcolors.to_hex(CMAP_APPLICATIONS_E(3)),
    "iclf-mnet": mcolors.to_hex(CMAP_APPLICATIONS_E(4)),
    "text-bert": mcolors.to_hex(CMAP_APPLICATIONS_E(5)),
    "iclf-efnet": mcolors.to_hex(CMAP_APPLICATIONS_E(6)),
    "text-tbert": mcolors.to_hex(CMAP_APPLICATIONS_E(7)),
    "iclf-mvit": mcolors.to_hex(CMAP_APPLICATIONS_E(8)),
}
