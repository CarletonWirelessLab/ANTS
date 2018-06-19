#!/bin/python3

from tkinter import filedialog
from echo_client import echo_to_server
import random as rnd
import subprocess
import threading
import time

def control_sg(setup_file, on_file, off_file, rnd_scale=5, lower_bound=0.01, \
               upper_bound=2, signal_format="awgn", output_mode="scaled", \
               seed=None, initial_delay=2.0, run_duration=10.0, \
               executable="ks_lanio", instr="echo_client.py", test_mode=True, \
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

    # Check to see which output mode was set. Defaults to using the exponential
    # distribution from the Python random module
    # on_time = 0
    # if output_mode == "exp":
    #     on_time = rnd.expovariate(rate)
    # elif output_mode == "const":
    #     on_time = rate
    # else:
    #     on_time = rnd.expovariate(rate)
    # off_time = 1 - on_time

    signal=""
    if signal_format == "awgn":
        #setup_args = ("../{0} {1} {2}".format(executable, sg_ip, arb_on_command)).split()
        setup_args = ("./{0} {1} {2}".format(executable, sg_ip, arb_on_command)).split()
        popen = subprocess.Popen(setup_args, stdout=subprocess.PIPE)
        popen.wait()
    elif signal_format == "carrier":
        pass

    started_fake_usrp = "Started fake USRP"
    stopped_fake_usrp = "Stopped fake USRP"

    #dummy_USRP_on_args = ("./{0} {1}".format(instr, started_fake_usrp))
    #dummy_USRP_on_split = dummy_USRP_on_args.split()
    dummy_USRP_on = ["./echo_client.py", "Started fake USRP"]
    #dummy_USRP_off_args = ("./{0} {1}".format(instr, stopped_fake_usrp))
    #dummy_USRP_off_split = dummy_USRP_off_args.split()
    dummy_USRP_off = ["./echo_client.py", "Stopped fake USRP"]

    on_args = ("./{0} {1} {2}".format(executable, sg_ip, rf_on_command))
    on_args_split = on_args.split()
    off_args = ("./{0} {1} {2}".format(executable, sg_ip, rf_off_command))
    off_args_split = off_args.split()

    total_time = 0
    start_time = time.time()
    print("Started recording\n")
    on_time = 0
    off_time = 0

    popen = subprocess.Popen(dummy_USRP_on, stdout=subprocess.PIPE)
    popen.wait()

    while(total_time + initial_delay < run_duration):

        time.sleep(initial_delay)

        # Check to see which output mode was set. Generates random on times
        # between 0 and a number specified by rnd_scale; otherwise defaults to
        # numbers between 0 and 1
        if output_mode == "scaled":
            on_time = rnd.random()*rnd_scale
            print(on_time)
            off_time = rnd_scale - on_time
            print(off_time)
        elif output_mode == "uniform":
            on_time = rnd.uniform(lower_bound, upper_bound)
            off_time = upper_bound - on_time
        else:
            on_time = rnd.random(dummy_USRP_on_split)
            off_time = 1 - on_time


        popen = subprocess.Popen(on_args_split, stdout=subprocess.PIPE)
        popen.wait()
        print(on_args)
        time.sleep(on_time)


        popen = subprocess.Popen(off_args_split, stdout=subprocess.PIPE)
        popen.wait()
        print(off_args)
        time.sleep(off_time)

        total_time = total_time + on_time + off_time
    popen = subprocess.Popen(dummy_USRP_off, stdout=subprocess.PIPE)
    popen.wait()
    print("Stopped recording\n")
    print("Ran for {0} seconds\n".format(time.time() - start_time))


    #output = popen.stdout.read()
    #print(output)

if __name__ == '__main__':
    #control_sg("test/control_sequences/awgn_setup.txt", "test/control_sequences/awgn_on.txt", "test/control_sequences/awgn_off.txt", rate = 2)
    control_sg("awgn_setup.txt", "awgn_on.txt", "awgn_off.txt", rnd_scale=2, run_duration=20.0, output_mode="uniform", test_mode=True, upper_bound = 4.0)
