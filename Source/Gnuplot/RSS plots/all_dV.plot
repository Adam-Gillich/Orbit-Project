set datafile separator comma

set xrange [0:1100]
set yrange [0:9800]

set title "All types of DeltaV [RSS]"
set xlabel "time [s]"
set ylabel "DeltaV [m/s]"

# lines
set arrow from 189, graph 0 to 189, graph 1 nohead lc 7 lw 2
set label "1st Stage separate" at 300, graph 0.95 center
set arrow from 305, graph 0 to 305, graph 0.92 nohead lc 4 lw 2
set label "Burnout" at 360, graph 0.9 center

set tmargin 2.1

plot "RSS_Kourou.csv" using 1:18 w l linecolor 3 lw 2 title "Total dV", \
"RSS_Kourou.csv" using 1:15 w l linecolor 2 lw 2 title "dV Grav", \
"RSS_Kourou.csv" using 1:17 w l linecolor 1 lw 2 title "dV Steer",\
"RSS_Kourou.csv" using 1:16 w l linecolor 6 lw 2 title "dV Drag"


#set terminal pngcairo size 800, 500
#set output "all_dV(RSS).png"
#replot