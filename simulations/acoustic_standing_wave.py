#!/usr/bin/env python3
"""
Ultrasonic Acoustic Levitation & Standing Wave Trapping Model
Calculates acoustic pressure fields, Gor'kov potential wells, radiation force nodes,
and maximum levitatable density for 40 kHz phased arrays.
"""

import math

# Physical Constants
AIR_DENSITY = 1.204        # Air density at 20°C (kg/m^3)
SPEED_OF_SOUND = 343.2     # Speed of sound in air (m/s)
P_REF = 20e-6              # Acoustic reference pressure in air (Pa, 0 dB SPL)
G_ACCEL = 9.80665          # Gravitational acceleration (m/s^2)


def acoustic_wave_parameters(frequency_hz: float = 40000.0) -> dict:
    """
    Computes acoustic wavelength, wavenumber, and angular frequency.
    """
    wavelength_m = SPEED_OF_SOUND / frequency_hz
    k = 2.0 * math.pi / wavelength_m
    omega = 2.0 * math.pi * frequency_hz
    node_spacing_m = wavelength_m / 2.0

    return {
        "frequency_hz": frequency_hz,
        "wavelength_mm": wavelength_m * 1e3,
        "wavenumber_k": k,
        "omega_rad_s": omega,
        "node_spacing_mm": node_spacing_m * 1e3,
        "max_particle_diameter_mm": (wavelength_m * 0.2) * 1e3  # Rayleigh scattering limit
    }


def pressure_from_spl(spl_db: float) -> float:
    """Converts Sound Pressure Level (dB) to RMS pressure amplitude in Pascals."""
    return P_REF * (10.0 ** (spl_db / 20.0))


def spl_from_pressure(p_rms_pa: float) -> float:
    """Converts RMS pressure in Pascals to Sound Pressure Level (dB)."""
    if p_rms_pa <= 0:
        return 0.0
    return 20.0 * math.log10(p_rms_pa / P_REF)


def calculate_gorkov_potential_and_force(
    z_m: float,
    p0_peak_pa: float,
    particle_radius_m: float,
    particle_density_kg_m3: float,
    frequency_hz: float = 40000.0
) -> dict:
    """
    Computes local acoustic pressure, particle velocity, Gor'kov potential U,
    and primary acoustic radiation force F_z along the standing wave axis.
    """
    params = acoustic_wave_parameters(frequency_hz)
    k = params["wavenumber_k"]
    rho0 = AIR_DENSITY
    c0 = SPEED_OF_SOUND

    # Standing wave pressure: p(z) = 2 * P0 * cos(k*z)
    # Standing wave velocity: v(z) = (2 * P0 / (rho0 * c0)) * sin(k*z)
    # Time-averaged square pressure and velocity:
    p_sq_avg = 2.0 * (p0_peak_pa ** 2) * (math.cos(k * z_m) ** 2)
    v_sq_avg = 2.0 * ((p0_peak_pa / (rho0 * c0)) ** 2) * (math.sin(k * z_m) ** 2)

    # Monopole and dipole contrast factors (assuming incompressible rigid particle)
    f1 = 1.0
    f2 = (2.0 * (particle_density_kg_m3 - rho0)) / (2.0 * particle_density_kg_m3 + rho0)

    # Gor'kov potential U
    vol = (4.0 / 3.0) * math.pi * (particle_radius_m ** 3)
    u_pot = 2.0 * math.pi * (particle_radius_m ** 3) * (
        (p_sq_avg / (3.0 * rho0 * (c0 ** 2))) * f1 - (rho0 * v_sq_avg / 2.0) * f2
    )

    # Primary radiation force F_z = -dU/dz = (5 * pi * P0^2 * r^3 * k) / (6 * rho0 * c0^2) * sin(2*k*z)
    force_amplitude = (5.0 * math.pi * (p0_peak_pa ** 2) * (particle_radius_m ** 3) * k) / (6.0 * rho0 * (c0 ** 2))
    force_z = force_amplitude * math.sin(2.0 * k * z_m)

    particle_mass_kg = vol * particle_density_kg_m3
    particle_weight_n = particle_mass_kg * G_ACCEL
    net_force_z = force_z - particle_weight_n

    return {
        "z_mm": z_m * 1e3,
        "force_radiation_n": force_z,
        "particle_weight_n": particle_weight_n,
        "net_vertical_force_n": net_force_z,
        "gorkov_potential_j": u_pot,
        "can_trap_against_gravity": force_amplitude > particle_weight_n
    }


