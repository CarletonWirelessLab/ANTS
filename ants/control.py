#!/usr/bin/python3

import sys
import subprocess
import threading
import time
import queue
import os
import datetime
from plotter import *

class ANTS_Controller():

    def __init__(self):

        # Class variables used for the subprocesses run, if any, of the tools
        # run when their checkboxes are selected
        self.usrp_proc = None
        self.plotter_proc = None
        self.iperf_client_proc = None
        self.iperf_server_proc = None

        # iperf-specific variables. The client_addr and server_addr variables
        # are self-explanatory and are set from the GUI's lineedit boxes.
        # Rate and mem_addr are for the other inputs to the client call
        # iperf -c [IP] -u -b[100]M -S [0x00]  -t10000000000
        self.iperf_client_addr = None
        self.iperf_server_addr = None
        self.iperf_rate = None
        self.iperf_mem_addr = None

        # Default run time length to 0.5 seconds if no time is provided
        self.run_time = 0.5

        # Output/conversion file name. Set to "no_name" as default in case the
        # user has not yet given a file name to the run in the GUI
        self.file_name = "no_name"

        # Used to set the access category. '0' is voice, '1' is video, '2' is
        # best effort, '3' is background
        self.access_category = 0

        # Path of project directory for use in calls to scripts in utils/
        #self.working_dir = os.getcwd()
        self.working_dir = os.path.dirname(os.path.abspath(__file__))

        # Path of the utilities (i.e. non-MATLAB scripts) used to run the tests
        self.utils_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'utils'))
        self.utils_dir = self.utils_dir + '/'

        # Path for calling scripts in simulation mode
        self.sim_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'utils/sim'))
        self.sim_dir = self.sim_dir + '/'


    # Make the timestamped data directory, and then return the full path for
    # writing data files to
    def make_data_dir(self, test_name):
        # Create the timestamp
        time = str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S"))
        time = time.replace(' ', '_')

        # Get the full path of the data file to be created
        dir_name = self.file_name + "_" + time + "/"
        location = os.path.dirname(os.path.abspath(__file__))
        full_path = location + "/../tests/" + dir_name

        # Make the data file path if it doesn't exist (this should always run as long as the timestamp is present)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        print("Generated the test directory {0}.\n".format(full_path))

        return full_path

    # Runs a subprocess for the USRP based on the usrp_control_args variable. Future-proofing method
    # for when the option is added to run the USRP only
    def start_usrp(self):
        print("Running USRP...\n")

        if self.access_category == 1:
            self.plotter_ac = "video"
        elif self.access_category == 2:
            self.plotter_ac = "best_effort"
        elif self.access_category == 3:
            self.plotter_ac = "background"
        else:
            self.plotter_ac = "voice"

        # Create the data directory for the run
        self.data_dir = self.make_data_dir(self.file_name)
        self.test_path = self.data_dir + self.file_name
        self.bin_path = self.test_path + "_" + self.plotter_ac + ".bin"
        print("The binary data file will be written to {0}.\n".format(self.bin_path))

        # Create the argument list to pass to the USRP subprocess that will be instantiated
        self.usrp_control_args = ["python", self.utils_dir + "writeIQ.py", self.test_path, str(self.run_time), self.plotter_ac]

        # Run the USRP process with the necessary arguments
        self.usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        while self.usrp_proc.poll() is None:
            continue

        print("Done sensing medium\n")

        return

    # Runs the USRP and iperf tools simultaneously
    def start_usrp_iperf(self):
        print("Running USRP with interference injected using iperf...\n")

        if self.access_category == 1:
            self.plotter_ac = "video"
            self.iperf_client_ac = "0x80"
        elif self.access_category == 2:
            self.plotter_ac = "best_effort"
            self.iperf_client_ac = "0x00"
        elif self.access_category == 3:
            self.plotter_ac = "background"
            self.iperf_client_ac = "0x20"
        else:
            self.plotter_ac = "voice"
            self.iperf_client_ac = "0xC0"

        # Create the data directory for the run
        self.data_dir = self.make_data_dir(self.file_name)
        self.test_path = self.data_dir + self.file_name
        self.bin_path = self.test_path + "_" + self.plotter_ac + ".bin"

        # Print the file path for debug purposes
        print("The binary data file will be written to {0}.\n".format(self.bin_path))

        # Set the arguments to be used to run the USRP
        self.usrp_control_args = ["python", self.utils_dir + "writeIQ.py", self.test_path, str(self.run_time), self.plotter_ac]

        # Ensure that the client and server addresses are set to something other than "None"
        if self.iperf_client_addr == None:
            self.iperf_client_addr = "10.1.11.115"

        if self.iperf_server_addr == None:
            self.iperf_server_addr = "10.1.1.120"

        # The arguments to run the iperf client
        self.iperf_client_args = ["iperf", "-B", "{0}".format(str(self.iperf_client_addr)), "-c", "10.2.1.120", "-u", "-b", "150M", "-t 10000000000000", "-i 1", "-S {0}".format(self.iperf_client_ac)]
        print("iperf client args are:\n")
        print(self.iperf_client_args)
        # The arguments to run the iperf server
        self.iperf_server_args = ["iperf", "-B", "{0}".format(str(self.iperf_server_addr)), "-s", "-u", "-t 1000000000000000", "-i 1"]
        print("iperf server args are:\n")
        print(self.iperf_server_args)

        # Run the iperf commands and print debug information
        print("iperf server IP is {0}\n".format(self.iperf_server_addr))
        print("iperf client IP is {0}\n".format(self.iperf_client_addr))
        self.iperf_server_proc = subprocess.Popen(self.iperf_server_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        self.iperf_client_proc = subprocess.Popen(self.iperf_client_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        # Wait for 3 seconds to ensure the iperf data has begun transferring
        time.sleep(3)
        # Start the USRP
        self.usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        # Continuously check to see if the USRP is running, then break out when it has stopped
        while True:
            self.usrp_proc.poll()
            if self.usrp_proc.returncode is not None:
                break

        # Close the iperf processes as soon as the USRP is done sensing the medium
        self.iperf_client_proc.kill()
        self.iperf_server_proc.kill()
        print("Done sampling the medium. iperf processes killed.\n")

        return

    #Method to create an ANTS_Plotter instance for analyzing and plotting the collected data
    def make_plots(self):
        if hasattr(self, "plotter"):
            del self.plotter
        print("Running data conversion and plot routine on {0}...\n".format(self.bin_path))
        # Create and run an actual plotter instance
        print("The test path is {0}\n".format(self.test_path))
        self.plotter = ANTS_Plotter(self.plotter_ac, self.test_path, 20e6)
        self.plotter.read_and_parse()
        self.plotter.setup_packet_data()
        self.plotter.write_results_to_file()
        self.plotter.plot_results()

        # Delete the current plotter when done to avoid excessive memory usage
        #del self.plotter
