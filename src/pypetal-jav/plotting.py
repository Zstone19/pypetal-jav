import corner
import javelin.lcmodel
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import palettable
from matplotlib.colors import ListedColormap


mpl.rcParams['xtick.minor.visible'] = True
mpl.rcParams['xtick.top'] = True
mpl.rcParams['xtick.direction'] = 'in'

mpl.rcParams['ytick.minor.visible'] = True
mpl.rcParams['ytick.right'] = True
mpl.rcParams['ytick.direction'] = 'in'

mpl.rcParams["figure.autolayout"] = False

mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['savefig.format'] = 'pdf'


def plot_javelin_hist(res, fixed=None, nbin=50,
                      time_unit='d',
                      remove_fixed=True, fname=None):


    """Plot the histograms of the posteriors for the JAVELIN fit parameters.
    Parameters
    ----------
    res : dict
        The output of ``pypetal.modules.run_javelin``.
    fixed : dict, optional
        The ``fixed`` argument passed to JAVELIN. If ``None``, all parameters will be assumed to vary. Default is ``None``.
    nbin : int, optional
        The number of bins to use for the histograms. Default is 50.
    time_unit : str, optional
        The unit of time for the light curves. Default is 'd'.
    remove_fixed : bool, optional
        If ``True``, will remove the fixed parameters from the plot. Default is ``True``.
    fname : str, optional
        If not ``None``, will save the plot to the given filename. Default is ``None``.
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    ax : list of matplotlib.axes.Axes
        The axes for the plot.
    """


    if type(res['rmap_model']) == javelin.lcmodel.Rmap_Model:
        rm_type = 'spec'
        Ncol = 3
    elif type(res['rmap_model']) == javelin.lcmodel.Pmap_Model:
        rm_type = 'phot'
        Ncol = 4


    time_unit_txt = '[' + str(time_unit) + ']'

    Nrow = len(res['tophat_params'])//3 + 1

    names = res['tot_dat'].names[1:]
    x1 = res['tot_dat'].jlist[0]

    if fixed is not None:
        fixed_reshape = np.zeros( (Nrow, Ncol) )
        fixed_reshape[0,0] = fixed[0]
        fixed_reshape[0,1] = fixed[1]

        for i in range(Nrow-1):
            for j in range(Ncol):
                fixed_reshape[i+1,j] = fixed[2 + j + i*Ncol ]

    else:
        fixed_reshape = np.ones( (Nrow, Ncol) )
        fixed_reshape[0, 2] = 0


    fig, ax = plt.subplots(Nrow, Ncol, figsize=(5*Ncol, 5*Nrow))

    ax[0,0].hist( np.log10(res['sigma']), bins=nbin )
    ax[0,1].hist( np.log10(res['tau']), bins=nbin )


    #Plot tophat params
    for i in range(1, Nrow):
        for j in range(Ncol):
            vals = res['tophat_params'][ (i-1)*Ncol + j ]
            x2 = res['tot_dat'].jlist[i]

            ax[i,j].hist( vals, bins=nbin )


    ax[0,0].set_xlabel(r'$\log_{10}(\sigma_{\rm DRW})$', fontsize=19)
    ax[0,1].set_xlabel(r'$\log_{10}(\tau_{\rm DRW} \,\, ' + time_unit_txt + ')$', fontsize=19)

    for i in range(1, Nrow):
        for j in range(Ncol):

            if j == 0:
                ax[i,j].set_xlabel(r'$t_{' + names[i-1] + '}$ ' + time_unit_txt, fontsize=22)
            if j == 1:
                ax[i,j].set_xlabel(r'w$_{' + names[i-1] + '}$ ' + time_unit_txt, fontsize=22)
            if j == 2:
                ax[i,j].set_xlabel(r's$_{' + names[i-1] + '}$', fontsize=22)
            if j == 3:
                ax[i,j].set_xlabel(r'$\alpha_{' + names[i-1] + '}$', fontsize=22)

    for i in range(Nrow):
        ax[i, 0].set_ylabel('N', fontsize=19)

    for i in range(2, Ncol):
        ax[0, i].axis('off')


    for i in range(Nrow):
        for j in range(Ncol):
            ax[i,j].tick_params('both', labelsize=14)
            ax[i,j].tick_params('both', which='major', length=8)
            ax[i,j].tick_params('both', which='minor', length=4)

            if remove_fixed:
                if fixed_reshape[i,j] == 0:
                    ax[i,j].clear()
                    ax[i,j].axis('off')

    plt.subplots_adjust( wspace=.25, hspace=.25 )

    if fname is not None:
        plt.savefig( fname, dpi=200, bbox_inches='tight' )

    return fig, ax


