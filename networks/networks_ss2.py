"""
Starsim Networks
"""

# %% Imports and settings
import sciris as sc
import numpy as np
import starsim as ss
import scipy.stats as sps
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import networkx as nx

small =  100
medium = 1000
large =  10_000

# %% Define the scripts

def manual_net():
    sc.heading('1.- Manual networks')

    # Make completely abstract layers
    n_edges = 10_000
    n_agents = medium
    p1 = np.random.randint(n_agents, size=n_edges)
    p2 = np.random.randint(n_agents, size=n_edges)
    beta = np.ones(n_edges)
    network_01 = ss.Network(p1=p1, p2=p2, beta=beta, label='rand')

    # Create a maternal network
    sim = ss.Sim(n_agents=n_agents)
    sim.init()
    network_02 = ss.MaternalNet()
    network_02.init_pre(sim)
    network_02.add_pairs(mother_inds=[1, 2, 3], unborn_inds=[100, 101, 102], dur=[1, 1, 1])
    
    # Tidy
    o = sc.objdict(network_01=network_01, network_02=network_02)
    return o


def random_net():
    sc.heading('1.- Random networks')

    # Manual creation
    network_01 = ss.RandomNet()
    ss.Sim(n_agents=small, networks=network_01, copy_inputs=False).init() # This initializes the network
    
    # Automatic creation as part of sim
    simulation_02 = ss.Sim(n_agents=small, networks='random').init()
    network_02 = simulation_02.networks[0]
    
    # Increase the number of contacts
    nwdict = dict(type='random', n_contacts=20)
    s3 = ss.Sim(n_agents=small, networks=nwdict).init()
    nw3 = s3.networks[0]
    
    # Checks
    assert np.array_equal(network_01.p2, network_02.p2), 'Implicit and explicit creation should give the same network'
    assert len(nw3) == len(network_02)*2, 'Doubling n_contacts should produce twice as many contacts'
    
    # Tidy
    o = sc.objdict(network_01=network_01, network_02=network_02, nw3=nw3)
    return o

def plot_erdosrenyi_graph(G, title, node_size=50, show_labels=True, option=1):
    plt.figure(figsize=(10, 10))  # Adjust figure size for larger graphs
    if option == 1:
        # Draw the graph with a spring layout (useful for small to medium networks)
        pos = nx.spring_layout(G)  # Positions for all nodes
        nx.draw(G, pos, with_labels=show_labels, node_size=node_size, node_color="lightblue", font_size=10, font_color="black", edge_color="gray")
        plt.title(f" spring -layout {title}", fontsize=16) 
    if option == 2:
        # Use a more efficient layout for large networks (e.g., Kamada-Kawai or Fruchterman-Reingold)
        pos = nx.kamada_kawai_layout(G)  # You can switch to nx.spring_layout(G) or nx.fruchterman_reingold_layout(G)
        # Draw the graph
        nx.draw(G, pos, node_size=node_size, node_color="orange", edge_color="gray", alpha=0.6, with_labels=show_labels)
        plt.title(f" kamada_kawai-layout {title}", fontsize=16) 
    plt.show()
    # Optionally draw the degree histogram
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # Degree sequence
    plt.figure()
    plt.hist(degree_sequence, bins='auto', color='blue', alpha=0.7)
    plt.title(f"Degree Histogram {title}")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    
    plt.show()

def erdosrenyi_net():
    sc.heading('1.- Erdos-Renyi network')

    def ER_Net(n, p, nw, alpha=0.01):
        p12 = np.concatenate([nw.edges['p1'], nw.edges['p2']])  # p1 and p2 are the UIDs of agents, used here to determine degree
        upper = sps.binom.ppf(n=n-1, p=p, q=0.999)  # Figure out the 99.9th percentile expected upper bound on the degree
        bins = np.arange(upper+1)  # Create bins
        counts = np.histogram(p12, bins=np.arange(n+1))[0]  # Count how many times each agent is connected
        f_obs = np.histogram(counts, bins=bins)[0]  # Form the degree distribution
        pp = sps.binom.pmf(bins[:-1], n=n, p=p)  # Computed the theoretical probability distribution
        
        f_exp = f_obs.sum() * pp / pp.sum()  # Scale

        # Filter out zero expected frequencies to avoid division by zero
        nonzero = f_exp > 0
        f_obs_nonzero = f_obs[nonzero]
        f_exp_nonzero = f_exp[nonzero]

        # Compute the chi-squared test on non-zero expected frequencies
        p_value = sps.chisquare(f_obs_nonzero, f_exp_nonzero).pvalue  # Compute the X2 p-value
        
        return p_value

    # Manual creation
    p = 0.1
    network_01 = ss.ErdosRenyiNet(p=p)
    ss.Sim(n_agents=40, networks=network_01, copy_inputs=False).init() # This initializes the network
    ER_Net(40, p, network_01)
    G = network_01.to_graph()
    plot_erdosrenyi_graph(G, "Erdos-Renyi Network 01")

    # Automatic creation as part of sim
    simulation_02 = ss.Sim(n_agents=small, networks='erdosrenyi').init()
    network_02 = simulation_02.networks[0]
    G = network_02.to_graph()
    plot_erdosrenyi_graph(G, "Erdos-Renyi Network 02", option=2)
    
    
    # Larger example with higher p
    p=0.6
    nwdict = dict(type='erdosrenyi', p=p)
    s3 = ss.Sim(n_agents=medium, networks=nwdict).init()
    nw3 = s3.networks[0]
    ER_Net(medium, p, nw3)
    
    # Tidy
    o = sc.objdict(network_01=network_01, network_02=network_02, nw3=nw3)
    return o


