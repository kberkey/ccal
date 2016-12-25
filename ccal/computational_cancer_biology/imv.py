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

from os.path import join

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from numpy import asarray, linspace, histogram, empty, argmin, sign
from pandas import read_csv, DataFrame, Series, concat
from seaborn import set_style, despine, distplot, rugplot
from statsmodels.sandbox.distributions.extras import ACSkewT_gen

from ..mathematics.equation import define_x_coordinates_for_reflection, define_cumulative_area_ratio_function
from ..support.file import establish_filepath
from ..support.log import timestamp, print_log
from ..support.plot import FIGURE_SIZE, save_plot


def fit_essentiality(feature_x_sample, bar_df, features=None, n_xgrids=3000,
                     directory_path=None, plot=True, overwrite=False, show_plot=True):
    """

    :param feature_x_sample:
    :param bar_df:
    :param features:
    :param n_xgrids: int;
    :param directory_path:
    :param plot:
    :param overwrite:
    :param show_plot:
    :return: dataframe;
    """

    if isinstance(feature_x_sample, str):  # Read from a file
        feature_x_sample = read_csv(feature_x_sample, sep='\t', index_col=0)

    if features:  # Fit selected features

        if isinstance(features, str) or isinstance(features, int):  # Single feature
            features = [features]

        feature_x_sample = feature_x_sample.ix[features, :].dropna(how='all')
        if any(feature_x_sample.index):
            print_log('Fitting selected features: {} ...'.format(feature_x_sample.index))
        else:
            raise ValueError('All of the selected features are not in the feature_x_sample indices.')

    else:  # Fit all features
        print_log('Fitting all features ...')

    # Result data structure
    feature_x_fit = DataFrame(index=feature_x_sample.index, columns=['N', 'DF', 'Shape', 'Location', 'Scale'])

    for i, (f_i, f_v) in enumerate(feature_x_sample.iterrows()):
        print_log('Fitting {} (@{}) ...'.format(f_i, i))

        # Fit skew-t PDF on this gene
        f_v.dropna(inplace=True)
        skew_t = ACSkewT_gen()
        n = f_v.size
        df, shape, location, scale = skew_t.fit(f_v)
        feature_x_fit.ix[f_i, :] = n, df, shape, location, scale

        # Plot
        if plot:

            # Make an output filepath
            if directory_path:
                filepath = join(directory_path, 'essentiality_plots', '{}.pdf'.format(f_i))
            else:
                filepath = None

            _plot_essentiality(feature_x_sample.ix[f_i, :], get_amp_mut_del(bar_df, f_i),
                               n=n, df=df, shape=shape, location=location, scale=scale,
                               n_xgrids=n_xgrids,
                               filepath=filepath, overwrite=overwrite, show_plot=show_plot)

    # Sort by shape
    feature_x_fit.sort_values('Shape', inplace=True)

    if directory_path:  # Save
        filepath = join(directory_path, '{}_skew_t_fit.txt'.format(timestamp()))
        establish_filepath(filepath)
        feature_x_fit.to_csv(filepath, sep='\t')

    return feature_x_fit


def plot_essentiality(feature_x_sample, feature_x_fit, bar_df, features=None, n_xgrids=3000,
                      directory_path=None, overwrite=False, show_plot=True):
    """
    Make essentiality plot for each gene.
    :param feature_x_sample: DataFrame or str; (n_features, n_samples) or a filepath to a file
    :param feature_x_fit: DataFrame or str; (n_features, 5 (n, df, shape, location, scale)) or a filepath to a file
    :param bar_df: dataframe;
    :param features: iterable; (n_selected_features)
    :param n_xgrids: int;
    :param directory_path: str; directory_path/essentiality_plots/feature<id>.pdf will be saved
    :param overwrite: bool; overwrite the existing figure or not
    :param show_plot: bool; show plot or not
    :return: None
    """

    if isinstance(feature_x_sample, str):  # Read from a file
        feature_x_sample = read_csv(feature_x_sample, sep='\t', index_col=0)

    if isinstance(feature_x_fit, str):  # Read from a file
        feature_x_fit = read_csv(feature_x_fit, sep='\t', index_col=0)

    if features is None:  # Use all features
        features = feature_x_sample.index
    if isinstance(features, str) or isinstance(features, int):  # Single feature
        features = [features]

    # Plot each feature
    for i, (f_i, fit) in enumerate(feature_x_fit.ix[features, :].iterrows()):
        print_log('{}: Plotting {} (@{}) ...'.format(timestamp(time_only=True), f_i, i))

        # Make an output filepath
        if directory_path:
            filepath = join(directory_path, 'essentiality_plots', '{}.pdf'.format(f_i))
        else:
            filepath = None

        # Parse fitted parameters
        n, df, shape, location, scale = fit

        _plot_essentiality(feature_x_sample.ix[f_i, :], get_amp_mut_del(bar_df, f_i),
                           n=n, df=df, shape=shape, location=location, scale=scale,
                           n_xgrids=n_xgrids,
                           filepath=filepath, overwrite=overwrite, show_plot=show_plot)


