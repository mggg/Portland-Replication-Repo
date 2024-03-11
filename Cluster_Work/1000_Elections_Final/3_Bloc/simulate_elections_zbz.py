import matplotlib.pyplot as plt
import numpy as np
import os 
from etools_zbz import simulate_ensembles
import json
import random
import os
import argparse
import re


ballot_generators = {
    "sp": "Slate Preference"
}

def simulate_elections(candidates, alpha_poc_params, alpha_wp_params, alpha_wm_params, 
                        cohesion_poc_params, cohesion_white_progressive_params, 
                        cohesion_white_conservative_params, num_elections):

    candidates_poc = candidates[0]
    candidates_wp = candidates[1]
    candidates_wm = candidates[2]

    alpha_poc_1 = alpha_poc_params[0]
    alpha_poc_2 = alpha_poc_params[1]
    alpha_poc_3 = alpha_poc_params[2]

    alpha_wp_1 = alpha_wp_params[0]
    alpha_wp_2 = alpha_wp_params[1]
    alpha_wp_3 = alpha_wp_params[2]

    alpha_wm_1 = alpha_wm_params[0]
    alpha_wm_2 = alpha_wm_params[1]
    alpha_wm_3 = alpha_wm_params[2]

    coh_poc_1 = cohesion_poc_params[0]
    coh_poc_2 = cohesion_poc_params[1]
    coh_poc_3 = cohesion_poc_params[2]

    coh_wp_1 = cohesion_white_progressive_params[0]
    coh_wp_2 = cohesion_white_progressive_params[1]
    coh_wp_3 = cohesion_white_progressive_params[2]

    coh_wm_1 = cohesion_white_conservative_params[0]
    coh_wm_2 = cohesion_white_conservative_params[1]
    coh_wm_3 = cohesion_white_conservative_params[2]

    alphas = {"C": {"C": alpha_poc_1, "WP": alpha_poc_2, "WM": alpha_poc_3},
            "WP": {"C": alpha_wp_1, "WP": alpha_wp_2, "WM": alpha_wp_3},
            "WM": {"C": alpha_wm_1, "WP": alpha_wm_2, "WM": alpha_wm_3}}
    cohesion = {"C": {"C": coh_poc_1, "WP": coh_poc_2, "WM": coh_poc_3},
            "WP": {"C": coh_wp_1, "WP": coh_wp_2, "WM": coh_wp_3},
            "WM": {"C": coh_wm_1, "WP": coh_wm_2, "WM": coh_wm_3}}

    basic_start = simulate_ensembles(
        cohesion=cohesion, 
        seats=3,
        num_elections=num_elections,
        alphas=alphas,
        candidates=candidates
    )

    basic_start_zone_data, aggregated_data = basic_start
    # iterate across each zones
    cand_types = ['C', 'WP', 'WM']
    cand_long = {'C':'POC Preferred', 'WP':'White Progressive Preferred', 'WM':'White Moderate Preferred'}
    cand_color = {'C':'skyblue', 'WP':'lightgreen', 'WM':'lightcoral'}
    print('basic_start_zone_data',basic_start_zone_data)
    for zone_data in basic_start_zone_data:
        print('hist zone', zone_data)
        curr_zone = zone_data['zone']
        print('hist curr zone', curr_zone)
        results = zone_data['sp']
        print('hist results', results)

        for curr_cand in cand_types:
            # Update the params string to accurately reflect simulation setup
            params = (
                f"MODEL PARAMETERS\n"
                f"\n"
                f"Zone: {curr_zone}\n"
                f"Number of POC candidates: {candidates_poc}\n"
                f"Number of WP candidates: {candidates_wp}\n"
                f"Number of WM candidates: {candidates_wm}\n"
                "Alphas POC (POC, WP, WM): " + ", ".join(map(str, alpha_poc_params)) + "\n"
                "Alphas WP (POC, WP, WM): " + ", ".join(map(str, alpha_wp_params)) + "\n"
                "Alphas WM (POC, WP, WM): " + ", ".join(map(str, alpha_wm_params)) + "\n"
                "Cohesion POC (POC, WP, WM): " + ", ".join(map(str, cohesion_poc_params)) + "\n"
                "Cohesion WP (POC, WP, WM): " + ", ".join(map(str, cohesion_white_progressive_params)) + "\n"
                "Cohesion WM (POC, WP, WM): " + ", ".join(map(str, cohesion_white_conservative_params)) + "\n"
                f"Number of Simulated Elections: {num_elections}"
            )
        
            election_results = {
                "params": {
                    "zone": curr_zone,
                    "candidate_type": curr_cand,
                    "num_elections": num_elections,
                    "alphas": alphas,
                    "cohesion": cohesion,
                    "candidates": {
                        "POC": candidates_poc,
                        "WP": candidates_wp,
                        "WM": candidates_wm,
                    },
                "results": results
                }
            }

            # Define filename for JSON output based on zone and number of elections
            json_filename = f'zone_{curr_zone}_{curr_cand}_{num_elections}_elections_results.json'
            output_directory = os.path.join(os.getcwd(), 'Results')
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            json_output_path = os.path.join(output_directory, json_filename)

            with open(json_output_path, 'a') as json_file:
                json.dump(election_results, json_file, indent=4)

            # Construct a string to describe the simulation type, should be done outside the 'with open' block
            simulation_type = (
                f'{curr_cand}candType_{candidates_poc}C_{candidates_wp}WP_{candidates_wm}WM_'
                f'{alphas["C"]["C"]}aCC_{alphas["C"]["WP"]}aCWP_{alphas["C"]["WM"]}aCWM_'
                f'{coh_poc_1}cohC_{coh_wp_1}cohWP_{coh_wm_1}cohWM_'
                f'{num_elections}sims'
            )

            generate_histogram(
                data=zone_data['sp'][curr_cand],  
                cand_type=cand_long[curr_cand],
                election_type='sp', 
                simulation_type=simulation_type, 
                params=params,  
                num_elections=num_elections,  
                curr_zone=curr_zone, 
                num_candidates_c=candidates_poc,  
                num_candidates_wp=candidates_wp, 
                num_candidates_wm=candidates_wm,
                zone=True,
                color=cand_color[curr_cand]
            )

            generate_histogram(
                data=aggregated_data['sp'][curr_cand],  
                cand_type=cand_long[curr_cand],
                election_type='sp', 
                simulation_type=simulation_type, 
                params=params,  
                num_elections=num_elections,  
                curr_zone=curr_zone, 
                num_candidates_c=candidates_poc,  
                num_candidates_wp=candidates_wp, 
                num_candidates_wm=candidates_wm,
                zone=False,
                color=cand_color[curr_cand]
            )
        