def disk_net():
    sc.heading('1.- Disk Network - without disease')
    # Visualize the path of agents

    network_01 = ss.DiskNet()
    simulation_01 = ss.Sim(n_agents=20, 
                             dur=50,
                             networks=network_01, 
                             copy_inputs=False).init()  # This initializes the network

    # Initial agent positions are displayed as scatter points.
    # A loop runs for each simulation year, plotting the movement of agents using ax.quiver(), 
    # which draws arrows representing velocity vectors.
    # The positions are updated by s1.step(), which progresses the simulation one step forward.
    
    if sc.options.interactive:
        fig, ax = plt.subplots()
        print("Disknet velocity:", network_01.pars.v)
        print("Simulation dt:", simulation_01.pars.dt)
        
        velocity = network_01.pars.v * simulation_01.pars.dt

        cmap = mpl.colormaps['viridis']
        colors = cmap(np.linspace(0, 1, simulation_01.pars.n_agents))

        for i in range(simulation_01.pars.dur):
            ax.clear()  # Clear the previous plot -- Comment to see the path of agents <--------------------------------
            ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], 'k-', lw=1)  # Boundary and agent positions
            
            ax.scatter(network_01.x, network_01.y, s=40, c=colors)
            
            
            ax.quiver(network_01.x, 
                      network_01.y, 
                      velocity * np.cos(network_01.theta), 
                      velocity * np.sin(network_01.theta), 
                      color=colors)
            ax.set_aspect('equal', adjustable='box')
            ax.title.set_text(f'Year: {i + 1}')  
            simulation_01.run_one_step()  # Run the simulation for one step
            plt.pause(0.1)  
        plt.show()  # Show the final plot after the loop
        simulation_01.plot().suptitle('1.- Disk Network without disease')
        
        # Now we add a disease to the simulation, and the states will also be added to the plot
        simulation_01.disease = ss.SIR(pars=dict(dur_inf=10, beta=0.1)).init_pre(simulation_01)
        
        simulation_01.plot().suptitle('1.- Disk Network with SIR disease')
        
    return simulation_01


def disk_net2():    
    sc.heading('2.- Disk Network - with SIR disease')
    # Simulate SIR on a DiskNet
    network_02 = ss.DiskNet(r=0.15, v=0.05)
    simulation_02 = ss.Sim(n_agents=small, 
                              networks=network_02, 
                              diseases='sir').init()  # This initializes the network
    simulation_02.run()

    if sc.options.interactive:
        simulation_02.plot().suptitle('2.- Disk Net with SIR disease')
        plt.show()

    return simulation_02



def static_net():
    sc.heading('1.- Static networks')
    
    # Create with p
    p = 0.2
    n = 100
    nc = p*n
    nd1 = dict(type='static', p=p)
    network_01 = ss.Sim(n_agents=n, networks=nd1).init().networks[0]
    
    # Create with n_contacts
    nd2 = dict(type='static', n_contacts=nc)
    network_02 = ss.Sim(n_agents=n, networks=nd2).init().networks[0]
    
    # Check
    assert len(network_01) == len(network_02), 'Networks should be the same length'
    target = n*n*p/2
    assert target/2 < len(network_01) < target*2, f'Network should be approximately length {target}'
    
    # Tidy
    o = sc.objdict(network_01=network_01, network_02=network_02)
    return o


def null_net():
    sc.heading('1.- NullNet...')
    people = ss.People(n_agents=small)
    network = ss.NullNet()
    sir = ss.SIR(pars=dict(dur_inf=10, beta=0.1))
    sim = ss.Sim(diseases=sir, people=people, networks=network)
    sim.run()
    return sim



# %% Run as a script
if __name__ == '__main__':
    do_plot = True
    sc.options(interactive=do_plot)
    T = sc.timer()

    # Run scripts
    # man  = manual_net()
    # rand = random_net()
    # stat = static_net()
    erdo = erdosrenyi_net()
    # disk01 = disk_net()
    # disk02 = disk_net2()
    
    plt.show()
    # null = null_net()

    T.toc()
