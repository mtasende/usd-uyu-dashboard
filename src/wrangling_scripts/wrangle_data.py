import plotly.graph_objs as go
import datetime as dt
import src.data.world_bank as wb
import src.data.preprocessing as pp
import plotly.figure_factory as ff
import numpy as np

START_DATE = 1960


def return_figures():
    """Creates four plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """

    end_date = dt.datetime.now().year

    cpi = wb.download_cpis(['uy', 'us'], end_date=end_date)
    rate = wb.download_exchange_rate('uy', end_date=end_date)
    data = pp.causal_estimation(cpi, rate)

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
                                  font=dict(size=10)
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
                                  font=dict(size=10)
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
    graph_four = list()

    '''graph_four.append(
        go.Histogram(
            x=data.relative_error.values.tolist(),
            histnorm='probability',
        )
    )'''
    x = np.random.randn(1000)
    hist_data = [x]
    group_labels = ['distplot']

    fig = ff.create_distplot(hist_data, group_labels)
    graph_four.append(fig.data)
    layout_four = fig.layout

    '''layout_four = dict(title='Relative Error Normalized Histogram',
                       xaxis=dict(title='Relative Error'),
                       )'''

    # append all charts to the figures list
    figures = list()
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    #figures.append(fig)
    figures.append(dict(data=graph_four, layout=layout_four))

    return figures
