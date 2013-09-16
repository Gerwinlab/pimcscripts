import pylab as pl
import glob,argparse,sys
import averagingTools as aTools

def parseCMD():
    ''' Parse the command line. '''
    parser = argparse.ArgumentParser(description='pulls down lots of files.')
    parser.add_argument('fileNames', help='Data File Name.', nargs='+')
    parser.add_argument('-t', '--typeOfAverage', type=str,
            default='jackknife',
            help='NOT WORKING YET: Do you want jackknife or bootstrap?')
    parser.add_argument('-s', '--skip', type=int,
            default=1000,
            help='Number of bins to skip')

    return parser.parse_args()

def main():

    args = parseCMD()
   
    # Check if our data file exists, if not: write one.
    # Otherwise, open the file and plot.
    check = glob.glob('*JackKnifeData_Cv.dat*')
    
    if check == []:
        
        fileNames = args.fileNames
        skip = args.skip
        temps,Cvs,CvsErr = pl.array([]),pl.array([]),pl.array([])
   
        # open new data file, write headers
        fout = open('JackKnifeData_Cv.dat', 'w')
        fout.write('#%09s\t%10s\t%10s\n'% ('T', 'Cv', 'CvErr'))
        
        # perform jackknife analysis of data, writing to disk
        for fileName in fileNames:
            temps = pl.append(temps, float(fileName[-40:-34]))
            EEcv, Ecv, dEdB = pl.loadtxt(fileName, unpack=True, usecols=(11,12,13))
            jkAve, jkErr = aTools.jackknife(EEcv[skip:],Ecv[skip:],dEdB[skip:])
            print '<est> = ',jkAve,' +/- ',jkErr
            Cvs = pl.append(Cvs,jkAve)
            CvsErr = pl.append(CvsErr,jkErr)
            fout.write('%10s\t%10s\t%10s\n' %(float(fileName[-40:-34]), jkAve, jkErr))
        
        fout.close()

    else:
        print 'Found existing data file in CWD.'
        temps,Cvs,CvsErr = pl.loadtxt('JackKnifeData_Cv.dat', unpack=True)

    # make array of energies
    Es, EsErr = pl.array([]),pl.array([])
    ET, ETerr = pl.array([]),pl.array([])

    for fileName in args.fileNames:
        Ecv,Eth = pl.loadtxt(fileName, unpack=True, usecols=(4,-5))
        Es = pl.append(Es,pl.average(Ecv))
        ET = pl.append(ET, pl.average(Eth))
        EsErr = pl.append(EsErr, pl.std(Ecv)/pl.sqrt(float(len(Ecv))))
        ETerr = pl.append(ETerr, pl.std(Eth)/pl.sqrt(float(len(Eth))))


    # plot specific heat for QHO
    tempRange = pl.arange(0.01,1.0,0.01)
    Eanalytic = 0.5/pl.tanh(1.0/(2.0*tempRange))
    CvAnalytic = 1.0/(4.0*(tempRange*pl.sinh(1.0/(2.0*tempRange)))**2)

    pl.figure(1)
    pl.plot(tempRange,CvAnalytic, label='Exact')
    pl.errorbar(temps,Cvs,CvsErr, label='PIMC',color='Violet',fmt='o')
    pl.xlabel('Temperature [K]')
    pl.ylabel('Specific Heat')
    pl.title('1D QHO -- 1 boson')
    pl.legend(loc=2)

    pl.figure(2)
    pl.plot(tempRange,Eanalytic, label='Exact')
    pl.errorbar(temps,Es,EsErr, label='PIMC virial',color='Lime',fmt='o')
    pl.errorbar(temps,ET,ETerr, label='PIMC therm.',color='k',fmt='o')
    #pl.scatter(temps,Es, label='PIMC')
    pl.xlabel('Temperature [K]')
    pl.ylabel('Energy [K]')
    pl.title('1D QHO -- 1 boson')
    pl.legend(loc=2)

    pl.show()

# =============================================================================
if __name__=='__main__':
    main()