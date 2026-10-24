# Low frequency transient of the IEEE 14 case. It starts from the power flow of power_flow.jl, which must be run
# before in the same session, so that system, solution and generation are in memory. From the root of the package,
# in the environment of PowerSystemExperiments:
#   include("cases/ieee14/power_flow.jl")
#   include("cases/ieee14/low_freq_transient.jl")
# The results are written to cases/ieee14/results, together with the dashboard that shows them

using nsLFT
import PowerSystemExperiments

if !@isdefined(solution)
    error("Run power_flow.jl before this script, so that the power flow solution is in memory.")
end

# The element order is the same as in power_flow.jl, so that element k of the power flow is element k of nsLFT.
# The voltages of the buses and the powers of the generators and loads come from the power flow

# Buses
buses = nsLFT.Bus[
    nsLFT.Bus(;
        name = "Bus 01",
        voltage = solution.voltage[1],
        angle = solution.voltage_angle[1],
        shunt_susceptance = 0.0,
        generator_idx = 1,
    ),
    nsLFT.Bus(;
        name = "Bus 02",
        voltage = solution.voltage[2],
        angle = solution.voltage_angle[2],
        shunt_susceptance = 0.0,
        generator_idx = 2,
        load_idx = 1,
    ),
    nsLFT.Bus(;
        name = "Bus 03",
        voltage = solution.voltage[3],
        angle = solution.voltage_angle[3],
        shunt_susceptance = 0.0,
        generator_idx = 3,
        load_idx = 2,
    ),
    nsLFT.Bus(;
        name = "Bus 04",
        voltage = solution.voltage[4],
        angle = solution.voltage_angle[4],
        shunt_susceptance = 0.0,
        load_idx = 3,
    ),
    nsLFT.Bus(;
        name = "Bus 05",
        voltage = solution.voltage[5],
        angle = solution.voltage_angle[5],
        shunt_susceptance = 0.0,
        load_idx = 4,
    ),
    nsLFT.Bus(;
        name = "Bus 06",
        voltage = solution.voltage[6],
        angle = solution.voltage_angle[6],
        shunt_susceptance = 0.0,
        generator_idx = 4,
        load_idx = 5,
    ),
    nsLFT.Bus(;
        name = "Bus 07",
        voltage = solution.voltage[7],
        angle = solution.voltage_angle[7],
        shunt_susceptance = 0.0,
    ),
    nsLFT.Bus(;
        name = "Bus 08",
        voltage = solution.voltage[8],
        angle = solution.voltage_angle[8],
        shunt_susceptance = 0.0,
        generator_idx = 5,
    ),
    # capacitor bank of 19 Mvar at 1 pu
    nsLFT.Bus(;
        name = "Bus 09",
        voltage = solution.voltage[9],
        angle = solution.voltage_angle[9],
        shunt_susceptance = 0.19,
        load_idx = 6,
    ),
    nsLFT.Bus(;
        name = "Bus 10",
        voltage = solution.voltage[10],
        angle = solution.voltage_angle[10],
        shunt_susceptance = 0.0,
        load_idx = 7,
    ),
    nsLFT.Bus(;
        name = "Bus 11",
        voltage = solution.voltage[11],
        angle = solution.voltage_angle[11],
        shunt_susceptance = 0.0,
        load_idx = 8,
    ),
    nsLFT.Bus(;
        name = "Bus 12",
        voltage = solution.voltage[12],
        angle = solution.voltage_angle[12],
        shunt_susceptance = 0.0,
        load_idx = 9,
    ),
    nsLFT.Bus(;
        name = "Bus 13",
        voltage = solution.voltage[13],
        angle = solution.voltage_angle[13],
        shunt_susceptance = 0.0,
        load_idx = 10,
    ),
    nsLFT.Bus(;
        name = "Bus 14",
        voltage = solution.voltage[14],
        angle = solution.voltage_angle[14],
        shunt_susceptance = 0.0,
        load_idx = 11,
    ),
]

