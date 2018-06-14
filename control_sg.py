import subprocess as sbp
import random as rnd
import threading as thrd
import time

def control_sg(setup_file, on_file, off_file, rate, signal_format="awgn", output_mode="exp", seed=None, run_duration=10.0, executable="sg_sequence", test_mode=True):

    # Set a new seed for the randomness (in functions that use it) each time the
    # program is run. Defaults to the system time
    rnd.seed(seed)

    # Define the IP to connect to based on whether or not the test_mode flag
    # was set. It must explicitly be set to False in order to connect to an
    # actual external device. Note that the executables should point to
    # port 5025
    sg_ip = ""
    if test_mode == True:
        sg_ip = "0.0.0.0"
    else:
        sg_ip = "134.117.62.53"


    # Define some SCPI commands to toggle the ARB and RF outputs on and off
    arb_on_command = ":RAD:AWGN:ARB:STAT 1"
    arb_off_command = ":RAD:AWGN:ARB:STAT 0"
    rf_on_command = "OUTP:STAT 1"
    rf_off_command = "OUTP:STAT 0"

    # Check to see which output mode was set. Defaults to using the exponential
    # distribution from the Python random module
    on_time = 0
    if output_mode == "exp":
        on_time = rnd.expovariate(rate)
    elif output_mode == "const":
        on_time = rate
    else:
        on_time = rnd.expovariate(rate)
    off_time = 1 - on_time

    signal=""
    if signal_format == "awgn":
        setup_args = ("../{0} {1} {2}".format(executable, sg_ip, arb_on_command)).split()
        popen = sbp.Popen(setup_args, stdout=sbp.PIPE)
        popen.wait()
    elif signal_format == "carrier":
        pass

    on_args = ("../{0} {1} {2}".format(executable, sg_ip, rf_on_command))
    on_args_split = on_args.split()
    off_args = ("../{0} {1} {2}".format(executable, sg_ip, rf_off_command))
    off_args_split = off_args.split()

    while(True):
        popen = sbp.Popen(on_args_split, stdout=sbp.PIPE)
        popen.wait()
        print(on_args)
        time.sleep(on_time)

        popen = sbp.Popen(off_args_split, stdout=sbp.PIPE)
        popen.wait()
        print(off_args)
        time.sleep(off_time)


    #output = popen.stdout.read()
    #print(output)

if __name__ == '__main__':
    control_sg("test/control_sequences/awgn_setup.txt", "test/control_sequences/awgn_on.txt", "test/control_sequences/awgn_off.txt", executable="ks_lanio")
