import numpy as np

from javelin.lcmodel import Cont_Model, Pmap_Model, Rmap_Model
from javelin.zylc import get_data

import pypetal_jav.defaults as dft
from pypetal_jav.petalio import write_data




def fix_jav_params_after_ufj(javelin_params, drw_rej_res):

    nlc = len(drw_rej_res['reject_data'])
    javelin_params = dft.set_javelin(javelin_params, nlc, ret_dict=True)
    new_params = javelin_params.copy()

    drw_sigma = np.median(drw_rej_res['sigmas'][0])
    drw_tau = np.median(drw_rej_res['taus'][0])

    if javelin_params['rm_type'] == 'spec':
        ntophat = 3
    elif javelin_params['rm_type'] == 'phot':
        ntophat = 4


    if javelin_params['together']:

        if javelin_params['fixed'] is None:
            fixed_tot = np.ones(2 + (nlc-1)*ntophat, dtype=int)
            p_fix_tot = np.ones(2 + (nlc-1)*ntophat )
        else:
            fixed_tot = javelin_params['fixed']
            p_fix_tot = javelin_params['p_fix']


        fixed_tot[0] = 0
        p_fix_tot[0] = np.log(drw_sigma)

        fixed_tot[1] = 0
        p_fix_tot[1] = np.log(drw_tau)


    else:        
        fixed_tot = np.ones( ( nlc-1, 2 + ntophat ), dtype=int )
        p_fix_tot = np.ones( ( nlc-1, 2 + ntophat ) )

        if javelin_params['fixed'] is not None:
            for i in range(nlc-1):
                if javelin_params['fixed'][i] is None:
                    continue
                else:
                    fixed_tot[i,:] = javelin_params['fixed'][i]
                    p_fix_tot[i,:] = javelin_params['p_fix'][i]


        for i in range(nlc-1):
            fixed_tot[i,0] = 0
            p_fix_tot[i,0] = np.log(drw_sigma)

            fixed_tot[i,1] = 0
            p_fix_tot[i,1] = np.log(drw_tau)


    new_params['fixed'] = fixed_tot
    new_params['p_fix'] = p_fix_tot

    return new_params



def get_javelin_filenames(output_chain, output_burn, output_logp, prefix, output_dir=None):
    tot_fnames = np.full(3, None)

    if output_chain:
        tot_fnames[0] = 'chain_' + prefix + '.txt'

    if output_burn:
        tot_fnames[1] = 'burn_' + prefix + '.txt'

    if output_logp:
        tot_fnames[2] = 'logp_' + prefix + '.txt'

    if output_dir is not None:
        if output_dir[-1] != r'/':
            output_dir += r'/'

        for i in range(len(tot_fnames)):

            if tot_fnames[i] is not None:
                tot_fnames[i] = output_dir + tot_fnames[i]

    return tot_fnames



