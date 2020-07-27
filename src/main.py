import os
import sys

# Check for root permissions
euid = os.geteuid()
if euid != 0:
    print("Script not started as root. Running sudo..")
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    # the next line replaces the currently-running process with the sudo
    os.execlpe('sudo', *args)  # Does not work in pycharm console


CORE_COUNT = os.cpu_count()
# Each core file is located in /sys/devices/system/cpu/cpu"X"/cpufreq/scaling_governor, where X is the core number
CORE_FILE1 = "/sys/devices/system/cpu/cpu"
CORE_FILE2 = "/cpufreq/scaling_governor"


def get_governor():
    cpuGovs = []
    # Get current governor for all cores
    for i in range(CORE_COUNT):
        coreNumber = str(i)
        coreFile = "".join((CORE_FILE1, coreNumber, CORE_FILE2))
        fileGov = open(coreFile, "r")
        getGov = fileGov.read()
        cpuGovs.append(getGov)

    # See if any of the cores have a different governor
    mainGov = cpuGovs[1]
    for i in range(1, CORE_COUNT):
        if cpuGovs[i] != mainGov:
            mainGov = "different"

    return mainGov


def set_governor(profile):
    # Find the file that contains the governor for each cpu core and write to it the requested governor
    for i in range(CORE_COUNT):
        coreNumber = str(i)
        coreFile = "".join((CORE_FILE1, coreNumber, CORE_FILE2))
        with open(coreFile, "w") as file:
            if profile == 1:
                file.write("performance")

            elif profile == 2:
                file.write("ondemand")

            elif profile == 3:
                file.write("powersave")


def display():
    mainGov = get_governor()
    print("Current governor: ", mainGov)


def main():
    profile = int(input())
    if profile == 0:
        return 1
    set_governor(profile)
    display()


print("1-set to performance \n2-set to ondemand \n3-set to powersave\n0-exit \n")
status = 0
while status != 1:
    status = main()
