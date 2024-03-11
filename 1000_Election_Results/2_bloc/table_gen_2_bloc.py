import pandas as pd
import json
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os 
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap

# light_cornflower = np.array([213, 237, 255]) / 255.0  # Light shade for the start
# light_cornflower = np.array([255, 255, 255]) / 255.0  # Light shade for the start
# cornflower_blue = np.array([0, 58, 129]) / 255.0  # Cornflower blue for the end
# cornflower_cmap = LinearSegmentedColormap.from_list("cornflower_blue_grad", [[1,1,1], [carn)

# light_orange = np.array([255,255,255]) / 255.0  # Dark shade for the start
# dark_orange = np.array([235,161,46]) / 255.0  # Dark shade for the start
# orange_map = LinearSegmentedColormap.from_list("orange_grad", [[1,1,1], dark_orange])

def parse_multiple_json_objects(file_content):
    decoder = json.JSONDecoder()
    pos = 0
    content_length = len(file_content)
    json_objects = []

    while pos < content_length:
        obj, next_pos = decoder.raw_decode(file_content, pos)
        json_objects.append(obj)
        pos = next_pos
        # Skip whitespace between JSON objects (if any)
        while pos < content_length and file_content[pos].isspace():
            pos += 1
    
    return json_objects



def make_dataframe_from_file(file_name, cand_type):
    with open(file_name, 'r') as file:
        file_content = file.read()

    json_objects = parse_multiple_json_objects(file_content)


    for i, obj in enumerate(json_objects):
        json_objects[i] = obj["params"]

    json_objects = sorted(json_objects, key=lambda x: 
        (
            x["candidates"]["POC"],
            x["candidates"]["W"],
        )    
    )
    
    
    df_trie = {}

    for obj in json_objects:
        cand_tuple = (obj["candidates"]["POC"], obj["candidates"]["W"])
        coh_tuple = (
            (obj["cohesion"]["C"]["C"], obj["cohesion"]["C"]["W"]),
            (obj["cohesion"]["W"]["C"], obj["cohesion"]["W"]["W"]),
        )
        df_trie[cand_tuple] = df_trie.get(cand_tuple, {})
        df_trie[cand_tuple][coh_tuple] = np.mean(obj["results"][cand_type])

    df_rows = list(df_trie.keys())
    df_columns = [
        ((0.8, 0.2), (0.1, 0.9)), # Race Predominant
        ((0.6, 0.4), (0.25, 0.75)), # Race & Ideology
        ((0.6, 0.4), (0.4, 0.6)), # Low Polarization
        # ((0.45, 0.45, 0.1), (0.45, 0.45, 0.1), (0.1, 0.1, 0.8)), # Ideology Predominant
        ((0.8, 0.2), (0.4, 0.6)), # WP Prefer POC
        ((0.8, 0.2), (0.3, 0.7)), # Race & Ideology w/ Strong POC Lean
        ((0.6, 0.4), (0.3, 0.7)), # POC Cross, WP Maj. Cross
        # ((0.8, 0.1, 0.1), (0.1, 0.8, 0.1), (0.1, 0.1, 0.8)), # Strong Bloc Cohesion
    ]       
        
    df_lst = []
    for row in df_rows:
        df_lst.append([df_trie[row][col] for col in df_columns])
        
    return pd.DataFrame(df_lst, index=df_rows, columns=df_columns)

    
