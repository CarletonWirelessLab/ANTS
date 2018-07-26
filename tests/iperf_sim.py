import time

def iperf_sim(slp_time, ip_addr):
    print("Fake converter will now sleep for {0} seconds.\n".format(str(slp_time)))
    time.sleep(slp_time)
    print("Done\n")
    print("Would have connected to {0}\n".format(ip_addr))

    return

if __name__ == '__main__':
    iperf_sim(float(sys.argv[1]))
