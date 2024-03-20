import pandas as pd
import json
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os 
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap


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
            x["candidates"]["WP"],
            x["candidates"]["WM"],
        )    
    )
    
    
    df_trie = {}

    for obj in json_objects:
        cand_tuple = (obj["candidates"]["POC"], obj["candidates"]["WP"], obj["candidates"]["WM"])
        coh_tuple = (
            (obj["cohesion"]["C"]["C"], obj["cohesion"]["C"]["WP"], obj["cohesion"]["C"]["WM"]),
            (obj["cohesion"]["WP"]["C"], obj["cohesion"]["WP"]["WP"], obj["cohesion"]["WP"]["WM"]),
            (obj["cohesion"]["WM"]["C"], obj["cohesion"]["WM"]["WP"], obj["cohesion"]["WM"]["WM"])
        )
        df_trie[cand_tuple] = df_trie.get(cand_tuple, {})
        df_trie[cand_tuple][coh_tuple] = np.array(obj["results"][cand_type])

    df_rows = list(df_trie.keys())
    df_columns = [
        ((0.8, 0.1, 0.1), (0.1, 0.45, 0.45), (0.1, 0.45, 0.45)), # Race Predominant
        ((0.6, 0.3, 0.1), (0.3, 0.6, 0.1), (0.1, 0.1, 0.8)), # Race & Ideology
        ((0.4, 0.3, 0.3), (0.3, 0.4, 0.3), (0.3, 0.3, 0.4)), # Low Polarization
        ((0.45, 0.45, 0.1), (0.45, 0.45, 0.1), (0.1, 0.1, 0.8)), # Ideology Predominant
        ((0.8, 0.1, 0.1), (0.8, 0.1, 0.1), (0.1, 0.1, 0.8)), # WP Prefer POC
        ((0.8, 0.1, 0.1), (0.3, 0.6, 0.1), (0.1, 0.05, 0.85)), # Race & Ideology w/ Strong POC Lean
        ((0.6, 0.3, 0.1), (0.45, 0.45, 0.1), (0.1, 0.05, 0.85)), # POC Cross, WP Maj. Cross
        # ((0.8, 0.1, 0.1), (0.1, 0.8, 0.1), (0.1, 0.1, 0.8)), # Strong Bloc Cohesion
    ]       
        
    df_lst = []
    for row in df_rows:
        df_lst.append([df_trie[row][col] for col in df_columns])
        
    return pd.DataFrame(df_lst, index=df_rows, columns=df_columns)

def plot_single_hist(
    df,
    column_name,
    row_name,
    min_val,
    max_val,
    ax
):
    bins = [i for i in range(min_val, max_val+1)]
    ax = sns.histplot(
        data = df[column_name][row_name], 
        bins = bins, 
    )
    


