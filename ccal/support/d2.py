"""
Computational Cancer Analysis Library

Authors:
    Huwate (Kwat) Yeerna (Medetgul-Ernar)
        kwat.medetgul.ernar@gmail.com
        Computational Cancer Analysis Laboratory, UCSD Cancer Center

    Pablo Tamayo
        ptamayo@ucsd.edu
        Computational Cancer Analysis Laboratory, UCSD Cancer Center
"""

from numpy import ones, isnan
from numpy.random import seed, shuffle
from pandas import concat
from scipy.cluster.hierarchy import linkage, dendrogram

from .. import RANDOM_SEED
from ..support.log import print_log


def drop_nan_columns(arrays):
    """
    Keep only not-NaN column positions in all arrays.
    :param arrays: iterable of numpy arrays; must have the same length
    :return: list of numpy arrays; none of the arrays contains NaN
    """

    # Keep all column indices
    not_nan_filter = ones(len(arrays[0]), dtype=bool)

    # Keep column indices without missing value in all arrays
    for a in arrays:
        not_nan_filter &= ~isnan(a)

    return [a[not_nan_filter] for a in arrays]


def get_top_and_bottom_indices(df, column_name, threshold, max_n=None):
    """

    :param df: DataFrame;
    :param column_name: str;
    :param threshold: number; quantile if < 1; ranking number if >= 1
    :param max_n: int; maximum number of rows
    :return: list; list of indices
    """

    if threshold < 1:
        column = df.ix[:, column_name]

        is_top = column >= column.quantile(threshold)
        is_bottom = column <= column.quantile(1 - threshold)

        top_and_bottom = df.index[is_top | is_bottom].tolist()

        if max_n and max_n < len(top_and_bottom):
            threshold = max_n // 2

    if 1 <= threshold:
        if 2 * threshold <= df.shape[0]:
            top_and_bottom = df.index[:threshold].tolist() + df.index[-threshold:].tolist()
        else:
            top_and_bottom = df.index

    return top_and_bottom


def get_dendrogram_leaf_indices(matrix):
    """

    :param matrix:
    :return:
    """

    row_dendro_leaves = dendrogram(linkage(matrix), no_plot=True)['leaves']
    col_dendro_leaves = dendrogram(linkage(matrix.T), no_plot=True)['leaves']
    return row_dendro_leaves, col_dendro_leaves


def split_slices(df, index, splitter, ax=0):
    """

    :param df:
    :param index:
    :param splitter:
    :param ax:
    :return:
    """

    splits = []

    if ax == 0:  # Split columns
        df = df.T

    for s_i, s in df.iterrows():

        old = s.ix[index]

        for new in old.split(splitter):
            splits.append(s.replace(old, new))

    # Concatenate
    if ax == 0:
        return concat(splits, axis=1)
    elif ax == 1:
        return concat(splits, axis=1).T


def drop_uniform_slice_from_dataframe(df, value, axis=0):
    """

    :param df:
    :param value:
    :param axis:
    :return:
    """

    if axis == 0:
        dropped = (df == value).all(axis=0)
        if any(dropped):
            print_log('Removed {} column index(ices) whoes values are all {}.'.format(dropped.sum(), value))
        return df.ix[:, ~dropped]

    elif axis == 1:
        dropped = (df == value).all(axis=1)
        if any(dropped):
            print_log('Removed {} row index(ices) whoes values are all {}.'.format(dropped.sum(), value))
        return df.ix[~dropped, :]


def shuffle_dataframe(df, axis=0, random_seed=RANDOM_SEED):
    """

    :param df: DataFrame;
    :param axis: int; {0, 1}
    :param random_seed: int or array-like;
    :return: DataFrame;
    """

    df = df.copy()

    seed(random_seed)
    if axis == 0:
        for c_i, col in df.iteritems():
            # Shuffle in place
            shuffle(col)

    elif axis == 1:
        for r_i, row in df.iterrows():
            # Shuffle in place
            shuffle(row)

    else:
        ValueError('Unknown axis {}; choose from {0, 1}.')

    return df


def split_dataframe(df, n_split):
    """
    Split df into n_split blocks (by row).
    :param df: DataFrame;
    :param n_split: int; 0 < n_split <= n_rows
    :return: list; list of dataframes
    """

    if df.shape[0] < n_split:
        raise ValueError('n_split ({}) can\'t be greater than the number of rows ({}).'.format(n_split, df.shape[0]))
    elif n_split <= 0:
        raise ValueError('n_split ({}) can\'t be less than 0.'.format(n_split))

    n = df.shape[0] // n_split

    splits = []

    for i in range(n_split):
        start_i = i * n
        end_i = (i + 1) * n
        splits.append(df.iloc[start_i: end_i, :])

    i = n * n_split
    if i < df.shape[0]:
        splits.append(df.ix[i:])

    return splits