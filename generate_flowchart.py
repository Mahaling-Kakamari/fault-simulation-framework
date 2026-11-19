#!/usr/bin/env python3
"""
Generate System Architecture Flowchart for Fault Simulation Framework
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Color scheme
color_user = '#E8F4F8'
color_module = '#B3D9FF'
color_process = '#FFE6CC'
color_output = '#D5E8D4'
color_atalanta = '#F8CECC'

# Title
ax.text(5, 11.5, 'Fault Simulation Framework Architecture', 
        fontsize=18, fontweight='bold', ha='center')

# User Input
user_box = FancyBboxPatch((4, 10.5), 2, 0.6, boxstyle="round,pad=0.1", 
                          edgecolor='black', facecolor=color_user, linewidth=2)
ax.add_patch(user_box)
ax.text(5, 10.8, 'User Interface', ha='center', va='center', fontsize=11, fontweight='bold')

# Arrow down
arrow1 = FancyArrowPatch((5, 10.5), (5, 9.8), arrowstyle='->', lw=2, color='black',
                         mutation_scale=20)
ax.add_artist(arrow1)

# Main Tabs Container
tabs_box = FancyBboxPatch((0.5, 5), 9, 4.5, boxstyle="round,pad=0.1", 
                          edgecolor='navy', facecolor='white', linewidth=3, linestyle='--')
ax.add_patch(tabs_box)
ax.text(5, 9.3, 'Three-Module Tabbed Interface', ha='center', va='center', 
        fontsize=12, fontweight='bold', style='italic')

# Module 1: ATPG Runner
module1_box = FancyBboxPatch((0.8, 6.8), 2.5, 2, boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=color_module, linewidth=2)
ax.add_patch(module1_box)
ax.text(2.05, 8.5, 'ATPG Runner', ha='center', va='center', fontsize=10, fontweight='bold')
ax.text(2.05, 8.1, '• File Selection', ha='center', va='center', fontsize=8)
ax.text(2.05, 7.8, '• Config Options', ha='center', va='center', fontsize=8)
ax.text(2.05, 7.5, '• Real-time Exec', ha='center', va='center', fontsize=8)
ax.text(2.05, 7.2, '• Progress Track', ha='center', va='center', fontsize=8)

# Module 2: Result Analyzer
module2_box = FancyBboxPatch((3.75, 6.8), 2.5, 2, boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=color_module, linewidth=2)
ax.add_patch(module2_box)
ax.text(5, 8.5, 'Result Analyzer', ha='center', va='center', fontsize=10, fontweight='bold')
ax.text(5, 8.1, '• Log Parsing', ha='center', va='center', fontsize=8)
ax.text(5, 7.8, '• 25+ Metrics', ha='center', va='center', fontsize=8)
ax.text(5, 7.5, '• 5 Charts', ha='center', va='center', fontsize=8)
ax.text(5, 7.2, '• Visualization', ha='center', va='center', fontsize=8)

# Module 3: Batch Execution
module3_box = FancyBboxPatch((6.7, 6.8), 2.5, 2, boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=color_module, linewidth=2)
ax.add_patch(module3_box)
ax.text(7.95, 8.5, 'Batch Execution', ha='center', va='center', fontsize=10, fontweight='bold')
ax.text(7.95, 8.1, '• Multi-Circuit', ha='center', va='center', fontsize=8)
ax.text(7.95, 7.8, '• CSV/TXT Reports', ha='center', va='center', fontsize=8)
ax.text(7.95, 7.5, '• Statistics', ha='center', va='center', fontsize=8)
ax.text(7.95, 7.2, '• Export', ha='center', va='center', fontsize=8)

# Processing Layer Label
ax.text(5, 6.4, 'Processing Layer', ha='center', va='center', 
        fontsize=11, fontweight='bold', style='italic')

# Arrows to ATALANTA
arrow2 = FancyArrowPatch((2.05, 6.8), (3.5, 5.8), arrowstyle='->', lw=2, color='black',
                         mutation_scale=20)
ax.add_artist(arrow2)
arrow3 = FancyArrowPatch((5, 6.8), (5, 5.8), arrowstyle='->', lw=2, color='black',
                         mutation_scale=20)
ax.add_artist(arrow3)
arrow4 = FancyArrowPatch((7.95, 6.8), (6.5, 5.8), arrowstyle='->', lw=2, color='black',
                         mutation_scale=20)
ax.add_artist(arrow4)

# ATALANTA ATPG Tool
atalanta_box = FancyBboxPatch((3.5, 5), 3, 0.7, boxstyle="round,pad=0.1", 
                             edgecolor='black', facecolor=color_atalanta, linewidth=2)
ax.add_patch(atalanta_box)
ax.text(5, 5.35, 'ATALANTA ATPG Engine', ha='center', va='center', 
        fontsize=11, fontweight='bold')

# Arrow to Outputs
arrow5 = FancyArrowPatch((5, 5), (5, 4.3), arrowstyle='->', lw=2, color='black',
                         mutation_scale=20)
ax.add_artist(arrow5)

# Output Processing
output_label = FancyBboxPatch((3.5, 3.8), 3, 0.4, boxstyle="round,pad=0.05", 
                             edgecolor='black', facecolor=color_process, linewidth=2)
ax.add_patch(output_label)
ax.text(5, 4, 'Output Processing & Storage', ha='center', va='center', 
        fontsize=10, fontweight='bold')

# Arrow to output types
arrow6 = FancyArrowPatch((5, 3.8), (5, 3.2), arrowstyle='->', lw=2, color='black',
                         mutation_scale=20)
ax.add_artist(arrow6)

# Output Types
output1_box = FancyBboxPatch((0.5, 1.8), 2.2, 1.2, boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=color_output, linewidth=1.5)
ax.add_patch(output1_box)
ax.text(1.6, 2.8, 'Log Files', ha='center', va='center', fontsize=9, fontweight='bold')
ax.text(1.6, 2.5, '• Timestamped', ha='center', va='center', fontsize=7)
ax.text(1.6, 2.3, '• Metadata', ha='center', va='center', fontsize=7)
ax.text(1.6, 2.1, '• ATPG Config', ha='center', va='center', fontsize=7)

output2_box = FancyBboxPatch((3.1, 1.8), 2.2, 1.2, boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=color_output, linewidth=1.5)
ax.add_patch(output2_box)
ax.text(4.2, 2.8, 'Charts', ha='center', va='center', fontsize=9, fontweight='bold')
ax.text(4.2, 2.5, '• Fault Dist.', ha='center', va='center', fontsize=7)
ax.text(4.2, 2.3, '• Coverage', ha='center', va='center', fontsize=7)
ax.text(4.2, 2.1, '• Time Breakdown', ha='center', va='center', fontsize=7)

output3_box = FancyBboxPatch((5.7, 1.8), 2.2, 1.2, boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=color_output, linewidth=1.5)
ax.add_patch(output3_box)
ax.text(6.8, 2.8, 'Batch Reports', ha='center', va='center', fontsize=9, fontweight='bold')
ax.text(6.8, 2.5, '• summary.csv', ha='center', va='center', fontsize=7)
ax.text(6.8, 2.3, '• summary.txt', ha='center', va='center', fontsize=7)
ax.text(6.8, 2.1, '• Statistics', ha='center', va='center', fontsize=7)

output4_box = FancyBboxPatch((8.3, 1.8), 1.5, 1.2, boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=color_output, linewidth=1.5)
ax.add_patch(output4_box)
ax.text(9.05, 2.8, 'Metrics', ha='center', va='center', fontsize=9, fontweight='bold')
ax.text(9.05, 2.5, '• Coverage', ha='center', va='center', fontsize=7)
ax.text(9.05, 2.3, '• Patterns', ha='center', va='center', fontsize=7)
ax.text(9.05, 2.1, '• CPU Time', ha='center', va='center', fontsize=7)

# Arrows to outputs
arrow7 = FancyArrowPatch((5, 3.2), (1.6, 3), arrowstyle='->', lw=1.5, color='black',
                         mutation_scale=15)
ax.add_artist(arrow7)
arrow8 = FancyArrowPatch((5, 3.2), (4.2, 3), arrowstyle='->', lw=1.5, color='black',
                         mutation_scale=15)
ax.add_artist(arrow8)
arrow9 = FancyArrowPatch((5, 3.2), (6.8, 3), arrowstyle='->', lw=1.5, color='black',
                         mutation_scale=15)
ax.add_artist(arrow9)
arrow10 = FancyArrowPatch((5, 3.2), (9.05, 3), arrowstyle='->', lw=1.5, color='black',
                         mutation_scale=15)
ax.add_artist(arrow10)

# Key Features Box
features_box = FancyBboxPatch((0.5, 0.3), 9, 1.2, boxstyle="round,pad=0.1", 
                             edgecolor='darkgreen', facecolor='#F0FFF0', linewidth=2)
ax.add_patch(features_box)
ax.text(5, 1.2, 'Key Features', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='darkgreen')
ax.text(2.5, 0.9, '✓ Real-time Monitoring', ha='center', va='center', fontsize=8)
ax.text(2.5, 0.6, '✓ Configurable Options', ha='center', va='center', fontsize=8)
ax.text(5, 0.9, '✓ 25+ Metrics Extraction', ha='center', va='center', fontsize=8)
ax.text(5, 0.6, '✓ Professional Visualization', ha='center', va='center', fontsize=8)
ax.text(7.5, 0.9, '✓ Batch Processing', ha='center', va='center', fontsize=8)
ax.text(7.5, 0.6, '✓ Automated Reports', ha='center', va='center', fontsize=8)

# Legend
legend_elements = [
    mpatches.Patch(color=color_user, label='User Interface', edgecolor='black'),
    mpatches.Patch(color=color_module, label='Framework Modules', edgecolor='black'),
    mpatches.Patch(color=color_atalanta, label='ATPG Engine', edgecolor='black'),
    mpatches.Patch(color=color_output, label='Output Types', edgecolor='black')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=8, framealpha=0.9)

plt.tight_layout()
plt.savefig('images/system_flowchart.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Flowchart generated: images/system_flowchart.png")
plt.close()
