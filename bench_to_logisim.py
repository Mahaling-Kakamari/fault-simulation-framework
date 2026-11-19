#!/usr/bin/env python3
"""
Convert .bench file to Logisim-evolution .circ file
Supports: AND, OR, NOT, NAND, NOR, XOR, BUF gates
"""

import re
import sys
import subprocess
import os


class BenchToLogisim:
    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.gates = []  # List of (output_signal, gate_type, input_signals)
        self.signal_coords = {}  # Signal name -> (x, y)
        self.wires = []  # List of (from_x, from_y, to_x, to_y)
        
        # Layout parameters
        self.input_x = 100
        self.gate_start_x = 300
        self.gate_spacing_x = 150
        self.output_x = 700
        self.vertical_spacing = 100
        
    def parse_bench(self, filepath):
        """Parse .bench file and extract inputs, outputs, and gates"""
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse INPUT
                if line.startswith('INPUT'):
                    match = re.match(r'INPUT\((\w+)\)', line)
                    if match:
                        self.inputs.append(match.group(1))
                
                # Parse OUTPUT
                elif line.startswith('OUTPUT'):
                    match = re.match(r'OUTPUT\((\w+)\)', line)
                    if match:
                        self.outputs.append(match.group(1))
                
                # Parse gate assignment
                elif '=' in line:
                    # Format: output = GATE(input1, input2, ...)
                    parts = line.split('=')
                    output_signal = parts[0].strip()
                    gate_expr = parts[1].strip()
                    
                    # Extract gate type and inputs
                    match = re.match(r'(\w+)\((.*)\)', gate_expr)
                    if match:
                        gate_type = match.group(1)
                        inputs_str = match.group(2)
                        input_signals = [s.strip() for s in inputs_str.split(',')]
                        
                        self.gates.append((output_signal, gate_type, input_signals))
    
    def assign_coordinates(self):
        """Assign x,y coordinates to all components"""
        y_pos = 100
        
        # Assign coordinates to inputs
        for inp in self.inputs:
            self.signal_coords[inp] = (self.input_x, y_pos)
            y_pos += self.vertical_spacing
        
        # Assign coordinates to gates (and their output signals)
        gate_x = self.gate_start_x
        gate_y = 150  # Center gates vertically
        
        for i, (output_signal, gate_type, input_signals) in enumerate(self.gates):
            # Calculate average Y position of inputs for better wire routing
            input_y_positions = []
            for inp_sig in input_signals:
                if inp_sig in self.signal_coords:
                    input_y_positions.append(self.signal_coords[inp_sig][1])
            
            if input_y_positions:
                avg_y = sum(input_y_positions) // len(input_y_positions)
            else:
                avg_y = gate_y
            
            # Place gate
            gate_coord = (gate_x, avg_y)
            self.signal_coords[output_signal] = gate_coord
            
            gate_x += self.gate_spacing_x
        
        # Assign coordinates to outputs
        y_pos = 150
        for out in self.outputs:
            if out not in self.signal_coords:
                # Output not connected to any gate, place it anyway
                self.signal_coords[out] = (self.output_x, y_pos)
            # Note: outputs that are gate outputs will use gate coordinates
            y_pos += self.vertical_spacing
    
    def get_logisim_gate_name(self, gate_type):
        """Map bench gate type to Logisim component name"""
        gate_map = {
            'AND': 'AND Gate',
            'OR': 'OR Gate',
            'NOT': 'NOT Gate',
            'NAND': 'NAND Gate',
            'NOR': 'NOR Gate',
            'XOR': 'XOR Gate',
            'XNOR': 'XNOR Gate',
            'BUF': 'Buffer',
            'BUFF': 'Buffer'
        }
        return gate_map.get(gate_type.upper(), 'AND Gate')
    
    def get_gate_input_count(self, gate_type):
        """Get number of inputs for a gate type"""
        if gate_type.upper() in ['NOT', 'BUF', 'BUFF']:
            return 1
        return 2  # Default to 2-input gates
    
    def generate_circ(self, output_filepath):
        """Generate Logisim .circ XML file"""
        xml_lines = []
        xml_lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
        xml_lines.append('<project source="3.8.0" version="1.0">')
        xml_lines.append('  <lib desc="#Wiring" name="0"/>')
        xml_lines.append('  <lib desc="#Gates" name="1"/>')
        xml_lines.append('  <main name="main"/>')
        xml_lines.append('  <circuit name="main">')
        
        # Add input pins
        for inp in self.inputs:
            x, y = self.signal_coords[inp]
            xml_lines.append(f'    <comp lib="0" loc="({x},{y})" name="Pin">')
            xml_lines.append(f'      <a name="label" val="{inp}"/>')
            xml_lines.append('      <a name="appearance" val="classic"/>')
            xml_lines.append('    </comp>')
        
        # Add gates
        for output_signal, gate_type, input_signals in self.gates:
            x, y = self.signal_coords[output_signal]
            gate_name = self.get_logisim_gate_name(gate_type)
            input_count = self.get_gate_input_count(gate_type)
            
            xml_lines.append(f'    <comp lib="1" loc="({x},{y})" name="{gate_name}">')
            if input_count > 2:
                xml_lines.append(f'      <a name="inputs" val="{input_count}"/>')
            xml_lines.append('    </comp>')
        
        # Add output pins
        for out in self.outputs:
            # Find the gate that produces this output
            gate_x = None
            for output_signal, gate_type, input_signals in self.gates:
                if output_signal == out:
                    gate_x, gate_y = self.signal_coords[output_signal]
                    break
            
            if gate_x:
                # Place output pin to the right of the gate
                out_x = gate_x + 100
                out_y = gate_y
            else:
                # Fallback if output not found
                out_x, out_y = self.output_x, 150
            
            xml_lines.append(f'    <comp lib="0" loc="({out_x},{out_y})" name="Pin">')
            xml_lines.append(f'      <a name="label" val="{out}"/>')
            xml_lines.append('      <a name="appearance" val="classic"/>')
            xml_lines.append('      <a name="facing" val="west"/>')
            xml_lines.append('      <a name="output" val="true"/>')
            xml_lines.append('    </comp>')
        
        # Add wires
        # Wire from inputs to gates
        for output_signal, gate_type, input_signals in self.gates:
            gate_x, gate_y = self.signal_coords[output_signal]
            
            # Calculate input positions based on gate type
            if gate_type.upper() in ['NOT', 'BUF', 'BUFF']:
                # Single input gate - input on the left
                input_offset = 0
            else:
                # Multi-input gate - inputs vertically spaced
                input_offset = -10
            
            for i, inp_sig in enumerate(input_signals):
                if inp_sig in self.signal_coords:
                    from_x, from_y = self.signal_coords[inp_sig]
                    to_x = gate_x - 30  # Input point of gate
                    to_y = gate_y + input_offset * (i - len(input_signals)/2 + 0.5)
                    
                    xml_lines.append(f'    <wire from="({from_x},{from_y})" to="({int(to_x)},{int(to_y)})"/>')
        
        # Wire from gates to outputs
        for out in self.outputs:
            for output_signal, gate_type, input_signals in self.gates:
                if output_signal == out:
                    gate_x, gate_y = self.signal_coords[output_signal]
                    out_x = gate_x + 100
                    out_y = gate_y
                    xml_lines.append(f'    <wire from="({gate_x},{gate_y})" to="({out_x},{out_y})"/>')
                    break
        
        xml_lines.append('  </circuit>')
        xml_lines.append('</project>')
        
        # Write to file
        with open(output_filepath, 'w') as f:
            f.write('\n'.join(xml_lines))
    
    def convert_and_display(self, bench_file, circ_file=None):
        """Convert .bench to .circ and open in Logisim"""
        # Parse bench file
        print(f"Parsing {bench_file}...")
        self.parse_bench(bench_file)
        
        print(f"  Inputs: {self.inputs}")
        print(f"  Outputs: {self.outputs}")
        print(f"  Gates: {len(self.gates)}")
        
        # Assign coordinates
        print("Assigning coordinates...")
        self.assign_coordinates()
        
        # Generate .circ file
        if circ_file is None:
            circ_file = bench_file.replace('.bench', '.circ')
        
        print(f"Generating {circ_file}...")
        self.generate_circ(circ_file)
        print(f"✓ Created {circ_file}")
        
        # Try to open in Logisim
        print("\nAttempting to open in Logisim-evolution...")
        try:
            subprocess.Popen(['logisim-evolution', circ_file])
            print("✓ Logisim launched successfully!")
            return True
        except FileNotFoundError:
            print("✗ logisim-evolution not found!")
            print("\nTo install on Ubuntu:")
            print("  sudo apt update")
            print("  sudo apt install logisim-evolution")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bench_to_logisim.py <input.bench> [output.circ]")
        print("\nExample:")
        print("  python3 bench_to_logisim.py test_simple.bench")
        sys.exit(1)
    
    bench_file = sys.argv[1]
    circ_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(bench_file):
        print(f"Error: File not found: {bench_file}")
        sys.exit(1)
    
    converter = BenchToLogisim()
    converter.convert_and_display(bench_file, circ_file)


if __name__ == "__main__":
    main()