def _plot_essentiality(vector, bars, n=None, df=None, shape=None, location=None, scale=None,
                       n_bins=50, n_xgrids=3000,
                       figure_size=FIGURE_SIZE, plot_vertical_extention_factor=1.26,
                       pdf_color='#20D9BA', pdf_reversed_color='#4E41D9', essentiality_index_color='#FC154F',
                       gene_fontsize=30, labels_fontsize=22,
                       bars_linewidth=2.4,
                       bar0_color='#9017E6', bar1_color='#6410A0', bar2_color='#470B72',
                       filepath=None, overwrite=True, show_plot=True):
    """

    :param vector:
    :param bars:
    :param n:
    :param df:
    :param shape:
    :param location:
    :param scale:
    :param n_bins:
    :param n_xgrids:
    :param figure_size:
    :param plot_vertical_extention_factor:
    :param pdf_color:
    :param pdf_reversed_color:
    :param essentiality_index_color:
    :param gene_fontsize:
    :param labels_fontsize:
    :param bars_linewidth:
    :param bar0_color:
    :param bar1_color:
    :param bar2_color:
    :param filepath:
    :param overwrite:
    :param show_plot:
    :return:
    """

    # ==================================================================================================================
    # Set up
    # ==================================================================================================================
    # Initialize a figure
    figure = plt.figure(figsize=figure_size)

    # Set figure styles
    set_style('ticks')
    despine(offset=9)

    # Set figure grids
    n_rows = 10
    n_rows_graph = 5
    gridspec = GridSpec(n_rows, 1)

    # Make graph ax
    ax_graph = plt.subplot(gridspec[:n_rows_graph, :])

    # Set bar axes
    ax_bar0 = plt.subplot(gridspec[n_rows_graph + 1:n_rows_graph + 2, :])
    ax_bar1 = plt.subplot(gridspec[n_rows_graph + 2:n_rows_graph + 3, :])
    ax_bar2 = plt.subplot(gridspec[n_rows_graph + 3:n_rows_graph + 4, :])
    for ax in [ax_bar1, ax_bar0, ax_bar2]:
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for t in ax.get_xticklines():
            t.set_visible(False)
        for t in ax.get_xticklabels():
            t.set_visible(False)
        for t in ax.get_yticklines():
            t.set_visible(False)
        for t in ax.get_yticklabels():
            t.set_visible(False)

    # ==================================================================================================================
    # Plot histogram
    # ==================================================================================================================
    distplot(vector, hist=True, bins=n_bins, kde=False, hist_kws={'linewidth': 0.92, 'alpha': 0.24, 'color': pdf_color},
             ax=ax_graph)

    # ==================================================================================================================
    # Plot skew-t fit PDF
    # ==================================================================================================================
    # Initialize a skew-t generator
    skew_t = ACSkewT_gen()

    # Set up x-grids
    x_grids = linspace(vector.min(), vector.max(), n_xgrids)

    # Generate skew-t PDF
    skew_t_pdf = skew_t.pdf(x_grids, df, shape, loc=location, scale=scale)

    # Scale skew-t PDF
    histogram_max = histogram(vector, bins=n_bins)[0].max()
    scale_factor = histogram_max / skew_t_pdf.max()
    skew_t_pdf *= scale_factor

    # Plot skew-t PDF
    line_kwargs = {'linestyle': '-', 'linewidth': 2.6}
    ax_graph.plot(x_grids, skew_t_pdf, color=pdf_color, **line_kwargs)

    # Extend plot vertically
    ax_graph.axis([vector.min(), vector.max(), 0, histogram_max * plot_vertical_extention_factor])

    # ==================================================================================================================
    # Plot reflected skew-t PDF
    # ==================================================================================================================
    # Get the x-grids to get the reflecting PDF
    x_grids_for_reflection = define_x_coordinates_for_reflection(skew_t_pdf, x_grids)

    # Generate skew-t PDF over reflected x-grids, and scale
    skew_t_pdf_reflected = skew_t.pdf(x_grids_for_reflection, df, shape, loc=location, scale=scale) * scale_factor

    # Plot over the original x-grids
    ax_graph.plot(x_grids, skew_t_pdf_reflected, color=pdf_reversed_color, **line_kwargs)

    # ==================================================================================================================
    # Plot essentiality indices
    # ==================================================================================================================
    essentiality_indices = define_cumulative_area_ratio_function(skew_t_pdf, skew_t_pdf_reflected, x_grids,
                                                                 direction=['+', '-'][shape > 0])
    ax_graph.plot(x_grids, essentiality_indices, color=essentiality_index_color, **line_kwargs)

    # ==================================================================================================================
    # Decorate
    # ==================================================================================================================
    # Set title
    figure.text(0.5, 0.96,
                vector.name,
                fontsize=gene_fontsize, weight='bold', horizontalalignment='center')
    figure.text(0.5, 0.92,
                'N={:.2f}    DF={:.2f}    Shape={:.2f}    Location={:.2f}    Scale={:.2f}'.format(n, df, shape,
                                                                                                  location, scale),
                fontsize=gene_fontsize * 0.6, weight='bold', horizontalalignment='center')

    # Set labels
    label_kwargs = {'weight': 'bold', 'fontsize': labels_fontsize}
    ax_graph.set_xlabel('RNAi Score', **label_kwargs)
    ax_graph.set_ylabel('Frequency', **label_kwargs)

    # Set ticks
    tick_kwargs = {'size': labels_fontsize * 0.81, 'weight': 'normal'}
    for t in ax_graph.get_xticklabels():
        t.set(**tick_kwargs)
    for t in ax_graph.get_yticklabels():
        t.set(**tick_kwargs)

    # ==================================================================================================================
    # Plot bars
    # ==================================================================================================================
    bar_kwargs = {'rotation': 90, 'weight': 'bold', 'fontsize': labels_fontsize * 0.81}
    bar_specifications = {0: {'vector': bars.iloc[0, :], 'ax': ax_bar0, 'color': bar0_color},
                          1: {'vector': bars.iloc[1, :], 'ax': ax_bar1, 'color': bar1_color},
                          2: {'vector': bars.iloc[2, :], 'ax': ax_bar2, 'color': bar2_color}}

    for i, spec in bar_specifications.items():
        v = spec['vector']
        ax = spec['ax']
        c = spec['color']
        rugplot(v * vector, height=1, color=c, ax=ax, linewidth=bars_linewidth)
        ax.set_ylabel(v.name[-3:], **bar_kwargs)

    # ==================================================================================================================
    # Save
    # ==================================================================================================================
    if filepath:
        save_plot(filepath, overwrite=overwrite)

    if show_plot:
        plt.show()

    # TODO: properly close
    plt.clf()
    plt.close()


