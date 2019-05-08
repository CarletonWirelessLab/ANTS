#!/usr/bin/python3

import sys
import subprocess
import color_subprocess
import threading
import time
import queue
import os
import datetime
import statistics as stat
from plotter import *
from network_connect import *
from setup_routing import *
from ipaddress import *

class ANTS_Controller():
    def __init__(self):
        self.UUT_type = "Supervising"
        self.essid = None
        self.center_frequency = '5.180'
        self.communication_success = 0
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
        self.iperf_ap_addr = None
        self.iperf_rate = None
        self.iperf_mem_addr = None
        self.iperf_bw = None

        # Default run time length to 0.5 seconds if no time is provided
        self.run_time = 0.5

        # The delay between the time that the iperf traffic starts and when the USRP process begins. Default to 3 seconds
        self.usrp_run_delay = 3

        # The sample rate in 20MS/s
        self.usrp_sample_rate = '20'
        self.ursp_gain = '40'

        # Output/conversion file name. Set to "no_name" as default in case the
        # user has not yet given a file name to the run in the GUI
        self.test_name = "no_name"

        # Used to set the access category. '0' is voice, '1' is video, '2' is
        # best effort, '3' is background
        self.access_category = 0

        # State variable to determine whether or not to configure network routing
        self.configure_routing = True

        # Path of project directory for use in calls to scripts in utils/
        #self.working_dir = os.getcwd()
        self.working_dir = os.path.dirname(os.path.abspath(__file__))

        # The number of times that the process should be run for an average. Minimum 1
        self.num_runs = 1
        self.ping_max = 10

    # Make the timestamped data directory, and then return the full path for
    # writing data files to
    def make_data_dir(self):
        # Create the timestamp
        time = str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S"))
        time = time.replace(' ', '_')

        # Get the full path of the data file to be created
        dir_name = self.test_name + "_" + time + "/"
        location = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.abspath(os.path.join(location, "..",  "tests", dir_name))

        # Make the data file path if it doesn't exist (this should always run as long as the timestamp is present)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        print("Generated the test directory {0}.".format(full_path))

        return full_path

    # Runs a subprocess for the USRP based on the usrp_control_args variable. Future-proofing method
    # for when the option is added to run the USRP only
    def start_usrp(self):
        print("Running USRP...\n")

        if self.access_category == 1:
            self.access_category_name = "video"
        elif self.access_category == 2:
            self.access_category_name = "best_effort"
        elif self.access_category == 3:
            self.access_category_name = "background"
        else:
            self.access_category_name = "voice"

        # Create the data directory for the run
        self.data_dir = self.make_data_dir()
        print("The binary data file will be written to {0}.".format(self.data_dir))

        # Create the argument list to pass to the USRP subprocess that will be instantiated
        usrp_control_args = ["python", self.working_dir + "/writeIQ.py", self.get_iq_file_name(self.data_dir), str(self.run_time), self.center_frequency, self.usrp_gain]
        # Run the USRP process with the necessary arguments
        self.usrp_proc = subprocess.Popen(usrp_control_args)
        while self.usrp_proc.poll() is None:
            continue

        print("Done sensing medium\n")

    # Runs the USRP and iperf tools simultaneously
    def start_usrp_iperf(self):
        print("Running USRP with interference injected using iperf...")

        if self.essid is None or len(self.essid) == 0:
            print("ERROR: No network selected.")
            return

        if self.access_category == 1:
            self.access_category_name = "video"
            self.iperf_client_ac = "0x80"
        elif self.access_category == 2:
            self.access_category_name = "best_effort"
            self.iperf_client_ac = "0x00"
        elif self.access_category == 3:
            self.access_category_name = "background"
            self.iperf_client_ac = "0x20"
        else:
            self.access_category_name = "voice"
            self.iperf_client_ac = "0xC0"

        # Create the data directory for the run
        self.data_dir = self.make_data_dir()

        # Print the file path for debug purposes
        print("The test results will be written to {0}.".format(self.data_dir))

        if self.iperf_ap_addr == None:
            self.iperf_ap_addr = "192.168.1.1"
            print("No IP was entered for the iperf access point. IP has defaulted to 192.168.1.1\n")

        # Setup routing and get the ip addresses for client and server and their virtual
        if self.configure_routing == True:
            # real
            self.iperf_client_addr = str(ip_address(self.iperf_ap_addr) + 1)
            print("CLIENT IP ADDRESS is: " , self.iperf_client_addr)
            self.iperf_server_addr = str(ip_address(self.iperf_ap_addr) + 2)
            print("SERVER IP ADDRESS is: " , self.iperf_server_addr)
            # virtual
            self.iperf_virtual_client_addr = str(ip_address(self.iperf_client_addr) + (256))
            print("VIRTUAL CLIENT IP ADDRESS is: " , self.iperf_virtual_client_addr)
            self.iperf_virtual_server_addr = str(ip_address(self.iperf_server_addr) + (256))
            print("VIRTUAL SERVER IP ADDRESS is: " , self.iperf_virtual_server_addr)

            print("BRINGING",self.wlan_name,"DOWN")
            call(['ifconfig', self.wlan_name, 'down'])
            call(['ip', 'addr', 'flush', 'dev', self.wlan_name])

            print("BRINGING",self.eth_name,"UP")
            call(['ifconfig', self.eth_name, 'up'])
            call(['ip', 'addr', 'flush', 'dev', self.eth_name])

            print("ASSIGNING",self.eth_name,"TO IP:", self.iperf_client_addr)
            call(['ifconfig', self.eth_name, 'inet', self.iperf_client_addr, 'up'])
            time.sleep(10)

            network_connect(self.wlan_name, self.iperf_server_addr, self.essid, self.wlan_internal_name)
            setup_routing(self.eth_name, self.eth_mac, self.wlan_name, self.wlan_mac, self.iperf_client_addr, self.iperf_virtual_client_addr, self.iperf_server_addr, self.iperf_virtual_server_addr)

            ping_args = "ping -c 1 -I {0} {1}".format(self.eth_name, self.iperf_virtual_server_addr).split(" ")
            ping_count = 0
            print("WAITING FOR PING SUCCESS OF THE VIRTUAL SERVER THROUGH THE CLIENT INTERFACE")
            self.communication_success = 0
            while ping_count < self.ping_max:
                ping_process = subprocess.Popen(ping_args)
                ping_process.communicate()
                rc = ping_process.returncode
                if int(rc) == 0:
                    print("PING SUCCEEDED AFTER {0} RUNS".format(ping_count+1))
                    self.communication_success = 1
                    break
                ping_count = ping_count + 1
            if ping_count == self.ping_max:
                print("PING FAILED AFTER {0} ATTEMPTS".format(self.ping_max))
                self.communication_success = 0

        # The arguments to run the iperf client. If configure_routing is True, then automating routing has been performed and a virtual destination IP is required for the iperf client
        iperf_client_args = ["iperf", "-B", "{0}".format(str(self.iperf_client_addr)), "-c", "{0}".format(str(self.iperf_virtual_server_addr)), "-u", "-b", " {0}M".format(self.iperf_bw), "-t 10000000000000", "-i 1", "-S {0}".format(self.iperf_client_ac)]
        # The arguments to run the iperf server
        iperf_server_args = ["iperf", "-B", "{0}".format(str(self.iperf_server_addr)), "-s", "-u", "-t 1000000000000000", "-i 1"]
        iq_sample_files = []
        if self.communication_success:
            # Run the iperf commands and print debug information
            print("iperf server IP is {0}".format(self.iperf_server_addr))
            print("iperf client IP is {0}".format(self.iperf_client_addr))
            print("iperf client bandwidth is {0} Mbits/sec".format(self.iperf_bw))
            iperf_server_proc = color_subprocess.Popen(iperf_server_args, prefix='iperf_server:', color=color_subprocess.colors.fg.lightblue)
            iperf_client_proc = color_subprocess.Popen(iperf_client_args, prefix='iperf_client:', color=color_subprocess.colors.fg.lightcyan)

            for run in range(0, self.num_runs):
                time.sleep(self.usrp_run_delay)
                iq_file_name = self.get_iq_file_name(self.data_dir, run)
                # Set the arguments to be used to run the USRP
                usrp_control_args = ["python", self.working_dir + "/writeIQ.py", iq_file_name, str(self.run_time), self.center_frequency, self.usrp_gain]
                # Start the USRP
                self.usrp_proc = color_subprocess.Popen(usrp_control_args, prefix='USRP:        ', color=color_subprocess.colors.fg.lightgreen)
                # Continuously check to see if the USRP is running, then break out when it has stopped
                while True:
                    self.usrp_proc.getProcess().poll()
                    if self.usrp_proc.getProcess().returncode is not None:
                        iq_sample_files.append(iq_file_name)
                        break

            # Close the iperf processes as soon as the USRP is done sensing the medium
            iperf_server_proc.terminate()
            iperf_client_proc.terminate()

            print("Done sampling the medium. iperf processes killed.")
        
        return iq_sample_files

    def get_iq_file_name(self, data_dir, run):
        return os.path.join(data_dir, "iqsamples_" + self.access_category_name + "_run" + str(run) + ".bin")