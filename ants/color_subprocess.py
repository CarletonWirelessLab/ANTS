import sys
import os
import subprocess
import time
import threading

class Popen(object):
    """
        Starts the subprocess with colorful output

        Arguments:
            command: The command

            prefix: The prefix to print before every line

            color: The color escape code
    """
    class PrefixStdoutPipe(threading.Thread):
        def __init__(self, prefix, color = ''):
            self._color = color
            self._prefix = prefix
            self._readpipe, self._writepipe = os.pipe()
            super().__init__()

        def fileno(self):
            self.start()
            return self._writepipe

        def finished(self):
            os.close(self._writepipe)

        def run(self):
            inputFile = os.fdopen(self._readpipe)

            while True:
                line = inputFile.readline()
                if len(line) == 0:
                    break
                    
                print(self._color, self._prefix, line.strip(), colors.reset, sep='')

    def __init__(self, command, prefix = '', color = ''):
        self._process = subprocess.Popen(command, stdout=PrefixStdoutPipe(prefix, color), stderr=PrefixStdoutPipe(prefix, colors.fg.red))

    def getProcess(self):
        return self._process

    def terminate(self):
        self._process.terminate()

class colors: 
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg: 
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'


    
    
    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive()

if __name__ == '__main__':
    command = "ping www.heise.de -c 5".split(" ")
    ping_process = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout_reader = PrefixStdoutPipe(process.stdout, "ping: ", colors.fg.red)
    stdout_reader.start()

    print("Hello, world!")
    time.sleep(5)
    print("End")

    # Let's be tidy and join the threads we've started.
    stdout_reader.join()

    # Close subprocess' file descriptors.
    ping_process.stdout.close()
    ping_process.terminate()
