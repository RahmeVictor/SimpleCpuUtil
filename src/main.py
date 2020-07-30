import os
import sys
import time

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


def set_governor_based_on_programs(originalGovernor: str, currentGovernor: str, watchedPrograms: dict):
    """
    Set a governor based on running programs, order matters
    """
    for program in watchedPrograms:
        if check_process_status(program):
            if watchedPrograms[program] != currentGovernor:
                currentGovernor = set_governor(watchedPrograms[program])

            break

    else:
        if originalGovernor != currentGovernor:
            # If no programs were found, return to the original program
            currentGovernor = set_governor(originalGovernor)
            print("No programs found.\r")

    return currentGovernor


def apply_arguments():
    """
    Gets and applies arguments. True if it found arguments, false otherwise
    """
    if len(sys.argv) == 3:
        if sys.argv[1] == "-setgov":
            display()
            set_governor(sys.argv[2])
            print("Set governor to: ", sys.argv[2])
            return True

        else:
            print("Commands: -setgov <governor>")
            sys.exit()

    else:
        return False


def get_settings():
    """
    Gets and applies settings.
    """
    watchedPrograms = {}
    with open(CONFIG_FILE, "r") as config:
        setting = config.readline().strip()  # Read each line and strip it of \n and trailing white space
        programSetting = setting.partition(" = ")
        watchedPrograms[programSetting[0]] = programSetting[2]  # Put the program in a dictionary {program : governor}

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
        getGov = (fileGov.read()).strip('\n')
        cpuGovs.append(getGov)

    # See if any of the cores have a different governor
    mainGov = cpuGovs[1]
    for i in range(1, CORE_COUNT):
        if cpuGovs[i] != mainGov:
            mainGov = "different"

    return mainGov


def set_governor(governor: str):
    # Find the file that contains the governor for each cpu core and write to it the requested governor(governor)
    for i in range(CORE_COUNT):
        coreNumber = str(i)
        coreFile = "".join((CORE_FILE1, coreNumber, CORE_FILE2))
        with open(coreFile, "w") as file:
            if governor == "performance":
                file.write("performance")

            elif governor == "ondemand":
                file.write("ondemand")

            elif governor == "powersave":
                file.write("powersave")

            else:
                print("Profile not found")
                return get_governor()

    return governor


def display():
    mainGov = get_governor()
    print("Current governor: " + str(mainGov))


def main():
    originalGovernor = get_governor()
    currentGovernor = originalGovernor
    if not apply_arguments():
        watchedPrograms = get_settings()
        while True:
            display()
            currentGovernor = set_governor_based_on_programs(originalGovernor, currentGovernor, watchedPrograms)
            time.sleep(5)


main()