def run_javelin(cont_fname, line_fnames, line_names,
                rm_type='spec',
                lagtobaseline=0.3, laglimit='baseline',
                fixed=None, p_fix=None, subtract_mean=True,
                nwalkers=100, nburn=100, nchain=100, threads=1, output_chains=False,
                output_burn=False, output_logp=False, output_dir=None,
                nbin=50, verbose=False, plot=False):

    """Run JAVELIN on a set of light curves.

    Parameters
    ----------
    cont_fname : str
        The filename of the continuum light curve.
    line_fnames: str, list of str
        The filename(s) of the line light curve(s).
    rm_type : str, optional
        The type of analysis (and JAVELIN model) to use. May either be "spec" for
        spectroscopic RM or "phot" for photometric RM. Default is "spec".
    lagtobaseline : float, optional
        JAVELIN will use a log prior on the lag and penalize lags larger x*baseline,
        where x is the input value and baseline is the baseline of the light curves.
        Default is 0.3.
    laglimit : (2,) list of floats, str, optional
         The range of lags to search for the lag between light curves in the following form:
         [lower, upper]. If set to "baseline", the range will be set to [-baseline, baseline].
         Default is 'baseline'.
    fixed : None or list of floats, optional
        An array defining which parameters are fixed and which are allowed to vary. The length of
        the array must match the number of parameters ( 2 + 3*len(line_fnames) ). In the array,
        1 corresponds to a variable parameter and 0 corresponds to a fixed parameter. If set to ``None``,
        all parameters will be allowed to vary. Default is ``None``.
    p_fix : None or list of floats, optional
        An array defining the values of the fixed parameters. The length of the array must match the
        number of parameters and of the ``fixed" array. If set to ``None``, all parameters will be allowed
        to vary. Must be defined if ``fixed`` is. Default is ``None``.
    subtract_mean : bool, optional
        If True, will subtract the mean of the light curves before analysis. Default is ``True``.
    nwalkers : int, optional
        The number of walkers to use in the MCMC. Default is 100.
    nburn : int, optional
        The number of burn-in steps to use in the MCMC. Default is 100.
    nchain : int, optional
        The number of steps to use in the MCMC. Default is 100.
    threads : int, optional
        The number of parallel threads to use in the MCMC. Default is 1.
    output_chains : bool, optional
        If ``True``, will output the MCMC chains to a file. Default is ``False``.
    output_burn : bool, optional
        If ``True``, will output the MCMC burn-in chains to a file. Default is ``False``.
    output_logp : bool, optional
        If ``True``, will output the MCMC log-probability values to a file. Default is ``False``.

    Returns
    -------
    res : dict
        A dictionary containing the results of the JAVELIN analysis. Has the following keys:
        * cont_hpd : list of float
            The highest posterior density (HPD) interval for the continuum light curve DRW fits.
        * tau : list of float
            The MC chain for the DRW tau parameter.
        * sigma : list of float
            The MC chain for the DRW sigma parameter.
        * tophat_params : list of float
            The MC chains for the tophat parameters (lag, width, scale), 3 for each light curve.
        * hpd : list of float
            The HPD intervals for the DRW and tophat parameters for each light curve.
        * cont_model : javelin.lcmodel.Cont_Model
            The continuum model object.
        * rmap_model : javelin.lcmodel.Rmap_Model, javelin.lcmodel.Pmap_Model
            The RM model object.
        * cont_dat : javelin.zylc.LightCurve
            The continuum light curve object.
        * tot_dat : javelin.zylc.LightCurve
            The object containing all light curves (continuum + lines).
    """


    total_fnames = np.hstack( [cont_fname, line_fnames] )
    total_names = line_names

    #Deal with csv files
    xi, yi, erri = np.loadtxt(cont_fname, delimiter=',', unpack=True, usecols=[0,1,2])
    write_data( [xi, yi, erri] , output_dir + 'cont_lcfile.dat', delimiter='\t' )

    for i in range(len(total_fnames[1:])):
        xi, yi, erri = np.loadtxt(total_fnames[i+1], delimiter=',', unpack=True, usecols=[0,1,2])
        write_data( [xi, yi, erri], output_dir + line_names[i+1] + '_lcfile.dat', delimiter='\t' )

    cont_fname = output_dir + 'cont_lcfile.dat'
    total_fnames = np.concatenate( [ [cont_fname], [output_dir + x + '_lcfile.dat' for x in line_names[1:] ]])

    con_dat = get_data(cont_fname, names=[total_names[0]], set_subtractmean=subtract_mean)
    tot_dat = get_data(total_fnames, names=total_names, set_subtractmean=subtract_mean)

    if fixed is not None:
        if (fixed[0] == 0) & (fixed[1] == 0):
            skip_init = True
        else:
            skip_init = False
    else:
        skip_init = False


    if not skip_init:

        #Run continuum fit to get priors on DRW values
        fnames = get_javelin_filenames(output_chains, output_burn, output_logp, 'cont', output_dir)

        if fixed is not None:
            fixed_cont = fixed[:2]
            p_fix_cont = p_fix[:2]
        else:
            fixed_cont = None
            p_fix_cont = None

        cmod = Cont_Model(con_dat)
        cmod.do_mcmc(fixed=fixed_cont, p_fix=p_fix_cont,
                    nwalkers=nwalkers, nburn=nburn, nchain=nchain, threads=1,
                    fchain=fnames[0], fburn=fnames[1], flogp=fnames[2],
                    set_verbose=verbose)

        #Get HPD from continuum fit
        cmod.get_hpd(set_verbose=False)
        conthpd = cmod.hpd

        if fixed is not None:
            if fixed[0] == 0:
                conthpd[0,0] = conthpd[1,0] - 1e-10
                conthpd[2,0] = conthpd[1,0] + 1e-10

            if fixed[1] == 0:
                conthpd[0,1] = conthpd[1,1] - 1e-10
                conthpd[2,1] = conthpd[1,1] + 1e-10

        #Get histogram figure from continuum fit
        if plot:
            cmod.show_hist(bins=nbin)
    else:
        conthpd = None
        cmod = None






    #Run fit on continuum + line(s)
    fnames = get_javelin_filenames(output_chains, output_burn, output_logp, 'rmap', output_dir)

    if rm_type == 'spec':
        rmod = Rmap_Model(tot_dat)
    elif rm_type == 'phot':
        rmod = Pmap_Model(tot_dat)

    if (len(total_fnames) == 2) & (len(laglimit) == 2):
        laglimit = [laglimit]

    rmod.do_mcmc(conthpd=conthpd, fixed=fixed, p_fix=p_fix, lagtobaseline=lagtobaseline, laglimit=laglimit,
                 nwalkers=nwalkers, nburn=nburn, nchain=nchain,
                 threads=threads, fchain=fnames[0], fburn=fnames[1], flogp=fnames[2],
                 set_verbose=verbose)

    #Get HPD from continuum + line(s) fit
    rmod.get_hpd(set_verbose=False)
    rmap_hpd = rmod.hpd

    tau = np.exp( rmod.flatchain[:,1] )
    sigma = np.exp( rmod.flatchain[:,0] )
    tophat_params = rmod.flatchain[:, 2:].T


    return {
        'cont_hpd': conthpd,
        'tau': tau,
        'sigma': sigma,
        'tophat_params': tophat_params,
        'hpd': rmap_hpd,
        'cont_model': cmod,
        'rmap_model': rmod,
        'cont_dat': con_dat,
        'tot_dat': tot_dat
    }