def plot_table(
    df, 
    cand_type,
    zone,
    colors,
    min_val,
    max_val,
    exclude_text=False
):
    new_labels = [
        "POC: {}\nW: {}\n".format(*coh)
        for coh in df.columns
    ]

    if exclude_text:
        plt.figure(figsize=(13, 7.5))
    else:
        plt.figure(figsize=(16, 10))
    ax = sns.heatmap(
        df,
        annot=True,
        fmt=".3f",
        cmap=colors,
        cbar=False,
        annot_kws={"size": 18},
        vmin=min_val,
        vmax=max_val
    )

    # Horizontal lines
    for i in range(df.shape[0]):
        ax.hlines(i, *ax.get_xlim(), color='white', linewidth=0.5)
    # Vertical lines
    for i in range(df.shape[1]):
        ax.vlines(i, *ax.get_ylim(), color='white', linewidth=0.5)
   
    
    plot_title = f"table_2_bloc_{cand_type}_wins_in_{'_'.join(zone.split())}_Portland"

    if exclude_text:
        ax.set_xticks([])
        ax.set_yticks([])

        plt.tight_layout(pad=0)
        plt.savefig(f"./tables/{plot_title}_unlabeled.png")

        return

    ax.set_xticklabels(new_labels, rotation=0, fontsize=12)
    ax.set_yticklabels(ax.get_ymajorticklabels(), fontsize = 16, rotation=0)
    ax.xaxis.tick_top()  # Move x-axis ticks to the top
    ax.xaxis.set_label_position('top')  # Move the x-axis label to the top as well

    # Example additional text to add above each x-axis label
    additional_texts = [
        'A:\nRace Predominant', 
        'B:\nRace & Ideology', 
        'C:\nLow Polarization', 
        # 'D:\nIdeology Predominant',
        'E:\nWP Prefer POC',
        'F:\nRace & Ideology\nw/Strong POC Lean',
        'G:\nPOC Cross,\nWP Maj. Cross',
        # 'H:\nStrong Bloc\nCohesion'
    ]

    for i, text in enumerate(additional_texts):
        ax.text(
            i+0.5,
            1.11,
            text,
            va='bottom',
            ha='center',
            fontsize=12,
            fontweight="bold",
            transform=ax.get_xaxis_transform(),
            rotation=0
        )


    # Set the position for the arrow
    x_position = -0.08
    y_position = 0.5
    arrow_length = 0.96

    # Create the arrow patch
    arrow = FancyArrowPatch((x_position, y_position + arrow_length / 2), 
                            (x_position, y_position - arrow_length / 2),
                            arrowstyle='<|-|>', mutation_scale=20,
                            color='black', lw=1, clip_on=False, transform=ax.transAxes)

    ax.add_patch(arrow)
    ax.text(x_position, y_position + arrow_length / 2 + 0.01, 'Few POC\nPref Cand.', 
            ha='center', va='bottom', transform=ax.transAxes, fontsize=12)
    ax.text(x_position, y_position - arrow_length / 2 - 0.01, 'Many POC\nPref Cand.', 
            ha='center', va='top', transform=ax.transAxes, fontsize=12)
    

    # Make layout a bit nicer
    plt.tight_layout(pad=1.5)
    plt.subplots_adjust(left=0.12, right=0.98) 

    plt.savefig(f"./tables/{plot_title}_labeled.png")
    
if __name__ == "__main__":
    color_dict = {
        "C": "Greens",
        "W": "Purples",
    }
    
    for cand_type in ["C"]:
        df1 = make_dataframe_from_file("zone1_1000_results_2bloc.json", cand_type)     
        df2 = make_dataframe_from_file("zone2_1000_results_2bloc.json", cand_type)
        df3 = make_dataframe_from_file("zone3_1000_results_2bloc.json", cand_type)
        df4 = make_dataframe_from_file("zone4_1000_results_2bloc.json", cand_type)
        
        df_all = (df1 + df2 + df3 + df4)
        
        plot_table(df1, cand_type, "Zone 1", color_dict[cand_type], 0, 3)
        plot_table(df2, cand_type, "Zone 2", color_dict[cand_type], 0, 3)
        plot_table(df3, cand_type, "Zone 3", color_dict[cand_type], 0, 3)
        plot_table(df4, cand_type, "Zone 4", color_dict[cand_type], 0, 3)
        plot_table(df_all, cand_type, "All Zones", color_dict[cand_type], 0, 12)
        
        plot_table(df1, cand_type, "Zone 1", color_dict[cand_type], 0, 3, True)
        plot_table(df2, cand_type, "Zone 2", color_dict[cand_type], 0, 3, True)
        plot_table(df3, cand_type, "Zone 3", color_dict[cand_type], 0, 3, True)
        plot_table(df4, cand_type, "Zone 4", color_dict[cand_type], 0, 3, True)
        plot_table(df_all, cand_type, "All Zones", color_dict[cand_type], 0, 12, True)
        
       