set datafile separator comma

set xrange [0:500]

set title "Pressure over time [RSS]"
set xlabel "time [s]"
set ylabel "Dynamic pressure [Pa]"

# lines
set arrow from 189, graph 0 to 189, graph 1 nohead lc 7 lw 2
set label "1st Stage separate" at 240, graph 0.95 center
set arrow from 305, graph 0 to 305, graph 0.92 nohead lc 4 lw 2
set label "Burnout" at 335, graph 0.9 center

set tmargin 2.1

plot "RSS_Kourou.csv" using 1:9 w l linecolor 9 lw 2 title "Pressure"


#set terminal pngcairo size 800, 500
#set output "max_q(RSS).png"
#replot