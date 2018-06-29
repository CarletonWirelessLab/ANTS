#!/bin/python3

from echo_client import echo_to_server
import random as rnd
import subprocess
import threading
import time

def control_sg(setup_file, on_file, off_file, lower_bound=0.01, \
               upper_bound=0.6, \
               seed=None, initial_delay=0, run_duration=2.5, \
               executable="ks_lanio", test_mode=True, \
               graphics=False):

    # Set a new seed for the randomness (in functions that use it) each time the
    # program is run. Defaults to the system time
    rnd.seed(seed)

    # Define the IP to connect to based on whether or not the test_mode flag
    # was set. It must explicitly be set to False in order to connect to an
    # actual external device. Note that the executables should point to
    # port 5025 (matches the port that the E4438C uses)
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

    # Run any SCPI setup file first, for doing things such as turning the AWGN
    # subsystem on before beginning to toggle the RF output
    setup_args = ("./{0} {1} {2}".format(executable, sg_ip, arb_on_command)).split()
    popen = subprocess.Popen(setup_args, stdout=subprocess.PIPE)
    popen.wait()

    # Dummy variables for when in test mode and the USRP is unavailable
    started_fake_usrp = "Started fake USRP"
    stopped_fake_usrp = "Stopped fake USRP"
    dummy_USRP_on = ["./echo_client.py", "Started fake USRP"]
    dummy_USRP_off = ["./echo_client.py", "Stopped fake USRP"]

    # Split the command and argument for running the tool (either the E4438C
    # controller itself, or the echo_client in test mode) up so that they can
    # be passed as arguments to Popen() within the while loop
    on_args = ("\n./{0} {1} {2}".format(executable, sg_ip, rf_on_command))
    on_args_split = on_args.split()
    off_args = ("\n./{0} {1} {2}".format(executable, sg_ip, rf_off_command))
    off_args_split = off_args.split()

    # The actual "control" block begins here
    total_time = 0
    start_time = time.time()
    print("Started recording\n")
    on_time = 0
    off_time = 0

    # Turn on the USRP for sensing the medium
    #popen = subprocess.Popen(dummy_USRP_on, stdout=subprocess.PIPE)
    #popen.wait()
    
    # initial delay
    time.sleep(initial_delay)
    # While time measured is less than specified run duration, toggle the
    # signal generator's RF output on and off periodically with an on
    # time specified by the on_time parameter.
    while(total_time + initial_delay < run_duration):

        # Generate a random number between the bounds specified to use as the
        # on time of the pulse, then calculate its corresponding off time
        on_time = rnd.uniform(lower_bound, upper_bound)
        off_time = upper_bound - on_time

        # Turn on the RF output, and then wait for the on part of the cycle
        # to end
        popen = subprocess.Popen(on_args_split, stdout=subprocess.PIPE)
        popen.wait()
        print(on_args)
        time.sleep(on_time)

        # Turn off the RF output, and then wait for the off part of the cycle
        # to end
        popen = subprocess.Popen(off_args_split, stdout=subprocess.PIPE)
        popen.wait()
        print(off_args)
        time.sleep(off_time)

        # add the time elapsed to the total_time variable to keep track of
        # run time
        total_time = total_time + time.time() - start_time

    # Turn off the USRP once the test run is finished
    #popen = subprocess.Popen(dummy_USRP_off, stdout=subprocess.PIPE)
    #popen.wait()
    print("Stopped injection\n")
    print("Ran for {0} seconds\n".format(total_time))

# What to do if this script is called externally
if __name__ == '__main__':
    control_sg("awgn_setup.txt", "awgn_on.txt", "awgn_off.txt", run_duration=2.5, test_mode=False, upper_bound = 4.0, seed=3.775, initial_delay=2)
