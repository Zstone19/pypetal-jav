import numpy as np


def set_javelin(input_args, fnames):

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

    params = { **default_kwargs, **input_args }

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
            if len(fixed) < len(fnames)-1:

                fixed_og = fixed
                p_fix_og = p_fix

                fixed = []
                p_fix = []
                for i in range(len(fnames)-1):
                    fixed.append(fixed_og)
                    p_fix.append(p_fix_og)

        else:
            fixed = np.full( len(fnames)-1, None )
            p_fix = np.full( len(fnames)-1, None )

        assert len(fixed) == len(fnames)-1

    else:
        if fixed is not None:
            assert len(fixed) == 2 + 3*( len(fnames) - 1 )


    return lagtobaseline, fixed, p_fix, subtract_mean, \
        nwalkers, nburn, nchain, output_chains, \
            output_burn, output_logp, nbin, metric, together, rm_type
