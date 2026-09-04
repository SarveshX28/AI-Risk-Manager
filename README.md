Markdown


# Physics Simulation Suite & R&D Framework for Sustained Levitation

A multi-pathway physics simulation workbench, analytical parameter engine, and empirical verification suite for reactionless lift and contactless levitation. 

This repository translates theoretical and apparent "antigravity" concepts into rigorous, empirically verifiable engineering domains:
1. **Electrohydrodynamic (EHD) Ion Propulsion** (Atmospheric momentum exchange)
2. **High-Temperature Superconducting (HTS) Levitation** (Frozen-image flux-pinning)
3. **Acoustic Trapping & Gor'kov Potential** (Ultrasonic standing wave radiation force)
4. **Breakthrough Gravitational Physics Metrology** (Casimir stress tensors, Gertsenshtein EM-to-GW coupling, and antimatter weak equivalence bounds)

---

## Repository Structure

```text
nage/
│
├── web/
│   └── index.html                     # Interactive client-side simulation dashboard
│
├── python/
│   ├── ehd_thruster_model.py          # Peek's law, Townsend current, and EHD thrust
│   ├── hts_magnetic_levitation.py     # Halbach dipole & frozen-image suspension model
│   ├── acoustic_trapping_gorkov.py    # 40 kHz standing wave & Gor'kov trapping limits
│   └── breakthrough_physics_limits.py # Casimir stress, Gertsenshtein conversion & ALPHA-g bounds
│
├── docs/
│   └── TECHNICAL_SPECIFICATION.md     # Derivations, constants, and boundary conditions
│
├── requirements.txt                   # Minimal Python scientific dependencies
└── README.md                          # Project documentation and guide
Key Features & Physics Models
1. Electrohydrodynamic (EHD) Thrust Engine
Peek's Law Formulation: Computes corona onset threshold V 
0
​
  as a function of wire radius r 
0
​
 , inter-electrode gap d, and air density factor δ.

Townsend Drift Current: Models unipolar ion current density I∝V(V−V 
0
​
 ).

Electrostatic Momentum Transfer: Evaluates net aerodynamic lift force F= 
μ
I⋅d
​
  using ion mobility μ≈2.0×10 
−4
  m 
2
 /(V⋅s).

2. Superconducting HTS Magnetic Levitation
Frozen-Image Approximation (Kordyuk Model): Computes passive, self-stabilizing suspension forces between a high-grade NdFeB field and a Type-II superconductor (e.g., YBCO).

Flux-Pinning Stiffness: Evaluates vertical restore stiffness k 
z
​
 =− 
dh
dF 
z
​
 
​
  and payload equilibrium up to 50 kg scale prototypes.

3. Ultrasonic Acoustic Trapping
Acoustic Radiation Force: Evaluates primary forces acting on incompressible particles (r≪λ) at 40 kHz ultrasound.

Gor'kov Potential Wells: Solves pressure nodes and calculates the maximum suspended material density (kg/m 
3
 ) versus acoustic sound pressure level (SPL).

4. Track B: Breakthrough Gravitational Physics Metrology
Casimir Energy Density: Computes vacuum boundary stress T 
μν
​
  and attractive pressure at nanometer scale separations:

ρ 
Casimir
​
 =− 
720d 
4
 
π 
2
 ℏc
​
 
Gertsenshtein Effect: Calculates the probability of resonant conversion from coherent electromagnetic waves into high-frequency gravitational waves inside high static magnetic fields:

P(γ→g)≈ 
c 
4
 
4πG
​
 B 
2
 L 
2
 
Weak Equivalence Principle (Antimatter): Benchmarks local free-fall ratios against CERN ALPHA-g (2023) experimental limits (g 
H
ˉ
 
​
 /g 
H
​
 ≈0.75±0.13).

Getting Started
Prerequisites
Python 3.9+

A modern web browser (Chrome, Edge, Firefox, Safari)

Installation
Clone or navigate to the workspace directory:

Bash


cd "c:\Users\shreyash nage\OneDrive\Desktop\nage"
Install Python dependencies:

Bash


pip install -r requirements.txt
(If requirements.txt is not yet created, run pip install numpy scipy matplotlib)

Running the Components
1. Interactive Web Workbench
Open the standalone web dashboard directly in any browser:

Double-click web/index.html, or

Run a local lightweight HTTP server:

Bash


python -m http.server 8000 --directory web
Navigate to http://localhost:8000 to interact with real-time sliders for voltage, gap distance, magnetic flux cooling height, and acoustic SPL.

2. Python Analytical Suite
Execute any reference model from the terminal:

Evaluate EHD thruster performance:

Bash


python python/ehd_thruster_model.py
Simulate HTS levitation forces and maximum payload:

Bash


python python/hts_magnetic_levitation.py
Calculate acoustic standing-wave trapping limits:

Bash


python python/acoustic_trapping_gorkov.py
Evaluate boundary conditions for breakthrough physics:

Bash


python python/breakthrough_physics_limits.py
Verification & Validation
Module	Boundary / Baseline Metric	Expected Analytical Result
EHD Inception	Wire r=0.1 mm, Gap d=4 cm	V 
0
​
 ≈11.5−13.0 kV
EHD Cutoff	Voltage V≤V 
0
​
 	Thrust = 0 mN (Strict zero-current cutoff)
HTS Suspension	Dipole m=120 A⋅m 
2
 , h=8 mm, h 
c
​
 =15 mm	F 
z
​
 ≈450−500 N (≈45−51 kg payload)
Acoustic Trap	40 kHz, SPL = 155 dB, Sphere r=1.5 mm	Traps materials with densities up to ≈1,200 kg/m 
3
  (water, polymers)
Gertsenshtein	B=15 T, L=10 m	Conversion probability ∼O(10 
−41
 )

References
Peek, F. W. (1929). Dielectric Phenomena in High Voltage Engineering. McGraw-Hill.

Kordyuk, A. A. (1998). "Magnetic levitation for hard superconductors." Journal of Applied Physics, 83(1), 610–612.

Gor'kov, L. P. (1962). "On the forces acting on a small particle in an acoustical field in an ideal fluid." Soviet Physics Doklady, 6, 773.

CERN ALPHA Collaboration (2023). "Observation of the effect of gravity on the motion of antimatter." Nature, 621, 716–722.

Gertsenshtein, M. E. (1962). "Wave resonance of light and gravitational waves." Soviet Physics JETP, 14, 84–85.
