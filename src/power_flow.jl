# Complex power delivered by each generator, which is the power injected into the network at its bus plus the
# power of the loads of the bus. The generator powers of the solution are not used because PowerFlow.jl returns
# the scheduled active power for the slack generator, not the one that closes the balance
function generator_powers(system::PSD.Input, solution::PF.ACSolution)
    Ybus = PSD.ybus(system)
    bus_generation = PSD.power_injection(solution.voltage, solution.voltage_angle, Ybus)
    for load_idx in 1:PSD.num_loads(system)
        bus_idx = PSD.load_bus_idx(system, load_idx)
        P = PSD.load_active_power(system, load_idx)
        Q = PSD.load_reactive_power(system, load_idx)
        bus_generation[bus_idx] += P + im * Q
    end

    # with a single generator per bus, the generation of the bus is the power of its generator
    powers = zeros(ComplexF64, PSD.num_generators(system))
    generators_per_bus = zeros(Int, PSD.num_buses(system))
    for gen_idx in 1:PSD.num_generators(system)
        bus_idx = PSD.generator_bus_idx(system, gen_idx)
        generators_per_bus[bus_idx] += 1
        if generators_per_bus[bus_idx] > 1
            error("Bus $bus_idx has more than one generator, so its generation cannot be split among them.")
        end
        powers[gen_idx] = bus_generation[bus_idx]
    end
    return powers
end
