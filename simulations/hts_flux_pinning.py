#!/usr/bin/env python3
"""
High-Temperature Superconductor (HTS) Flux-Pinning & Halbach Array Levitation Model
Calculates Halbach magnetic field profiles, frozen-image vertical restoring forces,
lateral stiffness, and multi-puck array sizing for a 50 kg class payload.
"""

import math

# Physical Constants
MU_0 = 4.0 * math.pi * 1e-7  # Vacuum permeability (T*m / A)
G_ACCEL = 9.80665            # Gravitational acceleration (m/s^2)


def halbach_surface_field(
    b_remanence: float = 1.48,   # NdFeB N52 remanence (Tesla)
    magnet_width_m: float = 0.02, # 20 mm cube magnets
    magnet_height_m: float = 0.02,
    elements_per_period: int = 4
) -> dict:
    """
    Computes Halbach wavelength, wavenumber, and peak surface flux density.
    B_0 = B_r * (sin(pi/M) / (pi/M)) * (1 - e^(-k * h))
    """
    wavelength = elements_per_period * magnet_width_m
    k = 2.0 * math.pi / wavelength
    m = float(elements_per_period)
    sinc_factor = math.sin(math.pi / m) / (math.pi / m)
    thickness_factor = 1.0 - math.exp(-k * magnet_height_m)
    b0 = b_remanence * sinc_factor * thickness_factor

    return {
        "wavelength_m": wavelength,
        "wavenumber_k": k,
        "b0_peak_surface_t": b0,
        "remanence_t": b_remanence
    }


def calculate_halbach_field_at_gap(halbach_info: dict, gap_z_m: float) -> float:
    """
    Calculates magnetic flux density at height z above the Halbach array track.
    B(z) = B_0 * e^(-k * z)
    """
    b0 = halbach_info["b0_peak_surface_t"]
    k = halbach_info["wavenumber_k"]
    return b0 * math.exp(-k * gap_z_m)


def calculate_flux_pinning_force(
    puck_diameter_m: float,
    gap_z_m: float,
    field_cooling_gap_m: float,
    halbach_info: dict,
    j_c_a_per_m2: float = 1.5e8  # Typical YBCO critical current density ~1.5e4 A/cm^2
) -> dict:
    """
    Calculates vertical restoring force and lateral stiffness using the frozen-image
    and Bean critical state formulation.
    """
    puck_radius = puck_diameter_m / 2.0
    puck_area = math.pi * (puck_radius ** 2)

    k = halbach_info["wavenumber_k"]
    b0 = halbach_info["b0_peak_surface_t"]

    # Maximum magnetic pressure: P_max = B^2 / (2 * mu_0)
    # The interaction between the trapped flux and external Halbach field gradient gives:
    # F_z = (B0^2 * Area / (2 * mu0)) * (e^(-2*k*z) - e^(-k*(z + z_fc)))
    bz_operating = b0 * math.exp(-k * gap_z_m)
    bz_fc = b0 * math.exp(-k * field_cooling_gap_m)

    # Restoring force: expelling when z < z_fc, attracting when z > z_fc
    f_repulsive = (puck_area * (b0 ** 2) / (2.0 * MU_0)) * math.exp(-2.0 * k * gap_z_m)
    f_pinned = (puck_area * (b0 ** 2) / (2.0 * MU_0)) * math.exp(-k * (gap_z_m + field_cooling_gap_m))
    f_vertical_net = f_repulsive - f_pinned

    # Vertical stiffness k_z = -dF_z / dz
    stiffness_z = 2.0 * k * f_repulsive - k * f_pinned

    # Lateral stiffness k_x is governed by vortex pinning energy
    stiffness_x = 0.35 * stiffness_z

    return {
        "gap_z_mm": gap_z_m * 1e3,
        "fc_gap_mm": field_cooling_gap_m * 1e3,
        "b_at_gap_t": bz_operating,
        "f_vertical_n": f_vertical_net,
        "mass_supported_kg": max(0.0, f_vertical_net / G_ACCEL),
        "stiffness_z_n_per_mm": stiffness_z / 1e3,
        "stiffness_x_n_per_mm": stiffness_x / 1e3,
        "puck_area_cm2": puck_area * 1e4
    }


