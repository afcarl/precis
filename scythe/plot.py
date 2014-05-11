import matplotlib.pyplot as plt
import math
import numpy as np


def make_figure(generator, panels, measure=None, rows=1, cols=None):
    ''' Plot a composite figure made up of a list of panels. '''

    if measure is None:
        measure = generator.best

    n_figs = len(panels)
    if cols is None:
        cols = math.ceil(float(n_figs)/rows)

    fig = plt.figure(1)

    for i, p in enumerate(panels):
        plt.subplot(rows, cols, i+1)

        if p.startswith('stat'):
            plot_generational_stats(generator)

        elif p.startswith('corr'):
            scale_intercorrelation_matrix(measure, corr_with=p.split('-')[-1])

    plt.show()


def scale_scatter_plot(measure, rows=1, cols=None, jitter=0.0, alpha=0.3, trend=False, text=True, totals=False):
    ''' Generate scatterplot of abbreviated vs. original scores for each scale.
    Args:
        measure: A Measure instance
        rows: Number of rows in scale grid
        cols: Number of columns in scale grid. If None, will set to n_scales/rows
        jitter: Amount to jitter x and y values by (uniform distribution in range 
            [-jitter, jitter]). This is useful when there are too many data points 
            to see clear trends.
        alpha: Alpha level (opacity) of data points.
        trend: Whether or not to plot the regression line.
        text: Whether or not to plot the r-squared text label.
        totals: If true, adds a subplot for the total score across all scales.
    '''

    if not hasattr(measure, 'predicted_y'):
        measure.compute_stats()

    if cols is None:
        cols = measure.n_y/rows

    # Variables we'll need
    abbreviated_y = measure.predicted_y
    original_y = measure.y
    names = list(measure.y_names)
    r_squared = list(measure.r_squared)

    # Add a column for total score, summing up all scales
    if totals:
        names.append('Total')
        abbreviated_y = np.hstack((abbreviated_y, np.atleast_2d(np.sum(abbreviated_y, 1)).T))
        original_y = np.hstack((original_y, np.atleast_2d(np.sum(original_y, 1)).T))
        r_squared.append(np.corrcoef(abbreviated_y[:,-1], original_y[:,-1])[0,1])

    n_points = len(abbreviated_y)
    for i in range(abbreviated_y.shape[1]):
        plt.subplot(rows, cols, i+1)
        ax = plt.gca()
        x = abbreviated_y[:,i] + np.random.uniform(-jitter, jitter, n_points)
        y = original_y[:,i] + np.random.uniform(-jitter, jitter, n_points)
        plt.scatter(x, y, s=12, color='black', alpha=alpha)

        # Add regression line
        if trend:
            fit = np.polyfit(x, y, 1)
            fit_fn = np.poly1d(fit)
            plt.plot(x, fit_fn(x), '--', color='gray', lw=2)

        # Add r-square text
        if text:
            r_sq = round(r_squared[i], 2)
            plt.text(0.88, 0.08, r'R$^2$ = %.2f' % r_sq, transform = ax.transAxes, horizontalalignment='right',
                 verticalalignment='bottom', size=16)

        plt.title(names[i], size=18)
        plt.xlabel('Abbreviated score', size=16)
        plt.ylabel('Full-scale score', size=16)
        plt.grid(True)
        plt.tick_params(axis='both', which='major', labelsize=12)

    plt.subplots_adjust(left=0.07, right=0.95, top=0.95, bottom=0.07, hspace=0.4, wspace=0.3)
    plt.show()


def scale_intercorrelation_plot(measure, corr_with='cross', text=True):
    ''' Plot the correlation matrix between scales. 
    Args:
        corr_with: Which sets of variables to correlate.
            'observed': Plots intercorrelations between observed (i.e., real) scores
            'predicted': Plots intercorrelations between predicted scores.
            'cross': Plots correlations between observed and predicted scores.
        text: Boolean indicating whether to display the actual correlation values
            on the matrix.
    '''

    if not hasattr(measure, 'predicted_y'):
        measure.compute_stats()

    # Get the appropriate data
    if corr_with == 'cross':
        data = np.corrcoef(measure.predicted_y.T, measure.dataset.y.T)[0:measure.n_y, measure.n_y::]
        xlab = 'Abbreviated scale'
        ylab = 'Original scale'
        title = 'Intercorrelations between original and abbreviated scales'
    elif corr_with == 'observed':
        data = np.corrcoef(measure.dataset.y.T)
        xlab = ylab = 'Original scale'
        title = 'Intercorrelations between original scales'
    else:
        data = np.corrcoef(measure.predicted_y.T)
        xlab = ylab = 'Abbreviated scale'
        title = 'Intercorrelations between abbreviated scales'

    # Make heatmap
    plt.pcolor(data, cmap='RdYlBu_r', vmin=-1, vmax=1, edgecolors='black')

    # Reposition ticks and set labels
    ax = plt.gca()
    ax.set_xticks(np.arange(data.shape[0])+0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1])+0.5, minor=False)

    # Add title and axis labels
    # plt.title(title)
    plt.xlabel(xlab, size=16)
    plt.ylabel(ylab, size=16)

    # Bump title slightly
    t = plt.title(title, size=20) 
    t.set_y(1.05)
    plt.subplots_adjust(left=0.08, right=0.92)

    # Refine positioning
    ax.invert_yaxis()
    plt.tick_params(which='major', labelsize=12)
    ax.xaxis.tick_top()
    ax.yaxis.tick_left()

    scale_names = list(measure.dataset.y_names)
    ax.set_xticklabels(scale_names, minor=False)
    ax.set_yticklabels(scale_names, minor=False)

    # Add text values to cells
    if text:
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                plt.text(x + 0.5, y + 0.5, '%.2f' % data[y, x],
                         horizontalalignment='center',
                         verticalalignment='center', size=16
                         )

    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=12)


def evolution_plot(generator):
    ''' Plot evolution of best measure across generations:
    total cost, r-squared, number of items.
    '''
    mean_rsq = [np.mean(m.r_squared) for m in generator.best_measures]
    n_items = [m.n_X for m in generator.best_measures]
    cost = generator.logbook.select('min')
    print mean_rsq
    print n_items
    print cost
    plt.subplot(131)
    plt.plot(mean_rsq)
    plt.ylabel('Mean R^2')
    plt.xlabel('Generation')
    plt.subplot(132)
    plt.plot(n_items)
    plt.ylabel('Number of items')
    plt.xlabel('Generation')
    plt.subplot(133)
    plt.plot(cost)
    plt.ylabel('Cost')
    plt.xlabel('Generation')      
    plt.show()
