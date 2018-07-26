import time

def usrp_sim(slp_time):
    print("Simulating USRP set up time...\n")
    time.sleep(1.9)
    print("Done\n")
    print("Fake USRP will now sleep for {0} seconds.\n".format(str(slp_time)))
    time.sleep(slp_time)
    print("Done\n")

    return

if __name__ == '__main__':
    usrp_sim(float(sys.argv[1]))