def javelin_corner(res, nbin=20, fname=None):

    """Create a corner plot for the JAVELIN parameter results.
    Parameters
    ----------
    res : dict
        The output of ``pypetal.modules.run_javelin``.
    nbins : int, optional
        The number of bins to use for the histograms. Default is 20.
    fname : str, optional
        If not ``None``, will save the plot to the given filename. Default is ``None``.
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object for the plot.
    ax : list of matplotlib.axes.Axes
        The axes objects for the plot.
    """

    if type(res['rmap_model']) == javelin.lcmodel.Rmap_Model:
        rm_type = 'spec'
    elif type(res['rmap_model']) == javelin.lcmodel.Pmap_Model:
        rm_type = 'phot'


    labels = []
    labels.append( r'$\log_{10} (\sigma_{\rm DRW})$' )
    labels.append( r'$\log_{10} (\tau_{\rm DRW})$' )

    for i in range( res['tot_dat'].nlc - 1 ):
        labels.append( r'$t_{' + res['tot_dat'].names[i+1] + '}$' )
        labels.append( r'$w_{' + res['tot_dat'].names[i+1] + '}$' )
        labels.append( r'$s_{' + res['tot_dat'].names[i+1] + '}$' )

        if rm_type == 'phot':
            labels.append( r'$\alpha_{' + res['tot_dat'].names[i+1] + '}$' )


    #Plot original output with weighted output superposed on histograms
    corner_dat = np.vstack( [np.log10(res['sigma']), np.log10(res['tau']),  res['tophat_params']]).T

    fig = corner.corner( corner_dat,
                labels=labels, show_titles=False, bins=nbin,
                label_kwargs={'fontsize': 20} )

    ax = np.array(fig.axes).reshape( (2 + len(res['tophat_params']), 2 + len(res['tophat_params']) ) )

    if fname is not None:
        plt.savefig( fname, dpi=200, bbox_inches='tight' )

    return fig, ax



def plot_javelin_bestfit(res, bestfit_model, time_unit='d', lc_unit='mag', fname=None):


    """Plot the fit to the data using the best-fit JAVELIN parameters.
    Parameters
    ----------
    res : dict
        The output of ``pypetal.modules.run_javelin``.
    bestfit_model : dict
        The bestfit model after using ``pypetal.utils.javelin_pred_lc``.
    time_unit : str, optional
        The time unit for the light curves. Default is 'd'.
    lc_unit : str, optional
        The light curve unit. Default is 'mag'.
    fname : str, optional
        If not ``None``, will save the plot to the given filename. Default is ``None``.
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object for the plot.
    ax : list of matplotlib.axes.Axes
        The axes objects for the plot.
    """

    if isinstance(lc_unit, str):
        lc_unit = np.full( tot_dat.nlc, lc_unit )


    cmap = ListedColormap( palettable.cartocolors.qualitative.Vivid_10.mpl_colors )
    colors = cmap.colors

    tot_dat = res['tot_dat']

    xmin = np.min( [bestfit_model.jlist[i][0] for i in range( bestfit_model.nlc ) ] )
    xmax = np.min( [bestfit_model.jlist[i][-1] for i in range( bestfit_model.nlc ) ] )



    fig, ax = plt.subplots(tot_dat.nlc, 1, sharex=True, figsize=(13, 7))
    for i in range(len(ax)):
        ax[i].set_prop_cycle('color', palettable.cartocolors.qualitative.Bold_10.mpl_colors )


    for i in range(tot_dat.nlc):
        ax[i].errorbar( tot_dat.jlist[i], tot_dat.mlist[i] + tot_dat.blist[i],
                    yerr=tot_dat.elist[i], fmt='.', ms=10, mfc=colors[9], mec='k',
                    label='Data', zorder=0 )

        ax[i].plot( bestfit_model.jlist[i], bestfit_model.mlist[i]+bestfit_model.blist[i],
                    c=colors[i % 9], lw=2, label='Best fit', zorder=-1 )
        ax[i].fill_between( bestfit_model.jlist[i],
                        bestfit_model.mlist[i]+bestfit_model.blist[i]+bestfit_model.elist[i],
                        bestfit_model.mlist[i]+bestfit_model.blist[i]-bestfit_model.elist[i],
                        color=colors[i % 9], alpha=.3, zorder=-2)


        y1, y2 = ax[i].get_ylim()
        y2 = y1 + (y2 - y1)*1.25
        ax[i].set_ylim( y1, y2 )

        ax[i].set_xlim( xmin, xmax )
        ax[i].text( .02, .8, tot_dat.names[i], transform=ax[i].transAxes, fontsize=16 )

        ax[i].tick_params('both', labelsize=15)
        ax[i].tick_params('both', which='major', length=8)
        ax[i].tick_params('both', which='minor', length=5)

        ax[i].legend( bbox_to_anchor=(1.13, 1.03), fontsize=12 )



        if lc_unit[i] == 'mag':
            ytxt = 'Magnitude'
            ax[i].invert_yaxis()

        elif lc_unit[i] == 'Arbitrary Units':
            ytxt = 'Flux'
        else:
            ytxt = 'Flux [' + str(lc_unit[i]) + ']'

        ax[i].set_ylabel( ytxt, fontsize=22, va='center' )

    ax[-1].set_xlabel('Time [' + str(time_unit) + ']', fontsize=20)

    plt.subplots_adjust(hspace=0)

    if fname is not None:
        plt.savefig( fname, dpi=200, bbox_inches='tight' )

    return fig, ax