def javelin_pred_lc(rmod, t_cont, t_lines, nbin=None, metric='med'):

    """Predict light curve(s) from a JAVELIN RM fit object.
    Parameters
    ----------
    rmod : javelin.lcmodel.Rmap_Model or javelin.lcmodel.Pmap_Model
        The output RM model from ``run_javelin``, after fitting the data.
    t_cont : array_like
        The time array for the continuum light curve.
    t_lines : array_like
        The time array for the line light curve(s).
    metric : str, optional
        The metric to use to get the bestfit parameter from the parameter distributions.
        Can be either "mean" or "med". Default is "med".
    Returns
    -------
    rmap_bestfit : javelin.lcmodel.Rmap_Model, javelin.lcmodel.Pmap_Model
        The RM model using the best fit parameters to predict the light curve(s).
    """

    if type(rmod) == Rmap_Model:
        rm_type = 'spec'
    elif type(rmod) == Pmap_Model:
        rm_type = 'phot'

    tau = rmod.flatchain[:,1]
    sigma = rmod.flatchain[:,0]
    tophat_params = rmod.flatchain[:, 2:].T

    if rm_type == 'spec':
        Nlc = len(tophat_params)//3
        ntophat = 3
    elif rm_type == 'phot':
        Nlc = len(tophat_params)//4
        ntophat = 4

    if metric == 'med':
        func = np.median
    if metric == 'mean':
        func = np.mean



    tau_best = func(tau)
    sigma_best = func(sigma)
    tophat_best = np.zeros( Nlc*ntophat )


    for i in range(Nlc):
        for j in range(3):


            if j == 0:
                mc_vals = tophat_params[ntophat*i + j, :]
                tophat_best[ ntophat*i + j ] = func(mc_vals)

            else:
                tophat_best[ ntophat*i + j ] = func(tophat_params[ ntophat*i + j, : ])


    bestfit_vals = np.concatenate([ [sigma_best], [tau_best], tophat_best ])
    rmap_bestfit = rmod.do_pred(bestfit_vals)

    return rmap_bestfit