def plot_hist(
    df, 
    cand_type,
    zone,
    color,
    min_val,
    max_val,
    file_name_suffix = "",
):
    new_labels = [
        "POC: {}\nWP: {}\nWM: {}\n".format(*coh)
        for coh in df.columns
    ]


    fig, axs = plt.subplots(*df.shape, figsize=(40,30))

    rows = df.index
    columns = df.columns
    
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            bins = np.arange(min_val - 0.5, max_val + 1.5, 1)
            
            sns.histplot(
                data = df[columns[j]][rows[i]],
                bins = bins,
                ax = axs[i, j],
                color = color,
            )
            axs[i,j].set_ylim(0,1000)
            axs[i,j].set_xticks(range(min_val, max_val+1))
            axs[i,j].set_ylabel('')


    
    plot_title = f"hist_3_bloc_{cand_type}_wins_in_{'_'.join(zone.split())}_Portland"

    # Example additional text to add above each x-axis label
    additional_texts = [
        'A:\nRace\nPredominates', 
        'B:\nRace + Ideo.', 
        'C:\nLow Polarization', 
        'D:\nIdeo.\nPredominates',
        'E:\nWP Prefer POC',
        'F:\nRace + Ideo.,\nStrong POC Lean',
        'G:\nPOC Cross,\nWP Maj. Cross',
        # 'H:\nStrong Bloc\nCohesion'
    ]

    for i, text in enumerate(additional_texts):
        fig.text(
            0.07 + (i*0.91+0.5)/df.shape[1],
            0.99,
            text,
            va='top',
            ha='center',
            fontsize=28,
            fontweight="bold",
            rotation=0
        )
    
    for i, col in enumerate(columns):
        fig.text(
            0.07 + (i*0.91+0.5)/len(columns),
            0.94,
            f"POC: {col[0]}\nWP: {col[1]}\nWM: {col[2]}",
            va='top',
            ha='center',
            fontsize=24,
            rotation=0
        ) 
    
     
    for i, row in enumerate(rows):
        fig.text(
            0.045,
            0.9 - (i+0.5)*0.9/(len(rows)),
            row,
            fontsize=24,
        )


    # Set the position for the arrow
    x_position = 0.025
    y_position = 0.458
    arrow_length = 0.82

    # Create the arrow patch with figure coordinates
    arrow = FancyArrowPatch((x_position, y_position + arrow_length / 2), 
                            (x_position, y_position - arrow_length / 2),
                            arrowstyle='<|-|>', mutation_scale=20,
                            color='black', lw=5, clip_on=False, 
                            transform=fig.transFigure)  # Use figure coordinates

    # Add the arrow patch to the figure
    fig.patches.append(arrow)

    # Add text associated with the arrow using figure coordinates
    fig.text(x_position, y_position + arrow_length / 2 + 0.01, 'Few POC\nPref Cand.', 
            ha='center', va='bottom', fontsize=26, transform=fig.transFigure)
    fig.text(x_position, y_position - arrow_length / 2 - 0.01, 'Many POC\nPref Cand.', 
            ha='center', va='top', fontsize=26, transform=fig.transFigure)
    

    # Make layout a bit nicer
    plt.tight_layout(pad=1.5)
    fig.subplots_adjust(left=0.09, right=0.98) 
    fig.subplots_adjust(top=0.9)

    plt.savefig(f"./histograms/{plot_title}.png")
    plt.close()


    
