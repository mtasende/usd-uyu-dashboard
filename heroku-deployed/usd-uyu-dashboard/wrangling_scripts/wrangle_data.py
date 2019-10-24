import plotly.graph_objs as go
import datetime as dt
import data.world_bank as wb
import data.preprocessing as pp
import plotly.figure_factory as ff
import os
from pathlib import Path
import pandas as pd

START_DATE = 1960

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = str(Path(MODULE_DIR).parent)
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DATA_RAW = os.path.join(DATA_DIR, 'raw')
DATA_INTERIM = os.path.join(DATA_DIR, 'interim')
DATA_EXTERNAL = os.path.join(DATA_DIR, 'external')
DATA_PROCESSED = os.path.join(DATA_DIR, 'processed')

PLOT_DATA = os.path.join(DATA_PROCESSED, 'plot_data.pkl')


def get_the_data(end_date, save=False):
    cpi = wb.download_cpis(['uy', 'us'], end_date=end_date)
    rate = wb.download_exchange_rate('uy', end_date=end_date)
    data = pp.causal_estimation(cpi, rate)

    if save:
        data.to_pickle(PLOT_DATA)

    return data


def return_figures():
    """Creates four plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """

    end_date = dt.datetime.now().year

    if os.path.exists(PLOT_DATA):
        print('Found the saved data.')
        data = pd.read_pickle(PLOT_DATA)
        if data.index[-1] < end_date - 1:
            print('The data is outdated. Downloading...')
            data = get_the_data(end_date, save=True)
    else:
        print('Data not found. Downloading...')
        data = get_the_data(end_date, save=True)

    # First chart plots USD/UYU and Causal Estimations
    graph_one = list()
    graph_one.append(
        go.Scatter(
            x=data.index.values.tolist(),
            y=data.causal_estimation.values.tolist(),
            mode='lines',
            name='PPP Estimation'
        )
    )
    graph_one.append(
        go.Scatter(
            x=data.index.values.tolist(),
            y=data.usd_uyu.values.tolist(),
            mode='lines',
            name='USD/UYU Exchange Rate'
        )
    )
    graph_one.append(
        go.Scatter(
            x=data.index.values.tolist(),
            y=data.causal_est_low.values.tolist(),
            mode='lines',
            name='Low Estimation'
        )
    )
    graph_one.append(
        go.Scatter(
            x=data.index.values.tolist(),
            y=data.causal_est_high.values.tolist(),
            mode='lines',
            name='High Estimation'
        )
    )

    layout_one = dict(title='USD/UYU Exchange and PPP Estimation',
                      xaxis=dict(title='Year'),
                      yaxis=dict(title='USD Value in UYU'),
                      legend=dict(x=0,
                                  font=dict(size=12)
                                  ),
                      )

    # Second chart plots USD/UYU and Causal Estimations in log scale.
    graph_two = graph_one

    layout_two = dict(title='USD/UYU Exchange and PPP Estimation ' +
                            '(log scale)',
                      xaxis=dict(title='Year', ),
                      yaxis=dict(title='USD Value in UYU', type='log'),
                      legend=dict(x=0,
                                  y=1,
                                  font=dict(size=12)
                                  ),
                      #showlegend=False,
                      )

    # Third chart plots the relative error trace
    graph_three = list()
    graph_three.append(
        go.Scatter(
            x=data.index.values.tolist(),
            y=data.relative_error.values.tolist(),
            mode='lines',
            name='Error'
        )
    )
    graph_three.append(
        go.Scatter(
            x=data.index.values.tolist(),
            y=data.relative_error_mean.values.tolist(),
            mode='lines',
            name='Mean'
        )
    )
    graph_three.append(
        go.Scatter(
            x=data.index.values.tolist(),
            y=data.relative_error_low.values.tolist(),
            mode='lines',
            name='Mean - 2 * Std'
        )
    )
    graph_three.append(
        go.Scatter(
            x=data.index.values.tolist(),
            y=data.relative_error_high.values.tolist(),
            mode='lines',
            name='Mean + 2 * Std'
        )
    )

    layout_three = dict(title='Relative Error Trace',
                        xaxis=dict(title='Year'),
                        yaxis=dict(title='Relative Error'),
                        legend=dict(x=0,
                                    y=1.2,
                                    font=dict(size=10)
                                    ),
                        )

    # Fourth chart shows the relative error histogram and pdf.
    group_labels = ['Relative Error']

    fig = ff.create_distplot([data.relative_error.values.tolist()],
                             group_labels,
                             bin_size=.05,
                             histnorm='probability')

    layout_four = dict(title='Relative Error Normalized Histogram',
                       xaxis=dict(title='Relative Error',
                                  range=[-0.6, 0.6]),
                       shapes=[
                           {
                               'type': 'line',
                               'x0': data.relative_error.iloc[-1],
                               'y0': 0,
                               'x1': data.relative_error.iloc[-1],
                               'y1': 0.18,
                               'line': {
                                   'color': 'rgb(0, 0, 0)',
                                   'width': 1,
                               },
                           }],
                       annotations=[
                           dict(
                               x=data.relative_error.iloc[-1],
                               y=0.18,
                               xref='x',
                               yref='y',
                               text='Current Value',
                               showarrow=True,
                               arrowhead=7,
                               ax=0,
                               ay=-40
                           )
                       ]
                       )
    fig.layout.update(layout_four)

    # append all charts to the figures list
    figures = list()
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(fig)
    #figures.append(dict(data=graph_four, layout=layout_four))

    return figures
