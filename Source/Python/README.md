# Trajectory calculation, python

## Introduction

There are three files uploaded, "DeltaV_calculations.py" is the program, the .yaml file is the config file, and the test.py variant is jusst a test program for the "find_max_not_NaN" fuction.

If you are looking for the results look into the "Results" folder.

## Diagrams

### Algorithms, sequence

This is a more robust and complicated description of the calculations.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 
  'noteBkgColor':'#ffcccc',
  'noteTextColor':'#000000',
  'noteBorderColor':'#ff0000',
  'labelBoxBkgColor':'#add8e6',
  'labelBoxBorderColor':'#4682b4',
  'loopTextColor':'#000000'
}}}%%
sequenceDiagram
    participant Main as main()
    participant FMNN as find_max_not_NaN
    participant MinScalar as minimize_scalar
    participant CalcTDV as calc_TotalDeltaV
    participant FB as find_bracket
    participant Brent as brentq
    participant Core as core_calculations
    participant Helpers as Helper Functions
    
    Main->>Main: Set name = "Earth"
    Main->>FMNN: Find valid M_percent upper bound (1, 99)
    Note over FMNN: Numerical method, recursive ~bisect
    FMNN->>CalcTDV: Test function at midpoints
    CalcTDV->>Core: Call with test M_percent
    Core-->>CalcTDV: Return TotalDeltaV
    CalcTDV-->>FMNN: Return result
    FMNN-->>Main: Return M_per_max
    
    Main->>MinScalar: Minimize calc_TotalDeltaV (1, M_per_max)
    Note over MinScalar: Numerical method, minimum
    
    loop For each M_percent trial
        MinScalar->>CalcTDV: Call with M_percent
        
        Note over CalcTDV,FB: Find optimal gamma
        CalcTDV->>FB: Search gamma bracket (gmin, gmax)
        loop Sample gamma values
            FB->>Core: Call with M_percent, gamma_i
            Core->>Helpers: config_open(name)
            Helpers-->>Core: Return config parameters
            Core->>Helpers: Calculate M2_f, tb_2, U1, U2
            Core->>Helpers: Calculate DeltaV1, DeltaV2
            Core->>Helpers: Calculate z2f, n1_, n2_
            Helpers-->>Core: Return parameters
            
            Note over Core,FB: Find z20 root
            Core->>FB: Search z20 bracket (zmin, zmax)
            loop Sample z20 values
                FB->>Helpers: Evaluate root_z20(z)
                Helpers-->>FB: Return f value
            end
            FB-->>Core: Return z20 bracket
            
            Core->>Brent: Solve root_z20 with bracket
            Note over Brent: Numerical method, Brent
            loop Brentq iterations (max 5000)
                Brent->>Helpers: Evaluate root_z20(z)
                Helpers-->>Brent: Return f value
            end
            Brent-->>Core: Return z20
            
            Core->>Helpers: Recompute A1, A2
            Core->>Helpers: Calculate V_at_z20, V_at_z2f
            Core->>Helpers: Calculate h_at_z20, h_at_z2f
            Core->>Helpers: Calculate L, E, e, r_Ap, r_Pe
            Core->>Helpers: Calculate DeltaV_c via vis_viva
            Helpers-->>Core: Return values
            
            Core->>Core: Print detailed results
            Core-->>FB: Return f_Ap
        end
        FB-->>CalcTDV: Return gamma bracket
        
        CalcTDV->>Brent: Solve root_gamma with bracket
        Note over Brent: Numerical method, Brent
        loop Brentq iterations (max 1000)
            Brent->>Core: Call with M_percent, gamma_i
            Core-->>Brent: Return f_Ap
        end
        Brent-->>CalcTDV: Return optimal gamma
        
        CalcTDV->>Core: Final call with optimal gamma
        Core-->>CalcTDV: Return f_Ap, TotalDeltaV
        CalcTDV-->>MinScalar: Return TotalDeltaV
    end
    
    MinScalar-->>Main: Return optimal result
```