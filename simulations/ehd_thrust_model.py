#!/usr/bin/env python3
"""
Electrohydrodynamic (EHD) Thrust / Ion Propulsion Analytical Model
Calculates corona inception, Townsend space-charge current, ion drift thrust,
electrical-to-kinetic conversion efficiency, and untethered flight mass margins.
"""

import math

# Physical Constants
EPSILON_0 = 8.8541878128e-12  # Vacuum permittivity (F/m)
ION_MOBILITY_AIR = 2.0e-4      # Average ion mobility in air (m^2 / (V*s))
AIR_DENSITY_STP = 1.225        # Air density at STP (kg/m^3)
G_ACCEL = 9.80665              # Gravitational acceleration (m/s^2)
E_BREAKDOWN_AIR = 3.0e6        # Nominal uniform dielectric breakdown of air (V/m)
PEEK_E0 = 3.1e6                # Peek's empirical baseline field (V/m)


def calculate_peeks_inception_voltage(
    wire_radius_m: float,
    gap_distance_m: float,
    surface_factor: float = 0.9,
    relative_air_density: float = 1.0
) -> float:
    """
    Calculates corona inception voltage using Peek's Law for a thin wire over a plane/collector.
    E_c = E_0 * m * delta * (1 + 0.0308 / sqrt(delta * r_w))
    V_0 = E_c * r_w * ln(2 * d / r_w)
    """
    rw_cm = wire_radius_m * 100.0
    ec_v_cm = PEEK_E0 * 0.01 * surface_factor * relative_air_density * (
        1.0 + 0.308 / math.sqrt(relative_air_density * rw_cm)
    )
    ec_v_m = ec_v_cm * 100.0
    v_inception = ec_v_m * wire_radius_m * math.log(2.0 * gap_distance_m / wire_radius_m)
    return v_inception


def calculate_ehd_performance(
    voltage_v: float,
    wire_radius_m: float,
    wire_length_m: float,
    gap_distance_m: float,
    mobility: float = ION_MOBILITY_AIR
) -> dict:
    """
    Computes Townsend space-charge limited current, thrust, thrust-to-power,
    and ion drift velocity.
    """
    v0 = calculate_peeks_inception_voltage(wire_radius_m, gap_distance_m)
    if voltage_v <= v0:
        return {
            "v_inception_v": v0,
            "operating_voltage_v": voltage_v,
            "current_a": 0.0,
            "power_w": 0.0,
            "thrust_n": 0.0,
            "thrust_gf": 0.0,
            "thrust_to_power_n_kw": 0.0,
            "ion_velocity_m_s": 0.0,
            "active": False
        }

    # Townsend quadratic current relation: I = C * mu * epsilon_0 * (L / d^2) * V * (V - V_0)
    # Dimensionless geometry factor C ~ 2.0 to 2.5 for wire-to-foil
    geom_factor = 2.2
    current = geom_factor * mobility * EPSILON_0 * (wire_length_m / (gap_distance_m ** 2)) * voltage_v * (voltage_v - v0)
    power = voltage_v * current

    # EHD Thrust equation: T = (I * d) / mu
    thrust = (current * gap_distance_m) / mobility
    thrust_gf = (thrust / G_ACCEL) * 1000.0  # Grams-force

    thrust_to_power = (thrust / power) * 1000.0 if power > 0 else 0.0  # N / kW
    avg_electric_field = voltage_v / gap_distance_m
    ion_drift_vel = mobility * avg_electric_field

    return {
        "v_inception_v": v0,
        "operating_voltage_v": voltage_v,
        "current_a": current,
        "power_w": power,
        "thrust_n": thrust,
        "thrust_gf": thrust_gf,
        "thrust_to_power_n_kw": thrust_to_power,
        "ion_velocity_m_s": ion_drift_vel,
        "active": True
    }


def evaluate_untethered_lift(
    ehd_results: dict,
    frame_mass_g: float = 35.0,
    hv_converter_specific_power_w_per_kg: float = 1200.0,  # e.g., high-efficiency Cockcroft-Walton
    battery_energy_density_wh_per_kg: float = 180.0,
    flight_time_minutes: float = 3.0
) -> dict:
    """
    Evaluates whether the lifter can close the untethered flight threshold carrying its
    own power supply, HV multiplier, and frame.
    """
    power_w = ehd_results["power_w"]
    thrust_gf = ehd_results["thrust_gf"]

    # Mass of high-voltage step-up converter
    converter_mass_kg = power_w / hv_converter_specific_power_w_per_kg if hv_converter_specific_power_w_per_kg > 0 else 0
    converter_mass_g = converter_mass_kg * 1000.0

    # Required battery capacity for desired flight time
    energy_wh = power_w * (flight_time_minutes / 60.0)
    battery_mass_kg = energy_wh / battery_energy_density_wh_per_kg if battery_energy_density_wh_per_kg > 0 else 0
    battery_mass_g = battery_mass_kg * 1000.0

    total_mass_g = frame_mass_g + converter_mass_g + battery_mass_g
    net_lift_gf = thrust_gf - total_mass_g
    thrust_to_weight_ratio = thrust_gf / total_mass_g if total_mass_g > 0 else 0.0

    return {
        "total_mass_g": total_mass_g,
        "frame_mass_g": frame_mass_g,
        "converter_mass_g": converter_mass_g,
        "battery_mass_g": battery_mass_g,
        "thrust_gf": thrust_gf,
        "net_lift_gf": net_lift_gf,
        "twr": thrust_to_weight_ratio,
        "is_flight_viable": net_lift_gf > 0.0
    }


def print_report():
    print("=" * 75)
    print(" ELECTROHYDRODYNAMIC (EHD) THRUST & UNTETHERED LIFTER MODEL")
    print("=" * 75)

    wire_r = 50e-6  # 50-micron tungsten/corona wire
    wire_l = 4.0    # 4 meters total emitter perimeter
    gap_d = 0.04    # 40 mm inter-electrode spacing

    v0 = calculate_peeks_inception_voltage(wire_r, gap_d)
    print(f" Corona Wire Radius:        {wire_r * 1e6:.1f} um")
    print(f" Emitter-Collector Gap (d): {gap_d * 1e3:.1f} mm")
    print(f" Total Emitter Length:      {wire_l:.2f} m")
    print(f" Peek's Inception Voltage:  {v0 / 1e3:.2f} kV")
    print("-" * 75)

    voltages_kv = [15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
    print(f"{'V (kV)':>7} | {'Current (mA)':>12} | {'Power (W)':>10} | {'Thrust (gf)':>11} | {'Eff (N/kW)':>10} | {'TWR':>7} | Viable?")
    print("-" * 75)

    for v_kv in voltages_kv:
        res = calculate_ehd_performance(v_kv * 1e3, wire_r, wire_l, gap_d)
        flight = evaluate_untethered_lift(res, frame_mass_g=25.0)
        status = "YES (LIFT)" if flight["is_flight_viable"] else "NO"
        print(
            f"{v_kv:>7.1f} | "
            f"{res['current_a'] * 1e3:>12.2f} | "
            f"{res['power_w']:>10.2f} | "
            f"{res['thrust_gf']:>11.2f} | "
            f"{res['thrust_to_power_n_kw']:>10.2f} | "
            f"{flight['twr']:>7.2f} | {status}"
        )
    print("=" * 75)


if __name__ == "__main__":
    print_report()
