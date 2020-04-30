# third party modules
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
plt.ioff() #deactivate interactive mode for plotting
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import pandas as pd


# Function to make the figure for the stacked area plot of the evolution
# of COVID-19 in the differennt comunidades autonomas.
def make_CCAA_area_plot_figure():
    fig,ax = plt.subplots(constrained_layout=True)
    # Set grid for the plot
    # ax.grid(True)
    # axes labels
    return fig,ax


# Function to update the stacked area plot
def update_CCAA_area_plot_figure(CCAA_name,communities_data_frames_dict,ax=None):
    try:
        df = communities_data_frames_dict[CCAA_name]
    except:
        print('¡Introduzca una comunidad autónoma válida!')
        return None
    # Column names for the data
    df_columns = df.columns.to_list()
    ISO_code_column_name = df_columns[0]
    date_column_name = df_columns[1]
    cases_column_name = df_columns[2]
    PCR_column_name = df_columns[3]
    TestAC_column_name = df_columns[4]
    Hospitalized_column_name = df_columns[5]
    UCI_column_name = df_columns[6]
    deaths_column_name = df_columns[7]
    recovered_column_name = df_columns[8]
    activeCases_column_name = df_columns[9]


    # Create a figure if no axes are provided
    if not ax:
        fig, ax = plt.subplots(constrained_layout=True);
    ax.clear()
    # Make the plot
    df.plot.area(
        x = date_column_name,
        y = [
            activeCases_column_name
            ,deaths_column_name
            ,recovered_column_name
        ],
        color = [
            'blue',
            'red',
            'green'
        ],
        ax = ax
    )
    ax.lines.clear()
    ax.set_xlabel('')
    ax.set_ylabel('Casos')
    # ticks rotation
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    # set ticks every week
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter(''))
    # plot title
    ax.set_title(CCAA_name)
    #legend position
    ax.legend(loc='upper left')
    # display figure
    display(ax.figure)
    return None


# Function to make a map chart of the actual situation in Spain
def plotMap(column_name,merged_data,ax = None):

    # Values range for the color maps
    vmin = min(merged_data[column_name])
    vmax = max(merged_data[column_name])

    # Color map for the plots
    cmap = 'YlGn'

    # Create a figure if no axes are provided
    if not ax:
        fig, ax = plt.subplots(constrained_layout=True);

    # title for the plot
    ax.set_title(column_name)
    # face color of the plot
    ax.set_facecolor('#00FFFF');
    # deactivate grid
    ax.grid(False)
    # remove the ticks
    plt.xticks([],[])
    plt.yticks([],[])

    # Make the plot
    merged_data.plot(
        column=column_name,
        cmap=cmap,
        edgecolors='lightblue',
        vmin = vmin,
        vmax = vmax,
        ax=ax
    );
    # colorbar for the plot
    sm = plt.cm.ScalarMappable(cmap=cmap,norm=plt.Normalize(vmin=vmin,vmax=vmax))
    # place it inside of the plot
    bar_ax = inset_axes(ax,
                    width="2.5%",
                    height="50%",
                    loc='upper left')
    ax.figure.colorbar(sm,cax=bar_ax,orientation='vertical');

    display(ax.figure)
    plt.close(ax.figure.number)
