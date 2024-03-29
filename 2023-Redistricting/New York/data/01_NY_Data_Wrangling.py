import matplotlib.pyplot as plt
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.proposals import recom
from functools import partial
import pandas
from gerrychain.tree import recursive_tree_part

from gerrychain.metrics import efficiency_gap, mean_median

import geopandas as gpd

import os

from gerrychain.constraints.contiguity import contiguous_components, contiguous

import numpy as np


g = Graph.from_json("./Downloads/MAUP Code/Precinct_Graph_connected_CON.json")


df = gpd.read_file("./Downloads/MAUP Code/Processed_Precincts.shp")


df = df.drop(407)


df.plot(column='CON',cmap='tab20')


len(df['CON'].unique())


sorted(df['CON'].unique())

df.groupby('CON')["Population"].sum()

df.columns

elections = [
    Election("G20PRE", {"Democratic": "G20PREDBID", "Republican": "G20PRERTRU"}),

]

for node in g.nodes():
    if g.nodes[node]['Population'] ==g.nodes[node]['Population']:
        g.nodes[node]['population'] = g.nodes[node]['Population']
    else:
        g.nodes[node]['population'] = 0
        
        

my_updaters = {"population": updaters.Tally("population", alias="population")}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)

initial_partition = GeographicPartition(g, assignment="CON", updaters=my_updaters)

contiguous(initial_partition)

plt.plot(sorted(initial_partition['G20PRE'].percents('Republican')),'r*')
plt.axhline(.5,color='green',label= '50 %')
plt.axhline(.45,color='yellow', label='45 %')
plt.axhline(.6,color='blue',label='60%')

plt.axhline(.4134,color='red',label='Statewide Average')
plt.xlabel('Sorted District Index')
plt.ylabel('Republican Vote Percentage')
plt.title('President 2020 Vote Data')

plt.legend()


initial_partition['population']


df.groupby("CON")["Population"].sum()


ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)

# We use functools.partial to bind the extra parameters (pop_col, pop_target, epsilon, node_repeats)
# of the recom proposal.
proposal = partial(recom,
                   pop_col="population",
                   pop_target=ideal_population,
                   epsilon=0.02,
                   node_repeats=2
                  )



compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]),
    2*len(initial_partition["cut_edges"])
)

pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.05)


chain = MarkovChain(
    proposal=proposal,
    constraints=[
        pop_constraint,
        compactness_bound
    ],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=10
)


egs = []
mms = []
for partition in chain:
    egs.append(efficiency_gap(partition['G20PRE']))
    mms.append(mean_median(partition['G20PRE']))
    
    df['Current_assignment'] = df.index.map(dict(partition.assignment))
    df.plot(column='Current_assignment',cmap='tab20')
    plt.axis('off')
    plt.show()


plt.hist(egs)


chain2 = MarkovChain(
    proposal=proposal,
    constraints=[
        pop_constraint,
        compactness_bound
    ],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=100
)


newpath = './NY_First_Plots'
if not os.path.exists(newpath):
    os.makedirs(newpath)

egs = []
mms = []
t=0
s=0
plt.close()
for partition in chain2:
    
    egs.append(efficiency_gap(partition['G20PRE']))
    mms.append(mean_median(partition['G20PRE']))
    
    
    if t % 1 ==0:
        print(t)
    
        df['Current_assignment'] = df.index.map(dict(partition.assignment))
        df.plot(column='Current_assignment',cmap='tab20')
        plt.axis('off')
        if egs[-1] <0:
            plt.title(f'Efficiency Gap: {egs[-1]:.4f}',color='red')
        else:
            plt.title(f'Efficiency Gap: {egs[-1]:.4f}',color='blue')
        #plt.show()
        plt.savefig(f'{newpath}/step_{s:03d}.png')
        s+=1


        plt.close()
    
    t+=1

