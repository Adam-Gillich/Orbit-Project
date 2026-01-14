set datafile separator comma

set title "Acceleration [RSS]"
set xlabel "time [s]"
set ylabel "Acceleration [g]"

# lines
set arrow from 189, graph 0 to 189, graph 1 nohead lc 7 lw 2
set label "1st Stage separate" at 280, graph 0.95 center
set arrow from 305, graph 0 to 305, graph 0.92 nohead lc 4 lw 2
set label "Burnout" at 345, graph 0.9 center

set tmargin 2.1

plot "RSS_Kourou.csv" using 1:8 w l linecolor 22 lw 2 title "Acceleration"


#set terminal pngcairo size 800, 500
#set output "acc(RSS).png"
#replot
