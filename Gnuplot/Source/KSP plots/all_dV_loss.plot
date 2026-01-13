set datafile separator comma

set yrange [0:700]

set title "All types of DeltaV loss [KSP]"
set xlabel "time [s]"
set ylabel "DeltaV [m/s]"

# lines
set arrow from 98, graph 0 to 98, graph 1 nohead lc 7 lw 2
set label "1st Stage separate" at 185, graph 0.95 center
set arrow from 167, graph 0 to 167, graph 0.92 nohead lc 4 lw 2
set label "Burnout" at 205, graph 0.9 center

set tmargin 2.1

plot "KSP.csv" using 1:15 w l linecolor 2 lw 2 title "dV Grav", \
"KSP.csv" using 1:17 w l linecolor 1 lw 2 title "dV Steer",\
"KSP.csv" using 1:16 w l linecolor 6 lw 2 title "dV Drag"


#set terminal pngcairo size 800, 500
#set output "all_dV_loss(KSP).png"
#replot
