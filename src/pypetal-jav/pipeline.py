import os
import warnings

import numpy as np
from astropy.table import Table

import pypetal_jav.modules as modules

from pypetal_jav import defaults
from pypetal_jav.petalio import write_data
from pypetal_jav.utils import fix_jav_params_after_ufj



def run_pipeline(output_dir, line_names,
                 javelin_params={}, use_for_javelin=False, 
                 drw_rej_res={}, **kwargs):


    output_dir = os.path.abspath(output_dir) + r'/'

    #pyPetal will create the output directory if it doesn't exist
    #Also will create the javelin subdirectories
    if not os.path.exists(output_dir):
        raise Exception('This assumes that pypetal.pipeline.run_pipeline has already been run.')


    #Look for light curve filenames
    line_fnames = []
    if output_dir + 'processed_lcs/' in glob.glob(output_dir +'*/'):
        cont_fname = output_dir + 'processed_lcs/' + line_names[0] + '_data.dat'
        line_fnames = [output_dir + 'processed_lcs/' + name + '_data.dat' for name in line_names[1:]]
    else:
        cont_fname = output_dir + 'light_curves/' + line_names[0] + '.dat'
        line_fnames = [output_dir + 'light_curves/' + name + '.dat' for name in line_names[1:]]

    if type(line_fnames) is str:
        line_fnames = [line_fnames]


    #Read in general kwargs
    general_kwargs = defaults.set_general(kwargs, fnames)



    #Get "together"
    _, fixed, p_fix, _, _, _, _, _, _, _, _, _, together, rm_type = defaults.set_javelin(javelin_params, fnames)


    javelin_params['fixed'] = fixed
    javelin_params['p_fix'] = p_fix

    if rm_type == 'spec':
        if together:
            nfixed = 2 + 3*( len(fnames)-1 )
        else:
            nfixed = 5
    elif rm_type == 'phot':
        nfixed = 6



    #Name lines if unnamed
    if line_names is None:
        line_names = np.zeros( len(line_fnames), dtype=str )
        for i in range(len(line_fnames)):
            line_names.append('Line {}'.format(i+1))


    if use_for_javelin:
        javelin_params = fix_jav_params_after_ufj(javelin_params, drw_rej_res)


    javelin_res = modules.javelin_tot(cont_fname, line_fnames, line_names, output_dir, general_kwargs, javelin_params)

    return javelin_res
