import numpy as np
import matplotlib.pyplot as plt
import scipy.linalg as slinalg
import time
import h5py

from Helpful import *





def Compute_Evolution(Nsteps, state, stateDesc, result_fil, preComputation_fil, evolution='single',  logEvo = False, MAX_COUNTER = 1, EIG_COUNTER = 10, SVD_Cutoff = 1e-4, output_folder = './', ObsVal = -1):

    preComputation = h5py.File(preComputation_fil, 'r')  #np.load(preComputation_fil)[()]
    
    
    L           = int(np.array(preComputation['L'])[0])

    U           = np.array(preComputation['U'])
    Udag        = np.conj(U).T
    Diag        = np.array(preComputation['Diag'])

    Compute_D = False
    if "D_U" in preComputation.keys():
        D_U         = np.array(preComputation['D_U'])
        D_Udag      = np.conj(D_U).T
        D_Diag      = np.array(preComputation['D_Diag'])
        Compute_D   = True
    
    if not logEvo:
        Diag = Diag**(MAX_COUNTER)
    print("MAX_COUNTER: ", MAX_COUNTER)

    
    if ObsVal == -1:
        print("WRONG OBS _ Setting OBSVAL = 0")
        ObsVal = 0
    
    Obs_0 = SigmaTerms(sigmaz, L, [ ObsVal ])
    
    HPrethermal = np.array(preComputation['HPrethermal'])
        
    Obs_t       = Obs_0
    print("Number of Obs_0: " , len(Obs_0))
    res         = np.array(preComputation['res'])[0]


    args = {}
    for key in preComputation.attrs:
        args[key] = preComputation.attrs[key]

    print args
    
    preComputation.close()
    
    print L
    print res
    #InfTemp     = preComputation['InfTemp']
    #eigHPrethermal = preComputation['eigHPrethermal']
    
    w = Diag
    valuesZZ = []
    valuesZ = []
    energies = []
    entropy = []
    alpha = []
    alphaEn = []

    if Compute_D:
        D_w = D_Diag    
        D_valuesZZ = []
        D_valuesZ = []
        D_energies = []
        D_alpha = []    
        D_alphaEn = []


    states = [state]
    
    NZZ = len(Obs_0) - 1
    NZ = NZZ
    NEn = 1

    #print( "Looking at state:", state)


                          
    if res:
        print( "Using Matrix Diagonalization")
        stateleft = []
        stateright = []
        alpha =  Udag.dot( Obs_0 ).dot(U) 
        alphaEn =  Udag.dot( HPrethermal ).dot(U)

        ZZ0 = []
        Z0 = []
        en0 = []
        ent0= []

        for state in states:
            stateleft.append( np.conj(Udag.dot(state)))
            stateright.append( Udag.dot(Obs_0).dot(state).T )

        for k in range(len(states)):
            ZZ0.append( (stateleft[k].dot(alpha).dot( stateright[k] ) ) )
            Z0.append( (stateleft[k].dot(alpha).dot( np.conj(stateleft[k].T)) ) )
            en0.append( (stateleft[k].dot(alphaEn).dot( np.conj(stateleft[k].T)) )  )

            ent0.append( Entropy(np.conj(U.dot(stateleft[k]) ).T, L/2, L) )
            
        valuesZZ.append(ZZ0)
        valuesZ.append(Z0)
        energies.append(en0)
        entropy.append(ent0)

        if Compute_D:
            D_stateleft = []
            D_stateright = []
            D_alpha = D_Udag.dot( Obs_0 ).dot(D_U)
            D_alphaEn = D_Udag.dot( HPrethermal ).dot(D_U)

            D_ZZ0 = []
            D_Z0 = []
            D_en0 = []

            for state in states:
                D_stateleft.append( np.conj(D_Udag.dot(state)))
                D_stateright.append( D_Udag.dot(Obs_0).dot(state).T )

            for k in range(len(states)):
                D_ZZ0.append( (D_stateleft[k].dot(D_alpha).dot( D_stateright[k] ) ) [0,0] )
                D_Z0.append( (D_stateleft[k].dot(D_alpha).dot( np.conj(D_stateleft[k].T)) ) )
                D_en0.append( (D_stateleft[k].dot(D_alphaEn).dot( np.conj(D_stateleft[k].T)) ) )

            D_valuesZZ.append(D_ZZ0)
            D_valuesZ.append(D_Z0)
            D_energies.append(D_en0)

    else:
        print( "NO LONGER SUPPOERTED")

    # else:
    #     print( "Using power of matrix")
    #     for i in range(len(Obs_0)-1):
    #         obs0 = []
    #         for state in states:
    #             obs0.append( (state.dot(Obs_0[i]).dot(Obs_0[i]).dot(state))  [0,0] )
    #         values.append([obs0])
    
    #     en0 = []
    #     for state in states:
    #         en0.append( (state.dot(HPrethermal).dot(state)))
    #     energies.append(en0)
    #     FloquetEvo = Floquet

    c = 0
    cc = 1

    times = [0]
    counter = 0
    eigCounter = 0
    dt = 1

    

    def compute_Expectations():
        if res:
            obst = []
            for k in range(len( states)):
                obst.append( (
                    np.multiply(stateleft[k] ,np.conj(Diag)).dot( alpha ).dot(
                        np.multiply( stateright[k].T, Diag).T)
                )[0,0] )

            valuesZZ.append(obst)
            

            Zt = []
            for k in range(len(states)):
                Zt.append( (
                    np.multiply(stateleft[k] , np.conj(Diag)).dot( alpha ).dot(
                        np.multiply( np.conj(stateleft[k]), Diag).T)
                )[0,0] )
                    
            valuesZ.append(Zt)


            ent = []
            for k in range(len(states)):
                ent.append( (
                    np.multiply(stateleft[k] , np.conj(Diag)).dot( alphaEn ).dot(
                        np.multiply( np.conj(stateleft[k]), Diag).T)
                ) )
            energies.append(ent)

            entrop = []
            for k in range(len(states)):
                entrop.append(
                    Entropy( U.dot(np.multiply( np.conj(stateleft[k]), Diag)).T, L/2, L)
                )
            entropy.append(entrop)
            
            if Compute_D:
                D_obst = []
                for k in range(len( states)):
                    D_obst.append( (
                        np.multiply(D_stateleft[k] ,np.conj(D_Diag)).dot( D_alpha ).dot(
                            np.multiply( D_stateright[k].T, D_Diag).T)
                    ) )
                D_valuesZZ.append(D_obst)

                D_Zt = []
                for k in range(len(states)):
                    D_Zt.append( (
                        np.multiply(stateleft[k] , np.conj(D_Diag)).dot( D_alpha ).dot(
                            np.multiply( np.conj(stateleft[k]), D_Diag).T)
                    ) )
                D_valuesZ.append(D_Zt)

                D_ent = []
                for k in range(len(states)):
                    D_ent.append( (
                        np.multiply(D_stateleft[k] , np.conj(D_Diag)).dot( D_alphaEn ).dot(
                            np.multiply( np.conj(D_stateleft[k]), D_Diag).T)
                    ))#[0,0] )
                D_energies.append(D_ent)
                
        else:
            print( "NO LONGER SUPPORTED")
            # if i < len(Obs_0) - 1:
            #     obst = []
            #     prod = prod.dot(Obs_0[i]) 
            #     for state in states:
            #         obst.append( (np.conj(state).dot( prod ).dot(state) )  [0,0] )
            #     values[i].append(obst)
            # elif i == len(Obs_0) - 1:
            #     ent = []
            #     for state in states:
            #         ent.append( (np.conj(state).dot( prod ).dot(state))  [0,0] )
            #     energies.append(ent)


    while times[-1] < Nsteps:
        #print( times[-1])
        # Evolve the different observables:
        if logEvo:
            if res == True:
                compute_Expectations()
                    
                                
            else:
                print( "NO LONGER SUPPORTED")
                    # prod =  np.conj(FloquetEvo).T.dot(Obs_t[i]).dot( FloquetEvo)
                    # Obs_t[i] = prod

                    # if eigCounter == EIG_COUNTER:
                    #     print( "Checking Numerics")
                    #     print( times[-1])
                    #     Need_SVD = EigenValueError(FloquetEvo , SVD_Cutoff )

                    #     eigCounter = 0
                    #     #l = min(np.abs(np.linalg.eigvals( FloquetEvo) ) )
                    #     #print( l)
                    #     if Need_SVD: #l < 1 - SVD_Cutoff:
                    #         #print( "Lowest absolute eigenvalue", l)
                    #         print( "Applying SVD procedure")
                    #         print( "Time: ", times[-1])
                    #         (U, s, V) = np.linalg.svd( FloquetEvo )
                    #         FloquetEvo = U.dot(V)
                    # else:
                    #     eigCounter += 1

                    # compute_Expectations(prod, i)
                        
                    # if i < len(Obs_0) - 1:
                    #     for state in states:
                    #         obst.append( (state.dot( prod ).dot(Obs_0[i]).dot(state) )[0,0] )
                    #     values[i].append(obst)
                    # elif i == len(Obs_0) - 1:
                    #     for state in states:
                    #         ent.append( (state.dot( prod ).dot(state))[0,0] )
                    #     energies.append([ent])
                        
        else:
            if res:
                    compute_Expectations()
                    
            else:
                print( "NO LONGER SUPPORTED")
                # prod = np.conj(Floquet).T.dot(Obs_t[i]).dot(Floquet)
                #     Obs_t[i] = prod
                #     compute_Expectations(prod, i)
                #     #values[i].append(prod[state,state])

        if logEvo:

            times.append( times[-1] + dt )
            if counter < MAX_COUNTER:
                counter += 1
            else:
                counter = 0 
                dt *= 2
                if res:
                    w = w * w
                    w = w / np.abs(w)

                    if Compute_D:
                        D_w = D_w * D_w
                        D_w = D_w / np.abs(D_w)
                else:
                    FloquetEvo = FloquetEvo.dot(FloquetEvo)

            if res:
                Diag = Diag * w
                Diag = Diag/np.abs(Diag)

                if Compute_D:
                    D_Diag = D_Diag * D_w
                    D_Diag = D_Diag/np.abs(D_Diag)
                    
        else:
            times.append(times[-1] + MAX_COUNTER)
            if res:
                Diag = Diag * w
                Diag = Diag/np.abs(Diag)

        
    times = np.array(times[:])

    
    valuesZZ = np.array(valuesZZ)
    valuesZ = np.array(valuesZ)
    energies = np.array( energies)
    entropy = np.array(entropy)

    if Compute_D:
        D_valuesZZ = np.array( D_valuesZZ )
        D_valuesZ = np.array( D_valuesZ )
        D_energies = np.array(D_energies)
    
    if  np.max(np.abs( np.imag( energies) ) )> 1e-14:
        print( "TOO MUCH IMAGINARY PART")
        #print( energies)
        print( np.max(np.abs( np.imag( energies) ) ))

        #print( stateDesc)
    info = {'L': L,
            'args': args,
            'state': state,
            'stateDesc': stateDesc,
            'Nsteps': Nsteps,
            'result_fil': result_fil,
            'preComputation_fil': preComputation_fil,
            'evolution': evolution,
            'logEvo': logEvo,
            #'InfTemp': InfTemp,
            'SVD_Cutoff': SVD_Cutoff,
            #'EigHPrethermal': eigHPrethermal,
            'EigFloquet': w}
            
    output = {'valuesZ': valuesZ,
              'valuesZZ': valuesZZ,
              'energies': energies,
              'entropy': entropy,
              # 'D_valuesZ': D_valuesZ,
              # 'D_valuesZZ': D_valuesZZ,
              # 'D_energies': D_energies,              
              'times': times,
              'info': info,
    }

    if Compute_D:
        output['D_valuesZ'] = D_valuesZ
        output['D_valuesZZ'] = D_valuesZZ
        output['D_energies'] = D_energies

    print( "")
    print( result_fil + ".npy")
    print( output_folder + result_fil)

    #np.save("here", output)
    #h5_output = h5py.File(output_folder + result_fil + '.h5', "w")
    np.save(output_folder + result_fil, output)

    # for key in info.keys():
    #     h5_output.create_dataset( key, data=info[key], compression=True)
    # for key in output.keys():
    #     h5_output.create_dataset( key, data=output[key], compression=True)    
    # h5_output.close()
        
    return output
        
            
