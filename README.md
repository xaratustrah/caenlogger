# CAEN module logger

This is a simple CAEN module logger.

## Install

Download the code. Go to the project directory and run:

```
pip3 install --no-build-isolation .
```

## Usage
Please first fill out the config file `caenlogger_config.toml` according to the local needs. This has to be provided in the command line.

```
caenlogger --config caenlogger_config.toml
```

## Uninstall

```
pip3 uninstall -y caenlogger
```

## View results

You can have a live view of the result file using [gnuplot](http://www.gnuplot.info/).


```
set term x11 noraise font "Sans, 25"
set data time
set timefmt "%Y%m%d-%H%M%S"
set grid
set title "CAEN logger"
set title font "Helvetica, 14"
set ylabel "Voltage [V]"
set xlabel "Time"

plot "caen_current.dat" using 1:3 title "I1" with lines lw 2, \
     "caen current.dat" using 1:5 title "I2" with lines lw 2, \
     "caen_current.dat" using 1:7 title "I3" with lines lw 2, \
     "caen_current.dat" using 1:9 title "I4" with lines lw 2

pause 1
reread
```