def calculate_maximum_levitatable_density(p0_peak_pa: float, frequency_hz: float = 40000.0) -> float:
    """
    Calculates the theoretical maximum density a particle can have and still be trapped.
    rho_max = (5 * P0^2 * k) / (8 * rho0 * c0^2 * g)
    """
    params = acoustic_wave_parameters(frequency_hz)
    k = params["wavenumber_k"]
    rho0 = AIR_DENSITY
    c0 = SPEED_OF_SOUND
    rho_max = (5.0 * (p0_peak_pa ** 2) * k) / (8.0 * rho0 * (c0 ** 2) * G_ACCEL)
    return rho_max


def print_report():
    print("=" * 75)
    print(" ULTRASONIC ACOUSTIC LEVITATION (40 KHZ PHASED ARRAY) MODEL")
    print("=" * 75)

    params = acoustic_wave_parameters(40000.0)
    print(f" Driving Frequency:         {params['frequency_hz'] / 1e3:.1f} kHz")
    print(f" Acoustic Wavelength:       {params['wavelength_mm']:.2f} mm")
    print(f" Pressure Node Spacing:     {params['node_spacing_mm']:.2f} mm")
    print(f" Rayleigh Diameter Limit:   {params['max_particle_diameter_mm']:.2f} mm")
    print("-" * 75)

    # Test with standard materials: Styrofoam (30 kg/m^3), Water droplet (1000 kg/m^3), Aluminum (2700 kg/m^3)
    spl_test_levels = [140.0, 150.0, 155.0, 160.0, 165.0]
    particle_radius = 1.0e-3  # 1 mm radius (2 mm diameter)

    print(f"{'SPL (dB)':>9} | {'P_RMS (Pa)':>11} | {'Max Density (kg/m3)':>20} | Styrofoam | Water | Aluminum")
    print("-" * 75)

    for spl in spl_test_levels:
        p_rms = pressure_from_spl(spl)
        p_peak = p_rms * math.sqrt(2.0)
        rho_max = calculate_maximum_levitatable_density(p_peak)

        styrofoam_ok = "TRAP" if rho_max >= 30.0 else "FALL"
        water_ok = "TRAP" if rho_max >= 1000.0 else "FALL"
        alum_ok = "TRAP" if rho_max >= 2700.0 else "FALL"

        print(
            f"{spl:>9.1f} | "
            f"{p_rms:>11.1f} | "
            f"{rho_max:>20.1f} | "
            f"{styrofoam_ok:>9} | "
            f"{water_ok:>5} | "
            f"{alum_ok:>8}"
        )
    print("-" * 75)

    # Profile across one pressure node (0 to lambda/2)
    p_op = pressure_from_spl(160.0) * math.sqrt(2.0)
    print(" RADIATION FORCE PROFILE ACROSS ONE STANDING WAVE NODE (SPL = 160 dB, Water Droplet):")
    print(f"{'z / (lambda/2)':>15} | {'z (mm)':>8} | {'F_rad (uN)':>12} | {'Weight (uN)':>12} | Action")
    print("-" * 75)
    for step in range(9):
        frac = step / 8.0
        z_pos = frac * (params["node_spacing_mm"] * 1e-3)
        res = calculate_gorkov_potential_and_force(z_pos, p_op, particle_radius, 1000.0)
        action = "Restores UP" if res["net_vertical_force_n"] > 0 else "Drifts DOWN"
        print(
            f"{frac:>15.3f} | "
            f"{res['z_mm']:>8.2f} | "
            f"{res['force_radiation_n'] * 1e6:>12.2f} | "
            f"{res['particle_weight_n'] * 1e6:>12.2f} | {action}"
        )
    print("=" * 75)


if __name__ == "__main__":
    print_report()