def plot_hist_3(
    df, 
    cand_type,
    zone,
    color,
    min_val,
    max_val,
    file_name_suffix = "",
):
    new_labels = [
        "POC: {}\nWP: {}\nWM: {}\n".format(*coh)
        for coh in df.columns
    ]


    fig, axs = plt.subplots(*df.shape, figsize=(40,10))

    rows = df.index
    columns = df.columns
    
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            bins = np.arange(min_val - 0.5, max_val + 1.5, 1)
            
            sns.histplot(
                data = df[columns[j]][rows[i]],
                bins = bins,
                ax = axs[i, j],
                color = color,
            )
            axs[i,j].set_ylim(0,1000)
            axs[i,j].set_xticks(range(min_val, max_val+1))
            axs[i,j].set_ylabel('')


    
    plot_title = f"hist_3_bloc_{cand_type}_wins_in_{'_'.join(zone.split())}_Portland"

    # Example additional text to add above each x-axis label
    additional_texts = [
        'A:\nRace\nPredominates', 
        'B:\nRace + Ideo.', 
        'C:\nLow Polarization', 
        'D:\nIdeo.\nPredominates',
        'E:\nWP Prefer POC',
        'F:\nRace + Ideo.,\nStrong POC Lean',
        'G:\nPOC Cross,\nWP Maj. Cross',
        # 'H:\nStrong Bloc\nCohesion'
    ]

    for i, text in enumerate(additional_texts):
        fig.text(
            0.07 + (i*0.91+0.5)/df.shape[1],
            0.98,
            text,
            va='top',
            ha='center',
            fontsize=20,
            fontweight="bold",
            rotation=0
        )
    
    for i, col in enumerate(columns):
        fig.text(
            0.07 + (i*0.91+0.5)/len(columns),
            0.87,
            f"POC: {col[0]}\nWP: {col[1]}\nWM: {col[2]}",
            va='top',
            ha='center',
            fontsize=16,
            rotation=0
        ) 
    
     
    for i, row in enumerate(rows):
        fig.text(
            0.045,
            0.8 - (i+0.5)*0.8/(len(rows)),
            row,
            fontsize=24,
        )


    # Set the position for the arrow
    x_position = 0.025
    y_position = 0.458
    arrow_length = 0.70

    # Create the arrow patch with figure coordinates
    arrow = FancyArrowPatch((x_position, y_position + arrow_length / 2), 
                            (x_position, y_position - arrow_length / 2),
                            arrowstyle='<|-|>', mutation_scale=18,
                            color='black', lw=5, clip_on=False, 
                            transform=fig.transFigure)  # Use figure coordinates

    # Add the arrow patch to the figure
    fig.patches.append(arrow)

    # Add text associated with the arrow using figure coordinates
    fig.text(x_position, y_position + arrow_length / 2 + 0.01, 'Few POC\nPref Cand.', 
            ha='center', va='bottom', fontsize=26, transform=fig.transFigure)
    fig.text(x_position, y_position - arrow_length / 2 - 0.01, 'Many POC\nPref Cand.', 
            ha='center', va='top', fontsize=26, transform=fig.transFigure)
    

    # Make layout a bit nicer
    plt.tight_layout(pad=1.5)
    fig.subplots_adjust(left=0.09, right=0.98) 
    fig.subplots_adjust(top=0.8)

    plt.savefig(f"./histograms/{plot_title}{file_name_suffix}.png")
    plt.close()
    
if __name__ == "__main__":
    color_dict = {
        "C": "green",
        "WP": "#2F7FBC",
        "WM": "#F75C41"
    }
    
    for cand_type in ["C", "WP", "WM"]:
        df1 = make_dataframe_from_file("zone1_1000_results_3bloc.json", cand_type)     
        df2 = make_dataframe_from_file("zone2_1000_results_3bloc.json", cand_type)
        df3 = make_dataframe_from_file("zone3_1000_results_3bloc.json", cand_type)
        df4 = make_dataframe_from_file("zone4_1000_results_3bloc.json", cand_type)
        
        df_all = (df1 + df2 + df3 + df4)
        
        plot_hist(df1, cand_type, "Zone 1", color_dict[cand_type], 0, 3)
        plot_hist(df2, cand_type, "Zone 2", color_dict[cand_type], 0, 3)
        plot_hist(df3, cand_type, "Zone 3", color_dict[cand_type], 0, 3)
        plot_hist(df4, cand_type, "Zone 4", color_dict[cand_type], 0, 3)
        plot_hist(df_all, cand_type, "All Zones", color_dict[cand_type], 0, 12)


        plot_hist_3(df1.loc[[(2,5,5),(3,5,5),(4,5,5)]], cand_type, "Zone 1", color_dict[cand_type], 0, 3,"_(2,3,4)_cross_section")
        plot_hist_3(df2.loc[[(2,5,5),(3,5,5),(4,5,5)]], cand_type, "Zone 2", color_dict[cand_type], 0, 3,"_(2,3,4)_cross_section")
        plot_hist_3(df3.loc[[(2,5,5),(3,5,5),(4,5,5)]], cand_type, "Zone 3", color_dict[cand_type], 0, 3,"_(2,3,4)_cross_section")
        plot_hist_3(df4.loc[[(2,5,5),(3,5,5),(4,5,5)]], cand_type, "Zone 4", color_dict[cand_type], 0, 3,"_(2,3,4)_cross_section")
        plot_hist_3(df_all.loc[[(2,5,5),(3,5,5),(4,5,5)]], cand_type, "All Zones", color_dict[cand_type], 0, 12,"_(2,3,4)_cross_section")
       