# Lines. nsLFT takes the total shunt susceptance of the pi model and splits it between the two ends
circuits = nsLFT.Circuit[
    nsLFT.Circuit(;
        name = "LT1-2",
        from_bus_idx = 1,
        to_bus_idx = 2,
        resistance = 0.0193,
        reactance = 0.0592,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0528,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT1-5",
        from_bus_idx = 1,
        to_bus_idx = 5,
        resistance = 0.05403,
        reactance = 0.223,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0492,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT2-3",
        from_bus_idx = 2,
        to_bus_idx = 3,
        resistance = 0.04699,
        reactance = 0.198,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0438,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT2-4",
        from_bus_idx = 2,
        to_bus_idx = 4,
        resistance = 0.05811,
        reactance = 0.1763,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0374,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT2-5",
        from_bus_idx = 2,
        to_bus_idx = 5,
        resistance = 0.05695,
        reactance = 0.1739,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.034,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT3-4",
        from_bus_idx = 3,
        to_bus_idx = 4,
        resistance = 0.06701,
        reactance = 0.171,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0346,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT4-5",
        from_bus_idx = 4,
        to_bus_idx = 5,
        resistance = 0.01335,
        reactance = 0.0421,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0128,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT6-11",
        from_bus_idx = 6,
        to_bus_idx = 11,
        resistance = 0.09498,
        reactance = 0.1989,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT6-12",
        from_bus_idx = 6,
        to_bus_idx = 12,
        resistance = 0.12291,
        reactance = 0.2558,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT6-13",
        from_bus_idx = 6,
        to_bus_idx = 13,
        resistance = 0.06615,
        reactance = 0.1303,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT7-8",
        from_bus_idx = 7,
        to_bus_idx = 8,
        resistance = 0.0,
        reactance = 0.1761,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT7-9",
        from_bus_idx = 7,
        to_bus_idx = 9,
        resistance = 0.0,
        reactance = 0.11,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT9-10",
        from_bus_idx = 9,
        to_bus_idx = 10,
        resistance = 0.03181,
        reactance = 0.0845,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT9-14",
        from_bus_idx = 9,
        to_bus_idx = 14,
        resistance = 0.12711,
        reactance = 0.2704,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT10-11",
        from_bus_idx = 10,
        to_bus_idx = 11,
        resistance = 0.08205,
        reactance = 0.1921,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT12-13",
        from_bus_idx = 12,
        to_bus_idx = 13,
        resistance = 0.22092,
        reactance = 0.1999,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    nsLFT.Circuit(;
        name = "LT13-14",
        from_bus_idx = 13,
        to_bus_idx = 14,
        resistance = 0.17093,
        reactance = 0.348,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1.0,
    ),
    # Transformers. The tap a sits on the from side, so the series current is (V_from / a - V_to) / Z,
    # which in the admittance matrix of nsLFT means tap_ratio = 1 / a
    nsLFT.Circuit(;
        name = "TR4-7",
        from_bus_idx = 4,
        to_bus_idx = 7,
        resistance = 0.0,
        reactance = 0.2091,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1 / 0.978,
    ),
    nsLFT.Circuit(;
        name = "TR4-9",
        from_bus_idx = 4,
        to_bus_idx = 9,
        resistance = 0.0,
        reactance = 0.5562,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1 / 0.969,
    ),
    nsLFT.Circuit(;
        name = "TR5-6",
        from_bus_idx = 5,
        to_bus_idx = 6,
        resistance = 0.0,
        reactance = 0.252,
        shunt_conductance = 0.0,
        shunt_susceptance = 0.0,
        tap_ratio = 1 / 0.932,
    ),
]

# Generators, with the parameters in the machine base, including the droop of the governors. Vn is NaN because the
# case gives no rated voltage and the model does not use it yet. UG3, UG6 and UG8 are synchronous condensers,
# which have no turbine and therefore no governor. Every machine has a voltage regulator, including the synchronous
# condensers, whose only role is to hold the voltage of their bus
generators = nsLFT.Generator[
    nsLFT.OneDOneQGenerator(;
        name = "UG1",
        bus = 1,
        Sn = 286.1881227,
        Vn = NaN,
        Xd = 1.8,
        Xd_prime = 0.4,
        Xq = 1.7,
        Xq_prime = 0.4,
        Ra = 0.0,
        Td0_prime = 8.0,
        Tq0_prime = 0.4,
        H = 5.0,
        D = 2.0,
        P0 = real(generation[1]),
        Q0 = imag(generation[1]),
        governor = nsLFT.Droop1stOrder(; name = "UG1 gov", R = 0.05, Tc = 0.01, Tr = 2.0, omega_ref = 60.0),
        voltage_regulator = nsLFT.Static1stOrder(; name = "UG1 avr", K = 50.0, T = 0.05, Lmn = -5.0, Lmx = 5.0),
    ),
    nsLFT.OneDOneQGenerator(;
        name = "UG2",
        bus = 2,
        Sn = 88.09334324,
        Vn = NaN,
        Xd = 1.8,
        Xd_prime = 0.4,
        Xq = 1.7,
        Xq_prime = 0.4,
        Ra = 0.0,
        Td0_prime = 8.0,
        Tq0_prime = 0.4,
        H = 5.0,
        D = 2.0,
        P0 = real(generation[2]),
        Q0 = imag(generation[2]),
        governor = nsLFT.Droop1stOrder(; name = "UG2 gov", R = 0.05, Tc = 0.01, Tr = 2.0, omega_ref = 60.0),
        voltage_regulator = nsLFT.Static1stOrder(; name = "UG2 avr", K = 50.0, T = 0.05, Lmn = -5.0, Lmx = 5.0),
    ),
    nsLFT.OneDOneQGenerator(;
        name = "UG3",
        bus = 3,
        Sn = 75.889,
        Vn = NaN,
        Xd = 1.8,
        Xd_prime = 0.4,
        Xq = 1.7,
        Xq_prime = 0.4,
        Ra = 0.0,
        Td0_prime = 8.0,
        Tq0_prime = 0.4,
        H = 5.0,
        D = 2.0,
        P0 = real(generation[3]),
        Q0 = imag(generation[3]),
        voltage_regulator = nsLFT.Static1stOrder(; name = "UG3 avr", K = 50.0, T = 0.05, Lmn = -5.0, Lmx = 5.0),
    ),
    nsLFT.OneDOneQGenerator(;
        name = "UG6",
        bus = 6,
        Sn = 40.722,
        Vn = NaN,
        Xd = 1.8,
        Xd_prime = 0.4,
        Xq = 1.7,
        Xq_prime = 0.4,
        Ra = 0.0,
        Td0_prime = 8.0,
        Tq0_prime = 0.4,
        H = 5.0,
        D = 2.0,
        P0 = real(generation[4]),
        Q0 = imag(generation[4]),
        voltage_regulator = nsLFT.Static1stOrder(; name = "UG6 avr", K = 50.0, T = 0.05, Lmn = -5.0, Lmx = 5.0),
    ),
    nsLFT.OneDOneQGenerator(;
        name = "UG8",
        bus = 8,
        Sn = 7.1863,
        Vn = NaN,
        Xd = 1.8,
        Xd_prime = 0.4,
        Xq = 1.7,
        Xq_prime = 0.4,
        Ra = 0.0,
        Td0_prime = 8.0,
        Tq0_prime = 0.4,
        H = 5.0,
        D = 2.0,
        P0 = real(generation[5]),
        Q0 = imag(generation[5]),
        voltage_regulator = nsLFT.Static1stOrder(; name = "UG8 avr", K = 50.0, T = 0.05, Lmn = -5.0, Lmx = 5.0),
    ),
]

# Loads
loads = nsLFT.Load[
    nsLFT.ConstantZLoad(;
        name = "CR2",
        bus = 2,
        P0 = PSD.load_active_power(system, 1),
        Q0 = PSD.load_reactive_power(system, 1),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR3",
        bus = 3,
        P0 = PSD.load_active_power(system, 2),
        Q0 = PSD.load_reactive_power(system, 2),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR4",
        bus = 4,
        P0 = PSD.load_active_power(system, 3),
        Q0 = PSD.load_reactive_power(system, 3),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR5",
        bus = 5,
        P0 = PSD.load_active_power(system, 4),
        Q0 = PSD.load_reactive_power(system, 4),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR6",
        bus = 6,
        P0 = PSD.load_active_power(system, 5),
        Q0 = PSD.load_reactive_power(system, 5),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR9",
        bus = 9,
        P0 = PSD.load_active_power(system, 6),
        Q0 = PSD.load_reactive_power(system, 6),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR10",
        bus = 10,
        P0 = PSD.load_active_power(system, 7),
        Q0 = PSD.load_reactive_power(system, 7),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR11",
        bus = 11,
        P0 = PSD.load_active_power(system, 8),
        Q0 = PSD.load_reactive_power(system, 8),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR12",
        bus = 12,
        P0 = PSD.load_active_power(system, 9),
        Q0 = PSD.load_reactive_power(system, 9),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR13",
        bus = 13,
        P0 = PSD.load_active_power(system, 10),
        Q0 = PSD.load_reactive_power(system, 10),
    ),
    nsLFT.ConstantZLoad(;
        name = "CR14",
        bus = 14,
        P0 = PSD.load_active_power(system, 11),
        Q0 = PSD.load_reactive_power(system, 11),
    ),
]

# trip of the generator UG2 at t = 1 s
perturbations = nsLFT.Perturbation[nsLFT.GeneratorTrip(; name = "UG2 trip", generator_idx = 2, time = 1.0)]

# trip of the line between buses 14 and 13 at t = 1.2 s, after a short circuit at bus 14 at t = 1.0 s
# perturbations = [nsLFT.ShortCircuit("curto-b14", 14, 1.0, 99999, 0), nsLFT.ShortCircuitRemoval("rm-curto-b14", 1, 1.2), nsLFT.CircuitTrip("trip-linha-b14-13", 17, 1.2)]

inputs = nsLFT.Inputs(;
    case_path = @__DIR__,
    Sb = PSD.base_power(system),
    fb = PSD.base_frequency(system),
    integration_step = 0.01,
    simulation_horizon = 10.0,
    tolerance = 1e-10,
    buses = buses,
    circuits = circuits,
    generators = generators,
    loads = loads,
    perturbations = perturbations,
)
output_dir = "results-1d1q-gov-avr-trip-ug2"
output_path = joinpath(nsLFT.case_path(inputs), output_dir)
results = nsLFT.solve(inputs; output_path)

# nsLFT writes the results to <case>/results, and the dashboard is built from those files
if !isdir(output_path)
    mkpath(output_path)
end
PowerSystemExperiments.write_dashboard(output_path)

nothing
