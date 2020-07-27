import os
import sys

# Check for root permissions
euid = os.geteuid()
if euid != 0:
    print("Script not started as root. Running sudo..")
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    # the next line replaces the currently-running process with the sudo
    os.execlpe('sudo', *args)  # Does not work in pycharm console


def main():
    coreFile1 = "/sys/devices/system/cpu/cpu"
    coreFile2 = "/cpufreq/scaling_governor"
    cpuCount = os.cpu_count()
    print(cpuCount)
    # Get current governor for all cores
    for i in range(cpuCount):
        coreNumber = str(i)
        coreFile = "".join((coreFile1, coreNumber, coreFile2))
        fileGov = open(coreFile, "r")
        getGov = fileGov.read()
        print(i, ": ", getGov)

    profile = int(input("1-set to performance \n2-set to ondemand \n3-set to powersave\n0-exit \n"))
    if profile == 0:
        return 0

    for i in range(cpuCount):
        coreNumber = str(i)
        coreFile = "".join((coreFile1, coreNumber, coreFile2))
        with open(coreFile, "w") as file:
            if profile == 1:
                file.write("performance")

            elif profile == 2:
                file.write("ondemand")

            elif profile == 3:
                file.write("powersave")


main()