def generate_histogram(data, cand_type, election_type, simulation_type, params, num_elections, curr_zone, num_candidates_c, 
                       num_candidates_wp, num_candidates_wm, show_plot=False, zone=True, color="blue"):
    """
    Generate and save a histogram based on election data.
    """
    unique_values, counts = np.unique(data, return_counts=True)

    fig, ax = plt.subplots(figsize=(6,8), nrows=2, ncols=1)

    # Ensure that the bins on the x-axis include 0, 1, 2, and 3
    bin_edges = np.arange(-0.5, max(unique_values) + 1.5, 1)
    ax[0].hist(data, bins=bin_edges, align='mid', alpha=0.7, edgecolor='black', color=color)
    if zone:
        ax[0].set_xticks([0, 1, 2, 3])
    else:
        ax[0].set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        
    ax[0].set_ylim(0, num_elections)  # Set to the number of simulated elections
    ax[0].set_xlabel('Number of Elected ' + cand_type + ' Candidates')
    ax[0].set_ylabel('Frequency')
    ax[0].set_title(f'Histogram for {election_type.upper()} Model')
     # Display the average and parameters text
    average_value = np.mean(data)
    
    # Create an external legend box for params
    if zone:
        params = params
        ax[1].text(0.25, 0.5, params, ha='left', va='center', fontsize=8, wrap=True,
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5', alpha=1))
        # Adjust layout to accommodate the new legend box
        ax[1].set_axis_off()
        fig.subplots_adjust(bottom=0.25, top=0.95)
    else:
        pattern = 'Zone: 4'
        replacement = 'Zone: All'
        params = re.sub(pattern, replacement, params)
        ax[1].text(0.25, 0.5, params, ha='left', va='center', fontsize=8, wrap=True,
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5', alpha=1))
        # Adjust layout to accommodate the new legend box
        ax[1].set_axis_off()
        fig.subplots_adjust(bottom=0.25, top=0.95)

    ax[1].text(0.5, 0.95, f'Average Number of Elected {cand_type} Candidates: {average_value:.2f}', ha="center", fontsize=8)

    if zone:
        folder_name = f'{election_type}_Zone_{curr_zone}_Histograms'
    else:
        folder_name = f'{election_type}_Aggregate_Histograms'
    output_directory = os.path.join(os.getcwd(), 'Histograms', folder_name)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_path = os.path.join(output_directory, f'{simulation_type}_histogram.png')
    plt.savefig(output_path, bbox_inches="tight")
    if show_plot:
        plt.show()
    plt.close()

def parse_args():
    parser = argparse.ArgumentParser(description='Run election simulations.')
    parser.add_argument("--candidates", type=str, help="Number of candidates in order POC, WP, WM")
    parser.add_argument("--alpha_poc_params", type=str, help="Alpha parameters for POC candidates")
    parser.add_argument("--alpha_wp_params", type=str, help="Alpha parameters for white progressive candidates")
    parser.add_argument("--alpha_wm_params", type=str, help="Alpha parameters for white conservative candidates")
    parser.add_argument("--cohesion_poc_params", type=str, help="Cohesion parameters for POC")
    parser.add_argument("--cohesion_white_progressive_params", type=str, help="Cohesion parameters for white progressives")
    parser.add_argument("--cohesion_white_conservative_params", type=str, help="Cohesion parameters for white conservatives")
    parser.add_argument("--num_elections", type=int, help="Number of elections to simulate")

    return parser.parse_args()

def main():
    args = parse_args()
    
    candidates = [int(i) for i in args.candidates.split(' ')]
    alpha_poc_params = [float(i) for i in args.alpha_poc_params.split(' ')]
    alpha_wp_params = [float(i) for i in args.alpha_wp_params.split(' ')]
    alpha_wm_params = [float(i) for i in args.alpha_wm_params.split(' ')]
    cohesion_poc_params = [float(i) for i in args.cohesion_poc_params.split(' ')]
    cohesion_white_progressive_params = [float(i) for i in args.cohesion_white_progressive_params.split(' ')]
    cohesion_white_conservative_params= [float(i) for i in args.cohesion_white_conservative_params.split(' ')]

    simulate_elections(
        candidates = candidates,
        alpha_poc_params=alpha_poc_params,
        alpha_wp_params=alpha_wp_params,
        alpha_wm_params=alpha_wm_params,
        cohesion_poc_params=cohesion_poc_params,
        cohesion_white_progressive_params=cohesion_white_progressive_params,
        cohesion_white_conservative_params=cohesion_white_conservative_params,
        num_elections=args.num_elections
    )

if __name__ == "__main__":
    main()
