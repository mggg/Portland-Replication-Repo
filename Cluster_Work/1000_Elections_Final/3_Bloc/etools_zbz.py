from votekit.elections import STV, fractional_transfer
from votekit import CambridgeSampler
import random
from votekit.graphs import PairwiseComparisonGraph
import numpy as np
import votekit.ballot_generator as bg
from votekit.ballot_generator import SlatePreference
import json
import os

ballot_generators = {
    #"bt": BradleyTerry,
    #"pl": PlackettLuce,
    #"cs": CambridgeSampler,
    "sp": SlatePreference
}

# WP = White progressive preferred candidates
# WM = White moderate preferred candidates
# WM = POC preferred candidates
candidates_to_select = {
    "WP": ["WP1", "WP2", "WP3", "WP4", "WP5", "WP6", "WP7", "WP8", "WP9", "WP10"],
    "WM": ["WM1", "WM2", "WM3", "WM4", "WM5", "WM6", "WM7", "WM8", "WM9", "WM10"],
    "C": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"],
}

def simulate_ensembles(
    cohesion: dict,
    seats: int,
    num_elections: int,
    alphas: dict,
    candidates: list,
    num_ballots: int = 1000,
    low_turnout: bool = False,
    alternate_slate: callable = None,
    
):
    """
    Runs simulation of RCV elections of an ensemble of plans
    """
    
    plan_results = []
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)

    # Portland blocks and coorsponding VAP for each group (POC, White progressive, White moderate)
    # Numbers calculated though analysis of Portland's voterfile
    zone_shares = {1: {"C": 0.38, "WP": 0.43, "WM": 0.19},
            2: {"C": 0.26, "WP": 0.68, "WM": 0.06},
            3: {"C": 0.20, "WP": 0.73, "WM": 0.07},
            4: {"C": 0.17, "WP": 0.73, "WM": 0.10}}

    for zone, shares in zone_shares.items():
        total_share = sum(shares.values())
        if total_share != 1:
            print(f"Zone {zone} sum is {total_share}, which does not equal 1.")

    # Interate across the 4 Portland blocks
    for zn in zone_shares.keys():
        assert set(zone_shares.keys()) == {1, 2, 3, 4}, "Unexpected zones in zone_shares"
        print('zone', zn)
        zone_data = {}
        zone_data["zone"] = zn
        # build hyperparams base on share and other toggles
        # based on the voter file
        blocs = zone_shares[zn]
        print (zn, blocs)
        cand_slate = {
            "WP": candidates_to_select["WP"][:candidates[1]],  
            "WM": candidates_to_select["WM"][:candidates[2]],  
            "C": candidates_to_select["C"][:candidates[0]],   
        }

        # Loop through number of simulated RCV elections
        for _ in range(num_elections):
            for model_name, model in ballot_generators.items():
                data = {
                    'bloc_voter_prop': blocs,
                    'cohesion_parameters': cohesion,
                    'alphas': alphas,
                    'slate_to_candidates':cand_slate
                }

                generator = model.from_params(**data)
                #print("Preference Intervals:", generator.pref_intervals_by_bloc)

                ballots = generator.generate_profile(num_ballots)
                #ballots.to_csv(current_dir + '/ballots.csv')

                # Run 3 bloc election
                results = STV(
                    ballots,
                    transfer=fractional_transfer,
                    seats=seats,
                    quota = "droop", # Added from chris' code
                    ballot_ties=False,
                    tiebreak = "random", # Added from chris' code
                ).run_election()

                # Determine the number of winners for each bloc
                num_winners_c = count_winners(results.winners(), "C")
                num_winners_wp = count_winners(results.winners(), "WP")
                num_winners_wm = count_winners(results.winners(), "WM")

                if model_name not in zone_data:
                    zone_data[model_name] = {}
                    zone_data[model_name]["C"] = []
                    zone_data[model_name]["WP"] = []
                    zone_data[model_name]["WM"] = []

                zone_data[model_name]["C"].append(num_winners_c)
                zone_data[model_name]["WP"].append(num_winners_wp)
                zone_data[model_name]["WM"].append(num_winners_wm)

        plan_results.append(zone_data)

    # Have results be reflected on a city-wide level
    condensed = condense_results(plan_results)

    print(f"Plan Results {zn}", plan_results)
    print("Results across zones", condensed)

    return(plan_results), condensed
    

def condense_results_single_cand (plan_results):
    """Condenses the 4-zone election results to city level for a single candidate"""
    election_results = {}
    
    for election_type in ballot_generators:
        summed_zone_results = []
        for item in plan_results:
            zone = item['zone']
            win_list = item[election_type]

            if len(summed_zone_results) == 0:
                summed_zone_results = win_list
            else: 
                summed_zone_results = np.add(summed_zone_results, win_list)
        election_results[election_type] = summed_zone_results
        #print("TO SEE")
        #print(election_results[election_type])

    return election_results

def condense_results(plan_results):
    """Condenses the 4-zone election results to city level"""
    election_results = {}
    
    for election_type in ballot_generators:
        summed_zone_results = {'C': [], 'WP': [], 'WM':[]}
        for item in plan_results:
            zone = item['zone']

            for cand_type in item[election_type]:
                win_list = item[election_type][cand_type]

                if len(summed_zone_results[cand_type]) == 0:
                    summed_zone_results[cand_type] = win_list
                    
                else: 
                    summed_zone_results[cand_type] = np.add(summed_zone_results[cand_type], win_list)

        election_results[election_type] = summed_zone_results

    return election_results


def count_winners(elected: list[set], party: str) -> int:
    """
    Counts number of elected candidates from the inputted party.
    """
    winner_count = 0

    for winner_set in elected:
        for cand in winner_set:
            if cand[0] == party or cand[0:2] == party: # allows for 'C' or 'WP'
                winner_count += 1

    return winner_count

def convert_tuples_in_keys(obj):
    """Recursively convert tuples in dictionary keys to strings."""
    if isinstance(obj, dict):
        return {str(key): convert_tuples_in_keys(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_tuples_in_keys(element) for element in obj]
    elif isinstance(obj, tuple):
        return str(obj) 
    else:
        return obj 


def slate_by_share(vote_share: float) -> dict:
    pass
