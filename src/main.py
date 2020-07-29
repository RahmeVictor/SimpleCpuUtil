import os
import sys

import psutil


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
CONFIG_FILE = "/home/" + os.getenv('SUDO_USER') + "/.config/SimpleCpuUtil/config.ini"


def get_settings():
    """
    Gets and applies settings.
    """
    watchedPrograms = {}
    with open(CONFIG_FILE, "r") as config:
        setting = config.readline().strip()  # Read each line and strip it of \n and trailing white space
        programSetting = setting.partition(" = ")
        watchedPrograms[programSetting[0]] = programSetting[2]  # Put the program in a dictionary {program : profile}
        print(watchedPrograms)

    return watchedPrograms


def check_process_status(processName):
    """
    Check if there is any running process that contains the given name processName.
    """
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


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
            if profile == "performance":
                file.write("performance")

            elif profile == "ondemand":
                file.write("ondemand")

            elif profile == "powersave":
                file.write("powersave")

            else:
                print("Profile not found")
                return


def display():
    mainGov = get_governor()
    print("Current governor: ", mainGov)


def main():
    print("Type what profile do you want to set or 0 to exit.")
    # Set a profile based on running programs.
    watchedPrograms = get_settings()
    for program in watchedPrograms:
        if check_process_status(program):
            pass

    while True:
        display()
        profile = input()
        if profile == "0":
            return
        set_governor(profile)


main()
