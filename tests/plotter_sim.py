import time
import sys

def plotter_sim(slp_time):
    print("Fake plotter will now sleep for {0} seconds.\n".format(str(slp_time)))
    time.sleep(slp_time)
    print("Done plotting sim\n")

    return

if __name__ == '__main__':
    plotter_sim(float(sys.argv[1]))
