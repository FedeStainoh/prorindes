import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
from matplotlib.patches import ConnectionPatch
from matplotlib.patches import Rectangle
from matplotlib.patches import Patch

import seaborn as sns

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader

from adjustText import adjust_text


import string

letters = string.ascii_lowercase

def create_base_map(
    ax=None,
    figsize=(3.3,6.85),
    extent=(-71, -54, -41, -24),
    projection=ccrs.Miller(),
    left_labels=True,
    bottom_labels=True,
):
    """
    Draw a base map on a Cartopy axis.

    Parameters
    ----------
    ax : cartopy axis, optional
        Existing axis to draw on.
        If None, creates a new figure and axis.

    extent : tuple
        (lon_min, lon_max, lat_min, lat_max)

    projection : cartopy CRS
        Map projection.

    Returns
    -------
    fig, ax
    """

    # Create figure only if ax is not provided
    if ax is None:
        fig, ax = plt.subplots(
            figsize=(figsize),
            dpi=300,
            subplot_kw={'projection': projection}
        )
    else:
        fig = ax.figure

    # Set extent
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # Borders and coastlines
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.coastlines(resolution='10m', linewidth=0.5)

    # Argentina provinces
    shpfilename = shapereader.natural_earth(
        resolution='10m',
        category='cultural',
        name='admin_1_states_provinces'
    )

    reader = shapereader.Reader(shpfilename)

    for record in reader.records():
        if record.attributes['admin'] == 'Argentina':
            ax.add_geometries(
                [record.geometry],
                crs=ccrs.PlateCarree(),
                facecolor='none',
                edgecolor='black',
                linewidth=0.7
            )

    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=True,
        linewidth=0.1,
        ylocs=[-25,-30,-35,-40],
        xlocs=[-55,-60,-65,-70]
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.left_labels = left_labels
    gl.bottom_labels = bottom_labels

    
    return fig, ax


def facet_plot(
    data,
    plot_func,
    *,
    col="location",
    row = None,
    col_wrap =3,
    x=None,
    y=None,
    hue=None,
    palette=None,
    legend_title=None,
    legend=True,
    height = 4, 
    aspect =0.8,
    
    sharex = True,
    **plot_kwargs
):
    sns.set_theme(style="whitegrid")

    
    g = sns.FacetGrid(
        data,
        col=col,
        row = row,
        col_wrap=col_wrap,
        height=height,
        aspect=aspect,
        despine=False,
        sharex= sharex
    )
    
    g.map_dataframe(
        plot_func,
        x=x,
        y=y,
        hue=hue,
        palette=palette,
        **plot_kwargs
    )

    
    
    """settings = {}
    for key, value in {
        "xlabel": xlabel,
        "ylabel": ylabel,
        "xticks": xticks,
        "yticks": yticks,
        "xticklabels": xticklabels,
        "yticklabels": yticklabels,
        "xlim": xlim,
        "ylim": ylim,
    }.items():
        if value is not None:
            settings[key] = value
    if settings is not None:
        g.set(**settings)"""

    if legend == True and hue is not None:
        handles, labels = g.axes.flat[0].get_legend_handles_labels()

        if len(labels) > 0:
            g.figure.legend(
                handles,
                labels,
                title=legend_title or hue,
                loc="lower center",
                bbox_to_anchor=(0.5, -0.08),
                ncol=len(labels)
            )

        # Remove legends from individual axes
        for ax in g.axes.flat:
            if ax.legend_:
                ax.legend_.remove()

    g.set_titles("{col_name}")
    for i, ax in enumerate(g.axes.flat):
        title = ax.get_title()          # e.g. "location = Reconquista"
        #title = title.replace("location = ", "")  # optional
        ax.set_title(f"{letters[i]}) {title}")
    
    return g


def map_plot(
    longitude,
    latitude,
    colors,
    texts,
    titles,
    cmap,
    cbar_title,
    vmin,
    vmax,
    figsize = (174  /25.4, 234 /25. ),
    fontsize=10,
    extend="both",
    cbar_ticks=None,
    cbar_ticklabels=None,
):
    # number of maps
    n_maps = len(colors)
    fig, axes = plt.subplots(
        1,
        n_maps,
        figsize=figsize,
        dpi=300,
        constrained_layout=True,
        subplot_kw={"projection": ccrs.Miller()},
    )
    
    # Make axes iterable
    if n_maps == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        create_base_map(
            ax=ax,
            left_labels=(i == 0) # Remove ytick labels if the ax is not the first one
        )

    # repeat scatter  ploting for each axes
    for ax, values in zip(axes, colors):
        sc = ax.scatter(
            longitude,
            latitude,
            c=values,
            s=400,
            alpha=0.5,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            transform=ccrs.PlateCarree(),
        )

    # Title for each map
    if titles !=None:
        for ax, title in zip(axes, titles):
            ax.set_title(title)
        
    # plot Text for each map (first for correpsond to the map)
    for ax, labels in zip(axes, texts):
        # loop to plot text
        for x, y, label in zip(longitude, latitude, labels):
    
            ax.text(
                x,
                y,
                label,
                ha="center",
                va="center",
                fontsize=fontsize,
                transform=ccrs.PlateCarree(),
            )

    cbar = fig.colorbar(
    sc,
    ax=axes,
    location="bottom",
    shrink=0.7,
    extend=extend,
    pad=0.03,
    )
    
    cbar.set_label(cbar_title)
    
    if cbar_ticks is not None:
        cbar.set_ticks(cbar_ticks)
    
    if cbar_ticklabels is not None:
        cbar.set_ticklabels(cbar_ticklabels)


    return fig, axes