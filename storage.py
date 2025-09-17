def simulate_battery(demand, generation, capacity=100, initial=50):
    soc = initial
    soc_list = []

    for d, g in zip(demand, generation):
        net = g - d
        soc += net
        soc = max(0, min(soc, capacity))  # Clamp between 0 and capacity
        soc_list.append(soc)

    return soc_list
