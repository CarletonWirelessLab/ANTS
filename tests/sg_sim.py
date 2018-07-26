import time
import sys

def sg_sim(slp_time):
    print("Fake signal generator will now sleep for {0} seconds.\n".format(str(slp_time)))
    time.sleep(slp_time)
    print("Done signal generator sim\n")

    return

if __name__ == '__main__':
    sg_sim(float(sys.argv[1]))
