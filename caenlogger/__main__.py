#!/usr/bin/env python3
"""
Monitor current and voltage on a caen module

based on a code by Nick

2022-02-07
Update: 2024-02-08
"""

import spur
import sshtunnel
import datetime
import time
import sys
import curses
from loguru import logger
import toml
import argparse

HV = ""

code_map = {
    "up": 1,
    "down": 2,
    "ovc": 3,
    "ovv": 4,
    "unv": 5,
    "maxv": 6,
    "trip": 7,
    "ovp": 8,
    "ovt": 9,
    "dis": 10,
    "kill": 11,
    "ilk": 12,
    "nocal": 13,
}


def process(stdscr, config_dic):

    logger.info("Screen is connected. Press ctrl-C to abort.")
    stdscr.clear()
    stdscr.addstr("Opening SSH Tunnels")
    username, pw, local_adr, remote_adr, plot_file = (
        config_dic["username"],
        config_dic["pw"],
        config_dic["local_adr"],
        config_dic["remote_adr"],
        config_dic["plot_file"],
    )

    with sshtunnel.open_tunnel(
        (remote_adr, 22),
        ssh_username=username,
        ssh_password=pw,
        remote_bind_address=(local_adr, 22),
    ) as tunnel:

        shell = spur.LocalShell()
        shell2 = spur.SshShell(
            hostname=remote_adr,
            username=username,
            password=pw,
            missing_host_key=spur.ssh.MissingHostKey.accept,
        )

        with shell:
            while True:
                time.sleep(2)
                shell.run(
                    ["screen", "-S", "caenhv", "-X", "hardcopy", "/run/user/1000/caen"]
                )
                with shell.open("/run/user/1000/caen", "r") as f:
                    HV = f.readlines()

                Vmon = [f for f in HV[5].strip().split("  ") if f]
                Imon = [f for f in HV[6].strip().split("  ") if f]
                HVSt = [f for f in HV[9].strip().split("  ") if f]
                VSet = [f for f in HV[10].strip().split("  ") if f]
                HVFlag = [
                    "Status",
                    HV[7][16:26],
                    HV[7][32:42],
                    HV[7][48:58],
                    HV[7][64:74],
                ]
                HVFlag = [f.strip() for f in HVFlag]

                hv = []
                stdscr.move(2, 0)
                stdscr.clrtobot()
                stdscr.addstr("Update time: {0}\n".format(datetime.datetime.now()))
                output_str = ""
                for i in range(1, len(Vmon)):
                    isOn = HVSt[i].strip() == "On"
                    iOn = 1 if isOn else 0
                    iStatus = 99
                    # check the if it is on

                    if not isOn:
                        continue

                    if HVFlag[i] == "":
                        iStatus = 0

                    if HVFlag[i].lower() in code_map:
                        iStatus = code_map[HVFlag[i].lower()]

                    try:
                        vset = float(VSet[i].split()[0])
                        vmon = float(Vmon[i].split()[0])
                        imon = float(Imon[i].split()[0])
                        output_str += f"{vmon} {imon} "

                    except ValueError:
                        pass

                now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                output_str = now + " " + output_str
                with open(plot_file, "a") as f:
                    f.write(output_str)

                result = shell2.run(
                    [
                        "sh",
                        "-c",
                        """sh -c "echo '{}' >> {} " """.format(output_str, plot_file),
                    ]
                )

            stdscr.refresh()


# -------


def main():
    parser = argparse.ArgumentParser(prog="caenlogger")
    parser.add_argument(
        "-c",
        "--config",
        nargs=1,
        type=str,
        default=None,
        help="The name of the config file.",
    )

    logger.remove(0)
    logger.add(sys.stdout, level="INFO")

    args = parser.parse_args()
    config_dic = None

    if args.config:
        logger.info("Config file provided.")
        try:
            # load config file
            with open(args.config[0], "r") as f:
                config_dic = toml.load(f)

            for key in ["username", "pw", "local_adr", "remote_adr", "plot_file"]:
                assert key in config_dic.keys()

        except:
            logger.error("Config file does not have required format.")
            exit()

    else:
        logger.error("Please provide a config file.")
        exit()

    try:
        # parameters for the function has to be given to wrapper as args
        curses.wrapper(process, config_dic)

    except (EOFError, KeyboardInterrupt):
        logger.success("User cancelled. Aborting...")
        exit()


# -------

if __name__ == "__main__":
    main()