def get_amp_mut_del(gene_x_samples, gene):
    """
    Get AMP, MUT, and DEL information for a gene in the CCLE mutation file.
    :param gene_x_samples: dataframe; (n_genes, n_samplesa)
    :param gene: str; gene index used in gene_x_sample
    :return: dataframe; (3 (AMP, MUT, DEL), n_samples)
    """

    null = Series(index=gene_x_samples.columns)

    # Amplification
    try:
        amplifications = gene_x_samples.ix['{}_AMP'.format(gene), :]
    except KeyError:
        print_log('No amplification data for {}.'.format(gene))
        amplifications = null
        amplifications.name = '{}_AMP'.format(gene)

    # Mutation
    try:
        mutations = gene_x_samples.ix['{}_MUT'.format(gene), :]
    except KeyError:
        print_log('No mutation data for {}.'.format(gene))
        mutations = null
        mutations.name = '{}_MUT'.format(gene)

    # Deletion
    try:
        deletions = gene_x_samples.ix['{}_DEL'.format(gene), :]
    except KeyError:
        print_log('No deletion data for {}.'.format(gene))
        deletions = null
        deletions.name = '{}_DEL'.format(gene)

    return concat([amplifications, mutations, deletions], axis=1).T


def make_essentiality_matrix(feature_x_sample, feature_x_fit, n_x_grids=3000, factor=1):
    """

    :param feature_x_sample:
    :param feature_x_fit:
    :param n_x_grids:
    :return:
    """

    common_indices = feature_x_sample.index & feature_x_fit.index
    if any(common_indices):
        print_log('Making essentiality matrix using {} common features (indices) ...'.format(common_indices.size))
    else:
        print_log('No common features (indices).')

    gene_x_sample = feature_x_sample.ix[common_indices, :]
    gene_x_fit = feature_x_fit.ix[common_indices, :]

    skew_t = ACSkewT_gen()
    essentiality_matrix = empty(gene_x_sample.shape)
    for i, (g, (n, df, shape, location, scale)) in enumerate(gene_x_fit.iterrows()):
        # Skew-t PDF
        vector = asarray(gene_x_sample.ix[g, :])
        x_grids = linspace(vector.min(), vector.max(), n_x_grids)
        skew_t_pdf = skew_t.pdf(x_grids, df, shape, loc=location, scale=scale)

        # Reflected Skew-t PDF
        x_grids_for_reflection = define_x_coordinates_for_reflection(skew_t_pdf, x_grids)
        skew_t_pdf_reflected = skew_t.pdf(x_grids_for_reflection, df, shape, loc=location, scale=scale)

        # Essentiality indices
        essentiality_indices = define_cumulative_area_ratio_function(skew_t_pdf, skew_t_pdf_reflected, x_grids,
                                                                     direction=['+', '-'][shape > 0])

        essentiality_matrix[i, :] = [factor * sign(shape) * essentiality_indices[argmin(abs(x_grids - v))] for v in
                                     vector]

    return DataFrame(essentiality_matrix, index=gene_x_sample.index, columns=gene_x_sample.columns)