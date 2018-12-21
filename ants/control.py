#!/usr/bin/python3

import sys
import subprocess
import threading
import time
import queue
import os
import datetime

# try:
#     import matlab.engine
# except ImportError:
#     print("MATLAB engine could not be found. Converter and plotter tools may not function properly. See README.md for details on how to install this component.\n")
#     matlab_available = False
# else:
#     matlab_available = True

class ANTS_Controller():

    def __init__(self):

        # Class variables used for the subprocesses run, if any, of the tools
        # run when their checkboxes are selected
        self.usrp_proc = None
        self.controller_proc = None
        self.converter_proc = None
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

        # The arguments to give to subprocess.Popen() to run iperf
        self.iperf_client_args = ["iperf", "-c", str(self.iperf_client_addr), "-u", "-b"+str(self.iperf_rate)+"M", "-S", str(self.iperf_mem_addr), "-t10000000000"]
        self.iperf_server_args = ["iperf", "-s", "-u", "-t100000000000000"]

        # Default run time length
        self.run_time = 0.5

        # Output/conversion file name
        self.file_name = ""

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
        self.sim_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'tests'))
        self.sim_dir = self.sim_dir + '/'

        # Create and/or get the
        self.data_dir = self.make_data_dir()

        # if matlab_available == True:
        #     print("Starting Matlab engine for Python... ")
        #     self.engine = matlab.engine.start_matlab()
        #     print("Done\n")
        #
        #     print("Pre-cleaning workspace...")
        #     self.engine.close('all', nargout=0)
        #     self.engine.clear('all', nargout=0)
        #     print("Done\n")
        #     print("Setting up Matlab engine workspace...")
        #     cur_dir = os.getcwd()
        #     self.engine.addpath(self.engine.genpath(cur_dir))
        #     print("Done\n")
        # else:
        #     print("Skipping MATLAB engine setup...\n")

    # def start_matlab(self):
    #
    #     if matlab_available == True:
    #         print("Starting Matlab engine for Python... ")
    #         self.engine = matlab.engine.start_matlab()
    #         print("Done\n")
    #
    #         print("Pre-cleaning workspace...")
    #         self.engine.close('all', nargout=0)
    #         self.engine.clear('all', nargout=0)
    #         print("Done\n")
    #         print("Setting up Matlab engine workspace...")
    #         cur_dir = os.getcwd()
    #         self.engine.addpath(self.engine.genpath(cur_dir))
    #         print("Done\n")
    #     else:
    #         print("Skipping MATLAB engine setup...\n")


    # Make the timestamped data directory, and then return the full path for
    # writing data files to
    def make_data_dir(self):
        time = str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S"))
        time = time.replace(' ', '_')
        dir_name = self.file_name + "_" + time + "/"
        location = os.path.dirname(os.path.abspath(__file__))
        full_path = location + "../tests/" + dir_name

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        return full_path

    # Runs a subprocess for the USRP based on the usrp_control_args variable

    def start_usrp(self, sim_mode):
        print("Running USRP...\n")

        if sim_mode == True:
            self.usrp_control_args = ["python3", self.sim_dir + "usrp_sim.py", str(self.run_time)]
        else:
            self.usrp_control_args = ["python", self.utils_dir + "writeIQ.py", self.file_name, str(self.run_time)]

        self.usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        while self.usrp_proc.poll() is None:
            continue
        print("Done sensing medium\n")

        return

    # Runs a subprocess for the SGControl tool based on the sg_controller_args
    # variable
    def start_controller(self, sim_mode):
        print("Running interference...\n")

        if sim_mode == True:
            self.sg_controller_args = ["python3", self.sim_dir + "sg_sim.py", str(self.run_time)]
        else:
            self.sg_controller_args = ["python3", self.utils_dir + "const_control.py", str(self.run_time)]

        self.controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        while self.controller_proc.poll() is None:
            continue
        print("Done injecting interference\n")

        return

    # Runs the USRP and SGControl tools simultaneously if and only if both boxes
    # are checked
    def start_usrp_controller(self, sim_mode):
        print("Running USRP with interference injected...\n")

        if sim_mode == True:
            self.usrp_control_args = ["python3", self.sim_dir + "usrp_sim.py", str(self.run_time)]
            self.sg_controller_args = ["python3", self.sim_dir + "sg_sim.py", str(self.run_time)]
        else:
            self.usrp_control_args = ["python", self.utils_dir + "writeIQ.py", self.file_name, str(self.run_time)]
            self.sg_controller_args = ["python3", self.utils_dir + "const_control.py", str(self.run_time)]

        self.usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        self.controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        while True:

            self.usrp_proc.poll()
            self.controller_proc.poll()
            # Make sure the sequence won't continue until both tools have
            # finished
            if self.usrp_proc.returncode is not None and self.controller_proc.returncode is not None:
                break

        print("Done sensing with added interference\n")
        return

    # Runs the USRP and iperf tools simultaneously if and only if both boxes
    # are checked
    def start_usrp_iperf_server(self, sim_mode):
        print("Running USRP with interference injected...\n")

        if sim_mode == True:
            self.usrp_control_args = ["python3", self.sim_dir + "usrp_sim.py", str(self.run_time)]
            self.iperf_client_args = ["python3", self.sim_dir + "iperf_sim.py", str(self.run_time), str(self.iperf_client_addr)]
            self.iperf_server_args = ["python3", self.sim_dir + "iperf_sim.py", str(self.run_time), str(self.iperf_server_addr)]
        else:
            self.usrp_control_args = ["python", self.utils_dir + "writeIQ.py", self.file_name, str(self.run_time)]

        # Only run with the client option if something is provided. If not, the iperf client will be run elsewhere
        if self.iperf_client_addr:
            #self.iperf_client_proc = subprocess.Popen(self.iperf_client_args, stdin=subprocess.PIPE, stderr=None, shell=False)
            pass

        # Always run the iperf server
        self.iperf_server_proc = subprocess.Popen(self.iperf_server_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        self.usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        if sim_mode == False:
            while True:

                self.usrp_proc.poll()
                # Make sure the sequence won't continue until all tools have
                # finished
                if self.usrp_proc.returncode is not None:
                    break

        self.iperf_server_proc.kill()

        print("Done sensing with iperf\n")
        return

    def start_converter(self, sim_mode):
        print("Running converter tool on {0}...".format(self.file_name))
        if sim_mode == True:
            self.matlab_converter_args = ["python3", self.sim_dir + "converter_sim.py", str(8)]
            self.converter_proc = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stderr=None, shell=False)
            self.converter_proc.wait()
        else:
            if matlab_available == True:
                self.engine.workspace['fileName'] = self.file_name + ".bin"
                self.engine.workspace['duration'] = self.run_time
                self.engine.workspace['accessCategory'] = self.access_category
                self.engine.findIFS_only(nargout=0)
                print("Done conversion\n")
            else:
                print("Nothing converted. Is the MATLAB engine installed?")

    def start_plotter(self, sim_mode):
        print("Running plotter...")
        if sim_mode == True:
            self.matlab_plotter_args = ["python3", self.sim_dir + "plotter_sim.py", str(10)]
            self.plotter_proc = subprocess.Popen(self.matlab_plotter_args, stdin=subprocess.PIPE, stderr=None, shell=False)
            self.plotter_proc.wait()
        else:
            if matlab_available == True:
                self.engine.Load_and_Eval_IFSOnly(nargout=0)
                print("Done plotting\n")
            else:
                print("Nothing plotted. Is the MATLAB engine installed?")

    # Runs the iperf client and server processes
    def start_iperf_server(self, sim_mode):
        print("Running iperf...\n")

        if sim_mode == True:
            self.iperf_client_args = ["python3", self.sim_dir + "iperf_sim.py", str(self.run_time), str(self.iperf_client_addr)]
            self.iperf_server_args = ["python3", self.sim_dir + "iperf_sim.py", str(self.run_time), str(self.iperf_server_addr)]

        #iperf arguments for real mode are currently defined earlier in this module
        #self.iperf_client_proc = subprocess.Popen(self.iperf_client_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        self.iperf_server_proc = subprocess.Popen(self.iperf_server_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        while True:

            #self.iperf_client_proc.poll()
            self.iperf_server_proc.poll()
            # Make sure the sequence won't continue until both tools have
            # finished. Is it necessary that we wait for the server, or is the
            # time given to it just to ensure that we had time to run the client
            # manually?
            if self.iperf_server_proc.returncode is not None:
                break

        print("Done running iperf\n")
        return