def design_50kg_levitation_system(target_mass_kg: float = 50.0) -> dict:
    """
    Determines number of YBCO pucks, Halbach track area, and LN2/cryocooler thermal budget.
    """
    weight_n = target_mass_kg * G_ACCEL
    halbach = halbach_surface_field(b_remanence=1.45, magnet_width_m=0.025, magnet_height_m=0.025)

    # Standard commercial YBCO puck: 30 mm diameter, 12 mm height
    puck_dia_m = 0.030
    nominal_operating_gap_m = 0.008  # 8 mm gap
    fc_gap_m = 0.015                # 15 mm field-cooling height

    single_puck = calculate_flux_pinning_force(puck_dia_m, nominal_operating_gap_m, fc_gap_m, halbach)
    force_per_puck = single_puck["f_vertical_n"]

    num_pucks_needed = math.ceil(weight_n / force_per_puck)
    actual_capacity_kg = (num_pucks_needed * force_per_puck) / G_ACCEL
    safety_margin = (actual_capacity_kg / target_mass_kg - 1.0) * 100.0

    # Thermal budget:
    # Radiation heat leak: ~1.5 W / m^2 of cryostat outer jacket
    # Conduction through suspension mounts: ~0.8 W per puck assembly
    cryostat_area_m2 = num_pucks_needed * 0.008 + 0.05
    thermal_load_w = (cryostat_area_m2 * 2.0) + (num_pucks_needed * 0.4)
    # Closed-loop Stirling cryocooler COP at 77K is roughly 0.05 (20 W electrical per 1 W cooling)
    cryocooler_electrical_power_w = thermal_load_w / 0.05

    return {
        "target_mass_kg": target_mass_kg,
        "target_weight_n": weight_n,
        "puck_diameter_mm": puck_dia_m * 1e3,
        "operating_gap_mm": nominal_operating_gap_m * 1e3,
        "force_per_puck_n": force_per_puck,
        "num_pucks": num_pucks_needed,
        "total_lift_capacity_kg": actual_capacity_kg,
        "safety_margin_pct": safety_margin,
        "thermal_load_77k_w": thermal_load_w,
        "cryocooler_input_power_w": cryocooler_electrical_power_w
    }


def print_report():
    print("=" * 75)
    print(" HIGH-TEMPERATURE SUPERCONDUCTING (HTS) FLUX-PINNING LEVITATION MODEL")
    print("=" * 75)

    halbach = halbach_surface_field(b_remanence=1.45, magnet_width_m=0.025, magnet_height_m=0.025)
    print(f" Halbach Period (Wavelength): {halbach['wavelength_m'] * 1e3:.1f} mm")
    print(f" Halbach Decay Constant (k):  {halbach['wavenumber_k']:.2f} m^-1")
    print(f" Peak Surface Field (B0):     {halbach['b0_peak_surface_t']:.3f} Tesla")
    print("-" * 75)

    puck_dia = 0.030  # 30 mm diameter YBCO
    fc_gap = 0.015    # Field cooled at 15 mm

    print(f"{'Gap (mm)':>9} | {'B-Field (T)':>12} | {'Force (N)':>10} | {'Lift (kg)':>10} | {'kz (N/mm)':>11} | {'kx (N/mm)':>11}")
    print("-" * 75)

    for gap_mm in [3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 18.0]:
        res = calculate_flux_pinning_force(puck_dia, gap_mm * 1e-3, fc_gap, halbach)
        print(
            f"{gap_mm:>9.1f} | "
            f"{res['b_at_gap_t']:>12.3f} | "
            f"{res['f_vertical_n']:>10.2f} | "
            f"{res['mass_supported_kg']:>10.2f} | "
            f"{res['stiffness_z_n_per_mm']:>11.2f} | "
            f"{res['stiffness_x_n_per_mm']:>11.2f}"
        )
    print("-" * 75)

    sys50 = design_50kg_levitation_system(50.0)
    print(" 50 KG SCALE PROTOTYPE CONFIGURATION:")
    print(f"  Puck Count:            {sys50['num_pucks']} x YBCO (Ø {sys50['puck_diameter_mm']:.0f} mm)")
    print(f"  Operating Gap:         {sys50['operating_gap_mm']:.1f} mm")
    print(f"  Total Capacity:        {sys50['total_lift_capacity_kg']:.1f} kg (Safety margin: +{sys50['safety_margin_pct']:.1f}%)")
    print(f"  Thermal Load @ 77K:    {sys50['thermal_load_77k_w']:.2f} W (Cooler input: {sys50['cryocooler_input_power_w']:.1f} W)")
    print("=" * 75)


if __name__ == "__main__":
    print_report()
