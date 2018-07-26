import time
import sys

def iperf_sim(slp_time, ip_addr):
    print("Fake iperf will now sleep for {0} seconds.\n".format(str(slp_time)))
    time.sleep(float(slp_time))
    print("Done iperf sim\n")
    print("Would have connected to {0}\n".format(ip_addr))

    return

if __name__ == '__main__':
    iperf_sim(sys.argv[1], sys.argv[2])
