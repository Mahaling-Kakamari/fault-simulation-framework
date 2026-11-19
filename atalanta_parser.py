"""
Parser for ATALANTA output files
Extracts fault coverage metrics and test pattern information
"""

import re
import os


class AtalantaParser:
    """Parse ATALANTA output and log files"""
    
    def __init__(self, output_text, log_file_path=None):
        self.output_text = output_text
        self.log_file_path = log_file_path
        self.results = {}
        
    def parse_output(self):
        """Parse the main ATALANTA output"""
        
        # Circuit structure info
        circuit_name = self._extract_value(r"Name of the circuit\s*:\s*(\S+)")
        num_inputs = self._extract_int(r"Number of primary inputs\s*:\s*(\d+)")
        num_outputs = self._extract_int(r"Number of primary outputs\s*:\s*(\d+)")
        num_gates = self._extract_int(r"Number of gates\s*:\s*(\d+)")
        circuit_level = self._extract_int(r"Level of the circuit\s*:\s*(\d+)")
        
        # Test pattern generation results
        patterns_before = self._extract_int(r"Number of test patterns before compaction\s*:\s*(\d+)")
        patterns_after = self._extract_int(r"Number of test patterns after compaction\s*:\s*(\d+)")
        fault_coverage = self._extract_float(r"Fault coverage\s*:\s*([\d.]+)")
        num_faults = self._extract_int(r"Number of collapsed faults\s*:\s*(\d+)")
        redundant_faults = self._extract_int(r"Number of identified redundant faults\s*:\s*(\d+)")
        aborted_faults = self._extract_int(r"Number of aborted faults\s*:\s*(\d+)")
        backtrackings = self._extract_int(r"Total number of backtrackings\s*:\s*(\d+)")
        
        # CPU time
        cpu_time = self._extract_float(r"Total\s*:\s*([\d.]+)\s*Secs")
        fault_sim_time = self._extract_float(r"Fault simulation\s*:\s*([\d.]+)\s*Secs")
        fan_time = self._extract_float(r"FAN\s*:\s*([\d.]+)\s*Secs")
        
        self.results = {
            "circuit_name": circuit_name,
            "circuit_structure": {
                "inputs": num_inputs,
                "outputs": num_outputs,
                "gates": num_gates,
                "level": circuit_level
            },
            "test_generation": {
                "patterns_before_compaction": patterns_before,
                "patterns_after_compaction": patterns_after,
                "compaction_ratio": round(patterns_after / patterns_before * 100, 2) if patterns_before else 0,
                "fault_coverage": fault_coverage,
                "total_faults": num_faults,
                "detected_faults": int(num_faults * fault_coverage / 100) if num_faults else 0,
                "redundant_faults": redundant_faults,
                "aborted_faults": aborted_faults,
                "backtrackings": backtrackings
            },
            "performance": {
                "total_cpu_time": cpu_time,
                "fault_simulation_time": fault_sim_time,
                "fan_time": fan_time
            }
        }
        
        return self.results
    
    def _extract_value(self, pattern):
        """Extract string value using regex"""
        match = re.search(pattern, self.output_text)
        return match.group(1) if match else None
    
    def _extract_int(self, pattern):
        """Extract integer value using regex"""
        match = re.search(pattern, self.output_text)
        return int(match.group(1)) if match else 0
    
    def _extract_float(self, pattern):
        """Extract float value using regex"""
        match = re.search(pattern, self.output_text)
        return float(match.group(1)) if match else 0.0
    
    def parse_log_file(self):
        """Parse the detailed log file to get per-pattern statistics"""
        if not self.log_file_path or not os.path.exists(self.log_file_path):
            return None
        
        pattern_stats = []
        with open(self.log_file_path, 'r') as f:
            for line in f:
                # Match lines like: "fpTestFile    1: ... 857 faults detected"
                match = re.search(r'fpTestFile\s+(\d+):.*?(\d+)\s+faults?\s+detected', line)
                if match:
                    pattern_num = int(match.group(1))
                    faults_detected = int(match.group(2))
                    pattern_stats.append({
                        "pattern_number": pattern_num,
                        "faults_detected": faults_detected
                    })
        
        return pattern_stats


def parse_atalanta_output(output_text, log_file_path=None):
    """Convenience function to parse ATALANTA output"""
    parser = AtalantaParser(output_text, log_file_path)
    results = parser.parse_output()
    
    if log_file_path:
        results["pattern_statistics"] = parser.parse_log_file()
    
    return results
