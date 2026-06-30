__author__ = 'ivand'

import matplotlib.lines as mlines
import matplotlib.pylab as plt
import numpy as np


wave = np.random.rand(802)*10.
thickness = np.random.rand(802)/100.
posx = np.random.rand(802)
posy = np.random.rand(802)


# paleta de cores 5-class Dark2, do ColorBrewer2: http://colorbrewer2.org/
colors = ['red',
          'green',
          'yellow',
          'blue']


def attri_color(wave,thickness):

    colors = {
        'Burn+Mechanical': 'red',
        'Dispersant': 'green',
        'Mechanical': 'yellow',
        'nada': 'blue',
    }
    if thickness >= 0.0068 and wave <= 3.0:
        return colors.get('Burn+Mechanical', 'black')
    elif thickness >= 0.0025 and wave <= 6.8:
        return colors.get('Mechanical', 'black')
    elif thickness >= 0.0025 and wave >= 6.8:
        return colors.get('Dispersant', 'black')
    elif thickness < 0.0025:
        return colors.get('nada', 'black')

# criando o vetor de cores.
colors_reg = list()

for w, t in zip(wave, thickness):
    colors_reg.append(attri_color(w, t))

plt.scatter(x=posx,
            y=posy,
            s=30,
            c=colors_reg,
            alpha=0.6)

coption = ['Burn+Mechanical',
           'Dispersant',
           'Mechanical',
           'Nothing']

# legend 1
legend1_line2d = list()
for passo in range(len(colors)):
    legend1_line2d.append(mlines.Line2D([0], [0],
                                        linestyle="none",
                                        marker="o",
                                        alpha=0.6,
                                        markersize=15,
                                        markerfacecolor=colors[passo]))

legend1 = plt.legend(legend1_line2d,
                     coption,
                     numpoints=1,
                     fontsize=16,
                     loc="best",
                     shadow=True)

plt.gca().add_artist(legend1)
plt.show()