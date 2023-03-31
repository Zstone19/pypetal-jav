import os

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import pypetal_jav.defaults as defaults
import pypetal_jav.plotting as plotting
import pypetal_jav.utils as utils
from pypetal_jav.petalio import write_data


def javelin_tot(cont_fname, line_fnames, line_names, output_dir, general_kwargs, kwargs):

    if line_fnames is str:
        line_fnames = [line_fnames]

    #--------------------------------------------------
    #Read general kwargs

    verbose = general_kwargs['verbose']
    plot = general_kwargs['plot']
    time_unit = general_kwargs['time_unit']
    lc_unit = general_kwargs['lc_unit']
    laglimit = general_kwargs['lag_bounds']
    threads = general_kwargs['threads']

    #--------------------------------------------------
    #Read kwargs

    lagtobaseline, fixed, p_fix, subtract_mean, \
        nwalkers, nburn, nchain, output_chains, \
            output_burn, output_logp, nbin, metric, \
                together, rm_type = defaults.set_javelin( kwargs, len(line_names) )

    #--------------------------------------------------
    #Account for parameters if javelin['together'] = False
    if not together:

        if ( type(laglimit) is str ) | ( laglimit is None ):
            laglimit = np.full( len(line_fnames), laglimit )

    #--------------------------------------------------

    if ( not isinstance(laglimit, str) ) & ( laglimit is not None ):
        if len(laglimit) > 2:
            laglimit_str = 'array'
        else:
            laglimit_str = laglimit
    else:
        laglimit_str = laglimit


    if verbose:
        txt_str = """
Running JAVELIN
--------------------
rm_type: {}
lagtobaseline: {}
laglimit: {}
fixed: {}
p_fix: {}
subtract_mean: {}
nwalker: {}
nburn: {}
nchain: {}
output_chains: {}
output_burn: {}
output_logp: {}
nbin: {}
metric: {}
together: {}
--------------------
        """.format( rm_type, lagtobaseline, laglimit_str, not (fixed is None), not (fixed is None),
                    subtract_mean, nwalkers, nburn, nchain, output_chains,
                    output_burn, output_logp, nbin, metric, together )

        print(txt_str)

    if together:
        res = utils.run_javelin(cont_fname, line_fnames, line_names,
                                rm_type=rm_type,
                                output_dir=output_dir + r'javelin/',
                                lagtobaseline=lagtobaseline, laglimit=laglimit,
                                fixed=fixed, p_fix=p_fix, subtract_mean=subtract_mean,
                                nwalkers=nwalkers, nburn=nburn, nchain=nchain, threads=threads,
                                output_chains=output_chains, output_burn=output_burn, output_logp=output_logp,
                                nbin=nbin, verbose=verbose, plot=plot)


        #Plot histograms
        fig, ax = plotting.plot_javelin_hist( res, fixed=fixed, nbin=nbin,
                                             time_unit=time_unit,
                                             remove_fixed=False,
                                             fname= output_dir + 'javelin/javelin_histogram.pdf' )

        if plot:
            plt.show()

        plt.cla()
        plt.clf()
        plt.close()


        if (fixed is None) | (fixed is np.ones( 2 + 3*len(line_fnames) )):

            #Corner plot
            fig, ax = plotting.javelin_corner(res,
                                            fname= output_dir + 'javelin/javelin_corner.pdf' )


            if plot:
                plt.show()

            plt.cla()
            plt.clf()
            plt.close()




        bestfit_model = utils.javelin_pred_lc( res['rmap_model'],
                                            res['tot_dat'].jlist[0], res['tot_dat'].jlist[1:],
                                            metric=metric)

        res['bestfit_model'] = bestfit_model


        #Plot model fits
        fig, ax = plotting.plot_javelin_bestfit(res, bestfit_model, time_unit=time_unit, lc_unit=lc_unit,
                                                fname= output_dir + 'javelin/javelin_bestfit.pdf' )

        if plot:
            plt.show()

        plt.cla()
        plt.clf()
        plt.close()




        #Write fits to light curves
        for i in range(len(line_names)):
            dat_fname = output_dir + r'javelin/' + line_names[i] + '_lc_fits.dat'
            dat = [ bestfit_model.jlist[i],
                    bestfit_model.mlist[i] + bestfit_model.blist[i],
                    bestfit_model.elist[i] ]
            write_data( dat, dat_fname )


        return res


    else:
        res_tot = []

        for i in range(len(line_fnames)):
            names_i = [line_names[0], line_names[i+1]]

            if isinstance(laglimit[i], str):
                input_laglimit = laglimit[i]
            else:
                input_laglimit = [laglimit[i]]

            res = utils.run_javelin(cont_fname, line_fnames[i], names_i,
                                    rm_type=rm_type,
                                    output_dir=output_dir + names_i[1] + r'/javelin/',
                                    lagtobaseline=lagtobaseline, laglimit=input_laglimit,
                                    fixed=fixed[i], p_fix=p_fix[i], subtract_mean=subtract_mean,
                                    nwalkers=nwalkers, nburn=nburn, nchain=nchain, threads=threads,
                                    output_chains=output_chains, output_burn=output_burn, output_logp=output_logp,
                                    verbose=verbose, plot=plot)


            #Plot histograms
            fig, ax = plotting.plot_javelin_hist( res, fixed=fixed[i], nbin=nbin,
                                                  time_unit=time_unit,
                                                  remove_fixed=False,
                                                  fname= output_dir + line_names[i+1] + r'/javelin/javelin_histogram.pdf' )

            if plot:
                plt.show()

            plt.cla()
            plt.clf()
            plt.close()



            #Corner plot
            if (fixed[i] is None) | (fixed[i] is np.ones( 2 + 3*len(line_fnames) )):
                fig, ax = plotting.javelin_corner(res,
                                                fname= output_dir + line_names[i+1] + '/javelin/javelin_corner.pdf' )

                if plot:
                    plt.show()

                plt.cla()
                plt.clf()
                plt.close()


            bestfit_model = utils.javelin_pred_lc( res['rmap_model'],
                                                res['tot_dat'].jlist[0], res['tot_dat'].jlist[1:],
                                                metric=metric)



            res['bestfit_model'] = bestfit_model
            res_tot.append(res)

            #Plot model fits
            fig, ax = plotting.plot_javelin_bestfit(res, bestfit_model, time_unit=time_unit,
                                                    lc_unit=[lc_unit[0], lc_unit[i+1]],
                                                    fname= output_dir + line_names[i+1] + '/javelin/javelin_bestfit.pdf' )

            if plot:
                plt.show()

            plt.cla()
            plt.clf()
            plt.close()



            #Write fits to light curves
            for j in range( bestfit_model.nlc ):

                if j == 0:
                    name = line_names[0]
                else:
                    name = line_names[i+1]

                dat_fname = output_dir + line_names[i+1] + r'/javelin/' + name + '_lc_fits.dat'
                dat = [ bestfit_model.jlist[j],
                        bestfit_model.mlist[j] + bestfit_model.blist[j],
                        bestfit_model.elist[j] ]
                write_data( dat, dat_fname )

        return res_tot