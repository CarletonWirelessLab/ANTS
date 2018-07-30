import time
import sys

def converter_sim(slp_time):
    print("Fake converter will now sleep for {0} seconds.\n".format(str(slp_time)))
    time.sleep(slp_time)
    print("Done conversion sim\n")

    return

if __name__ == '__main__':
    converter_sim(float(sys.argv[1]))
