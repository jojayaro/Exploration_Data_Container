#!/usr/bin/python3

import subprocess as cmd

cp = cmd.run("git -C /home/sidefxs/Documents/Exploration_Data_Container/ add .", check=True, shell=True)
cp = cmd.run("git -C /home/sidefxs/Documents/Exploration_Data_Container/ commit -m 'Update CSV with Daily Data'", check=True, shell=True)
cp = cmd.run("git -C /home/sidefxs/Documents/Exploration_Data_Container/ push -u origin master -f", check=True, shell=True)