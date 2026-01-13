set datafile separator comma

set title "Pitch over time [KSP]"
set xlabel "time [s]"
set ylabel "Pitch [deg]"

# lines
set arrow from 98, graph 0 to 98, graph 1 nohead lc 7 lw 2
set label "1st Stage separate" at 185, graph 0.95 center
set arrow from 167, graph 0 to 167, graph 0.92 nohead lc 4 lw 2
set label "Burnout" at 205, graph 0.9 center

set tmargin 2.1

plot "KSP.csv" using 1:14 w l linecolor 3 lw 2 title "Pitch"


#set terminal pngcairo size 800, 500
#set output "pitch(KSP).png"
#replot