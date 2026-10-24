# Power flow of the IEEE 14 case, solved by PowerFlow.jl. It runs in the environment of PowerSystemExperiments,
# from the root of the package,
#   julia --project=. cases/ieee14/power_flow.jl
# and leaves system, solution and generation in memory for low_freq_transient.jl

import PowerFlow
import PowerSystemData as PSD
import PowerSystemExperiments

base = PSD.SystemBase(; frequency = 60.0, power = 100.0)
system = PSD.Input(; base = base)

# Buses. The voltages are the starting point of the power flow, a flat start, except for the angle of the slack bus,
# which is the reference. The voltage of the PV and slack buses is the setpoint of their generators
PSD.add_bus!(system; name = "Bus 01", type = PSD.BusType.Slack, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 02", type = PSD.BusType.PV, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 03", type = PSD.BusType.PV, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 04", type = PSD.BusType.PQ, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 05", type = PSD.BusType.PQ, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 06", type = PSD.BusType.PV, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 07", type = PSD.BusType.PQ, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 08", type = PSD.BusType.PV, voltage = 1.0, voltage_angle = 0.0)
# capacitor bank of 19 Mvar at 1 pu
PSD.add_bus!(
    system;
    name = "Bus 09",
    type = PSD.BusType.PQ,
    voltage = 1.0,
    voltage_angle = 0.0,
    shunt_susceptance = 0.19,
)
PSD.add_bus!(system; name = "Bus 10", type = PSD.BusType.PQ, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 11", type = PSD.BusType.PQ, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 12", type = PSD.BusType.PQ, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 13", type = PSD.BusType.PQ, voltage = 1.0, voltage_angle = 0.0)
PSD.add_bus!(system; name = "Bus 14", type = PSD.BusType.PQ, voltage = 1.0, voltage_angle = 0.0)

# Lines. PowerSystemData adds the shunt susceptance of a branch at each of its ends,
# so each end gets half of the total line charging
PSD.add_branch!(
    system;
    name = "LT1-2",
    from_bus_idx = 1,
    to_bus_idx = 2,
    resistance = 0.0193,
    reactance = 0.0592,
    shunt_susceptance = 0.0528 / 2,
)
PSD.add_branch!(
    system;
    name = "LT1-5",
    from_bus_idx = 1,
    to_bus_idx = 5,
    resistance = 0.05403,
    reactance = 0.223,
    shunt_susceptance = 0.0492 / 2,
)
PSD.add_branch!(
    system;
    name = "LT2-3",
    from_bus_idx = 2,
    to_bus_idx = 3,
    resistance = 0.04699,
    reactance = 0.198,
    shunt_susceptance = 0.0438 / 2,
)
PSD.add_branch!(
    system;
    name = "LT2-4",
    from_bus_idx = 2,
    to_bus_idx = 4,
    resistance = 0.05811,
    reactance = 0.1763,
    shunt_susceptance = 0.0374 / 2,
)
PSD.add_branch!(
    system;
    name = "LT2-5",
    from_bus_idx = 2,
    to_bus_idx = 5,
    resistance = 0.05695,
    reactance = 0.1739,
    shunt_susceptance = 0.034 / 2,
)
PSD.add_branch!(
    system;
    name = "LT3-4",
    from_bus_idx = 3,
    to_bus_idx = 4,
    resistance = 0.06701,
    reactance = 0.171,
    shunt_susceptance = 0.0346 / 2,
)
PSD.add_branch!(
    system;
    name = "LT4-5",
    from_bus_idx = 4,
    to_bus_idx = 5,
    resistance = 0.01335,
    reactance = 0.0421,
    shunt_susceptance = 0.0128 / 2,
)
PSD.add_branch!(
    system;
    name = "LT6-11",
    from_bus_idx = 6,
    to_bus_idx = 11,
    resistance = 0.09498,
    reactance = 0.1989,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT6-12",
    from_bus_idx = 6,
    to_bus_idx = 12,
    resistance = 0.12291,
    reactance = 0.2558,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT6-13",
    from_bus_idx = 6,
    to_bus_idx = 13,
    resistance = 0.06615,
    reactance = 0.1303,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT7-8",
    from_bus_idx = 7,
    to_bus_idx = 8,
    resistance = 0.0,
    reactance = 0.1761,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT7-9",
    from_bus_idx = 7,
    to_bus_idx = 9,
    resistance = 0.0,
    reactance = 0.11,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT9-10",
    from_bus_idx = 9,
    to_bus_idx = 10,
    resistance = 0.03181,
    reactance = 0.0845,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT9-14",
    from_bus_idx = 9,
    to_bus_idx = 14,
    resistance = 0.12711,
    reactance = 0.2704,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT10-11",
    from_bus_idx = 10,
    to_bus_idx = 11,
    resistance = 0.08205,
    reactance = 0.1921,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT12-13",
    from_bus_idx = 12,
    to_bus_idx = 13,
    resistance = 0.22092,
    reactance = 0.1999,
    shunt_susceptance = 0.0,
)
PSD.add_branch!(
    system;
    name = "LT13-14",
    from_bus_idx = 13,
    to_bus_idx = 14,
    resistance = 0.17093,
    reactance = 0.348,
    shunt_susceptance = 0.0,
)

# Transformers. The tap sits on the from side, V_from / a, which is the Matpower convention of PowerSystemData
PSD.add_branch!(
    system;
    name = "TR4-7",
    from_bus_idx = 4,
    to_bus_idx = 7,
    resistance = 0.0,
    reactance = 0.2091,
    tap_ratio = 0.978,
    is_transformer = true,
)
PSD.add_branch!(
    system;
    name = "TR4-9",
    from_bus_idx = 4,
    to_bus_idx = 9,
    resistance = 0.0,
    reactance = 0.5562,
    tap_ratio = 0.969,
    is_transformer = true,
)
PSD.add_branch!(
    system;
    name = "TR5-6",
    from_bus_idx = 5,
    to_bus_idx = 6,
    resistance = 0.0,
    reactance = 0.252,
    tap_ratio = 0.932,
    is_transformer = true,
)

# Generators. The active power of the slack generator and the reactive power of every generator are results of
# the power flow, so they are not given
PSD.add_generator!(system; name = "UG1", bus_idx = 1, voltage_setpoint = 1.0)
PSD.add_generator!(system; name = "UG2", bus_idx = 2, active_power = 0.40, voltage_setpoint = 1.0)
PSD.add_generator!(system; name = "UG3", bus_idx = 3, active_power = 0.0, voltage_setpoint = 1.0)
PSD.add_generator!(system; name = "UG6", bus_idx = 6, active_power = 0.0, voltage_setpoint = 1.0)
PSD.add_generator!(system; name = "UG8", bus_idx = 8, active_power = 0.0, voltage_setpoint = 1.0)

# Loads
PSD.add_load!(system; name = "CR2", bus_idx = 2, active_power = 0.217, reactive_power = 0.127)
PSD.add_load!(system; name = "CR3", bus_idx = 3, active_power = 0.942, reactive_power = 0.19)
PSD.add_load!(system; name = "CR4", bus_idx = 4, active_power = 0.478, reactive_power = 0.039)
PSD.add_load!(system; name = "CR5", bus_idx = 5, active_power = 0.076, reactive_power = 0.016)
PSD.add_load!(system; name = "CR6", bus_idx = 6, active_power = 0.30, reactive_power = 0.30)
PSD.add_load!(system; name = "CR9", bus_idx = 9, active_power = 0.295, reactive_power = 0.166)
PSD.add_load!(system; name = "CR10", bus_idx = 10, active_power = 0.09, reactive_power = 0.058)
PSD.add_load!(system; name = "CR11", bus_idx = 11, active_power = 0.035, reactive_power = 0.018)
PSD.add_load!(system; name = "CR12", bus_idx = 12, active_power = 0.061, reactive_power = 0.016)
PSD.add_load!(system; name = "CR13", bus_idx = 13, active_power = 0.135, reactive_power = 0.058)
PSD.add_load!(system; name = "CR14", bus_idx = 14, active_power = 0.149, reactive_power = 0.05)

solution = PowerFlow.run_acpf(system)
# the standard power flow is solved with NonlinearSolve.jl, so the status is its return code
if Symbol(solution.termination_status) != :Success
    error("The power flow did not converge, the solver returned $(solution.termination_status).")
end
generation = PowerSystemExperiments.generator_powers(system, solution)

nothing
