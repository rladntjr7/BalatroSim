result_paths = "Results"
image_target = "Analysis/Plots"
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib as mpl

# Set up a professional font that resembles LaTeX without requiring LaTeX installation
plt.rcParams.update({
    "font.family": "cmr10",  # or try "Computer Modern"
    "mathtext.fontset": "cm",
    "axes.labelsize": 20,    # Increased from 14
    "axes.titlesize": 18,    # Increased from 16
    "xtick.labelsize": 14,   # Increased from 12
    "ytick.labelsize": 14    # Increased from 12
})

# Get all result files in the result_paths
result_files = [f for f in os.listdir(result_paths) if f.endswith('.csv')]

# Create a dictionary to store dataframes
all_dfs = {}
for file in result_files:
    # Clean up file names for better labels
    strategy_name = os.path.splitext(file)[0].replace('_', ' ').title()
    # Remove " Df" from the end of strategy names
    strategy_name = strategy_name.replace(' Df', '')
    # Read the CSV file
    df = pd.read_csv(os.path.join(result_paths, file))
    # Store it in the dictionary
    all_dfs[strategy_name] = df

# Get all unique columns except 'Strategy'
all_columns = []
for df in all_dfs.values():
    all_columns.extend(col for col in df.columns if col not in ['Strategy'])
unique_columns = sorted(set(all_columns))

# Set up the plots - one for each column
n_columns = len(unique_columns)
n_strategies = len(all_dfs)

# Create directory for saving plots if it doesn't exist
plots_dir = image_target
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

# Different hatch patterns for strategies
hatches = ['/', 
        #    '\\', 
           'x', 
           'o', 
        #    '.', 
        #    '*', 
        #    '+'
           ]

legend_hatches = ['//', 
        #    '\\', 
           'xx', 
           'oo', 
        #    '.', 
        #    '*', 
        #    '+'
           ]
# Process each column in a separate plot
for column in unique_columns:
    # Create a figure with appropriate size
    fig, ax = plt.subplots(figsize=(12, 6))  # Reduced from (12, 8)
    
    # Prepare data for this column across all strategies
    column_data = []
    strategy_names = []
    
    for strategy_name, df in all_dfs.items():
        if column in df.columns:
            column_data.append(df[column].values)
            strategy_names.append(strategy_name)
    
    # Box plot styling - monochrome with hatches
    box_props = dict(linestyle=':', linewidth=1, color='black')  # Changed to dotted line
    whisker_props = dict(linestyle='-', linewidth=2.0, color='black')
    cap_props = dict(linestyle='-', linewidth=2.0, color='black')
    median_props = dict(linestyle='-', linewidth=2.5, color='black')
    flier_props = dict(marker='o', markerfacecolor='none', markersize=6,
                       markeredgecolor='black', linestyle='none')
    mean_props = {'linestyle':'--', "dashes":(4,3.2), 'linewidth':2.5, 'color':'black'}
    
    # Draw a box plot for this column's results with improved styling
    boxplot = ax.boxplot(column_data, 
                        tick_labels=strategy_names,
                        patch_artist=True,
                        boxprops=box_props,
                        whiskerprops=whisker_props,
                        capprops=cap_props,
                        medianprops=median_props,
                        flierprops=flier_props,
                        showmeans=True,
                        meanline=True,
                        widths=0.7,
                        meanprops=mean_props)
    
    # Apply hatches to boxes instead of colors
    for patch, hatch in zip(boxplot['boxes'], hatches[:len(column_data)]):
        patch.set_facecolor('white')
        patch.set_hatch(hatch)
        patch.set_edgecolor('black')
    
    # Horizontal x-axis labels
    plt.xticks(rotation=0)
    
    # Add title and labels with better formatting
    plt.ylabel(column, fontweight='bold')
    plt.xlabel('Strategy', fontweight='bold')
    
    # Add a subtle grid for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Add a light border around the plot
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.5)  # Increased from 1.0
    
    # Add legend for hatches with smaller patches
    legend_patches = []
    for i, (name, hatch) in enumerate(zip(strategy_names, legend_hatches[:len(strategy_names)])):
        # Use smaller legend patches
        patch = mpl.patches.Patch(facecolor='white', edgecolor='black', 
                                 hatch=hatch, label=name)
        legend_patches.append(patch)
    
    # Add mean and median to legend
    mean_line = mpl.lines.Line2D([], [], color='black', linestyle='--', dashes=(4,3), 
                               linewidth=1.5, label='Mean')
    median_line = mpl.lines.Line2D([], [], color='black', linestyle='-', 
                                linewidth=1.5, label='Median')
    legend_patches.extend([mean_line, median_line])
    
    # Smaller legend
    ax.legend(handles=legend_patches, loc='upper right', frameon=True, 
              facecolor='white', edgecolor='black', prop={'size': 13},
              handlelength=2.5, handleheight=2.5, borderpad=0.5)
    
    # Improve layout
    plt.tight_layout()
    # Save the plot with the column name
    safe_column_name = column.replace(' ', '_').lower()
    plt.savefig(f'{plots_dir}/{safe_column_name}_boxplot.pdf', dpi=300, bbox_inches='tight')
    plt.close()

print(f"Generated {n_columns} boxplots, saved in the '{plots_dir}' directory")

