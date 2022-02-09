#!/usr/bin/env python3
'''
Monitor current and voltage on a caen module

based on a code by Nick

2022-02-07

'''

import spur
import datetime
import time
import sys
import curses

OUTPUT_FILENAME = 'data.txt'

SSH_REMOTE_USERNAME = ''
SSH_REMOTE_PASSWORD = ''
SSH_REMOTE_ADDRESS = ''

code_map = {
    'up': 1,
    'down': 2,
    'ovc': 3,
    'ovv': 4,
    'unv': 5,
    'maxv': 6,
    'trip': 7,
    'ovp': 8,
    'ovt': 9,
    'dis': 10,
    'kill': 11,
    'ilk': 12,
    'nocal': 13,
}


def main(stdscr):
    stdscr.clear()
    stdscr.addstr('Opening SSH Tunnels')

    shell = spur.LocalShell()
    shell2 = spur.SshShell(hostname=SSH_REMOTE_ADDRESS, username=SSH_REMOTE_USERNAME,
                           password=SSH_REMOTE_PASSWORD, missing_host_key=spur.ssh.MissingHostKey.accept)

    # add header?
    # with open(plot_file, 'a') as f:
    #    f.write('# Date | Vmon | Imon \n')

    # HV = ''
    with shell:
        while True:
            time.sleep(2)
            shell.run(['screen', '-S', 'caenhv', '-X',
                       'hardcopy', '/run/user/1000/caen'])
            with shell.open('/run/user/1000/caen', 'r') as f:
                HV = f.readlines()

            Vmon = [f for f in HV[5].strip().split('  ') if f]
            Imon = [f for f in HV[6].strip().split('  ') if f]
            HVSt = [f for f in HV[9].strip().split('  ') if f]
            VSet = [f for f in HV[10].strip().split('  ') if f]
            HVFlag = ['Status', HV[7][16:26], HV[7]
                      [32:42], HV[7][48:58], HV[7][64:74]]
            HVFlag = [f.strip() for f in HVFlag]

            # hv = []
            stdscr.move(2, 0)
            stdscr.clrtobot()
            stdscr.addstr('Update time: {0}\n'.format(
                datetime.datetime.now()))
            for i in range(1, len(Vmon)):
                isOn = (HVSt[i].strip() == 'On')
                iOn = 1 if isOn else 0
                iStatus = 99
                # check the if it is on
                if not isOn:
                    continue
                if HVFlag[i] == '':
                    iStatus = 0
                if HVFlag[i].lower() in code_map:
                    iStatus = code_map[HVFlag[i].lower()]
                try:
                    vset = float(VSet[i].split()[0])
                    vmon = float(Vmon[i].split()[0])
                    imon = float(Imon[i].split()[0])

                    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

                    output_str = '{} {} {}'.format(now, vmon, imon)
                    with open(plot_file, 'a') as f:
                        f.write(output_str)

                    result = shell2.run(
                        ['sh', '-c', '''sh -c "echo '{}' >> {} " '''.format(output_str, OUTPUT_FILENAME)])

                except ValueError:
                    pass

        stdscr.refresh()
 curses.wrapper(main)
