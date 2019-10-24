""" Some preprocessing functions. """


def causal_estimation(cpi, rate):
    """
    Calculate all the data to make a causal estimation of the exchange rate,
    according to the PPP theory: ex_rate_USD_UYU ~= a * CPI_uy / CPI_us
    The constant "a" is calculated with the expanding mean of the previous
    values. The function makes no predictions into the future, only estimations
    of the theoretical value of the exchange rate in the present.

    Args:
        cpi(pd.DataFrame): The Consumer Price Index.
        rate(pd.DataFrame): The USD/UYU exchange rate.

    Returns:
        pd.DataFrame: All the needed data to plot the causal estimations.
    """
    data = cpi.join(rate.rename(columns={'Uruguay': 'usd_uyu'}))
    data = data.rename(
        columns={'Uruguay': 'cpi_uy', 'United States': 'cpi_usa'})

    # Causal estimation
    data['raw_q'] = data.cpi_uy / data.cpi_usa
    data['instant_mean_coef'] = data.usd_uyu / data.raw_q
    data['mean_coef'] = data.instant_mean_coef.expanding().mean()
    data['causal_estimation'] = data.raw_q * data.mean_coef

    # Error estimation
    data['relative_error'] = (
                                     data.usd_uyu - data.causal_estimation) / data.causal_estimation
    data['relative_error_std'] = data.relative_error.expanding().std()
    data['relative_error_mean'] = data.relative_error.expanding().mean()
    data[
        'relative_error_low'] = data.relative_error_mean - 2 * data.relative_error_std
    data[
        'relative_error_high'] = data.relative_error_mean + 2 * data.relative_error_std
    data['causal_est_low'] = data.causal_estimation * (
            1 + data.relative_error_low)
    data['causal_est_high'] = data.causal_estimation * (
            1 + data.relative_error_high)

    return data
