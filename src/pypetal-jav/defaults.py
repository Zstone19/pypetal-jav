import numpy as np
from astropy.table import Table



def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z



def set_general(input_args, fnames):

    default_kwargs = {
        'verbose': False,
        'plot': False,
        'time_unit': 'd',
        'lc_unit': 'Arbitrary Units',
        'file_fmt': 'csv',
        'lag_bounds': 'baseline',
        'threads': 1
    }

    params = merge_dicts(default_kwargs, input_args)

    verbose = params['verbose']
    plot = params['plot']
    time_unit = params['time_unit']
    lc_unit = params['lc_unit']
    file_fmt = params['file_fmt']
    lag_bounds = params['lag_bounds']
    threads = params['threads']

    if isinstance(lag_bounds, list):
        if len(lag_bounds) == 1:
            assert isinstance(lag_bounds[0], list) or isinstance(lag_bounds[0], str) or ( lag_bounds[0] is None )

        elif len(lag_bounds) == 2:
            pass

        else:
            for i in range(len(lag_bounds)):
                assert len(lag_bounds[i]) == 2


    if isinstance(lc_unit, str):
        lc_unit = list( np.full( len(fnames), lc_unit ) )




    len_lag_bounds = len(lag_bounds)
    if len_lag_bounds == 2:
        if not ( isinstance(lag_bounds[0], list) or ( lag_bounds[0] == 'baseline' ) ):
            len_lag_bounds = 1
        else:
            len_lag_bounds = 2
            
    if lag_bounds is None:
        lag_bounds = [None] * (len(fnames)-1)

    if len_lag_bounds != len(fnames)-1:

        lag_bounds_og = lag_bounds
        lag_bounds = []

        for i in range(len(fnames)-1):
            lag_bounds.append(lag_bounds_og)

    if (len(fnames) == 2) and ( not isinstance(lag_bounds[0], list) ):
        if not isinstance(lag_bounds[0], str):
            lag_bounds = [lag_bounds]



    xvals_tot = []
    baselines = []
    for i in range(len(fnames)):

        try:
            dat = Table.read(fnames[i], format=file_fmt)
        except:
            dat = Table.read(fnames[i], format='ascii')

        colnames = dat.colnames
        x = np.array( dat[colnames[0]] )

        sort_ind = np.argsort(x)
        x = x[sort_ind]

        xvals_tot.append(x)

    for i in range(len(fnames)-1):
        baseline = np.max([ xvals_tot[0].max(), xvals_tot[i+1].max() ]) - np.min([ xvals_tot[0].min(), xvals_tot[i+1].min() ])
        baselines.append(baseline)

    for i in range(len(fnames)-1):
        if (lag_bounds[i] is None) | (lag_bounds[i] == 'baseline'):
            lag_bounds[i] = [-baselines[i], baselines[i]]


    #Return dict so it can be passed to other functions
    output = {
        'verbose': verbose,
        'plot': plot,
        'time_unit': time_unit,
        'lc_unit': lc_unit,
        'file_fmt': file_fmt,
        'lag_bounds': lag_bounds,
        'threads': threads
    }

    return output



def set_javelin(input_args, nlc, ret_dict=False):

    default_kwargs = {
        'lagtobaseline': 0.3,
        'fixed': None,
        'p_fix': None,
        'subtract_mean': True,
        'nwalker': 100,
        'nburn': 100,
        'nchain': 100,
        'output_chains': True,
        'output_burn': True,
        'output_logp': True,
        'nbin': 50,
        'metric': 'med',
        'together': False,
        'rm_type': 'spec'
    }

    params = merge_dicts(default_kwargs, input_args)

    lagtobaseline = params['lagtobaseline']
    fixed = params['fixed']
    p_fix = params['p_fix']
    subtract_mean = params['subtract_mean']
    nwalkers = params['nwalker']
    nburn = params['nburn']
    nchain = params['nchain']
    output_chains = params['output_chains']
    output_burn = params['output_burn']
    output_logp = params['output_logp']
    nbin = params['nbin']
    metric = params['metric']
    together = params['together']
    rm_type = params['rm_type']

    if (rm_type == 'phot') & (together):
        print('ERROR: JAVELIN cannot do phtotometric RM with more than two lines.')
        print('Setting together=False')
        together = False

    if not together:

        if fixed is not None:
            if len(fixed) != nlc-1:

                fixed_og = fixed
                p_fix_og = p_fix

                fixed = []
                p_fix = []
                for _ in range(nlc-1):
                    fixed.append(fixed_og)
                    p_fix.append(p_fix_og)

        else:
            fixed = np.full( nlc-1, None )
            p_fix = np.full( nlc-1, None )

        assert len(fixed) == nlc-1

    else:
        if fixed is not None:
            assert len(fixed) == 2 + 3*( nlc - 1 )

    if ret_dict:
        return {
            'lagtobaseline': lagtobaseline,
            'fixed': fixed,
            'p_fix': p_fix,
            'subtract_mean': subtract_mean,
            'nwalker': nwalkers,
            'nburn': nburn,
            'nchain': nchain,
            'output_chains': output_chains,
            'output_burn': output_burn,
            'output_logp': output_logp,
            'nbin': nbin,
            'metric': metric,
            'together': together,
            'rm_type': rm_type
        }

    else:
        return lagtobaseline, fixed, p_fix, subtract_mean, \
            nwalkers, nburn, nchain, output_chains, \
                output_burn, output_logp, nbin, metric, together, rm_type
