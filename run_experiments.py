#!/usr/bin/env python3
"""
Main script to run fault simulation experiments using ATALANTA
Automates test pattern generation across multiple circuits and configurations
"""

import subprocess
import os
import json
import time
import shlex
from datetime import datetime
from config import *
from atalanta_parser import parse_atalanta_output


class FaultSimulationFramework:
    """Framework to automate ATALANTA experiments and collect results"""
    
    def __init__(self, quick_mode=False):
        self.quick_mode = quick_mode
        self.circuits = QUICK_TEST_CIRCUITS if quick_mode else CIRCUITS
        self.experiments = QUICK_TEST_EXPERIMENTS if quick_mode else EXPERIMENTS
        self.all_results = []
        
        # Create output directories if they don't exist
        os.makedirs(RESULTS_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
        print("=" * 70)
        print("FAULT SIMULATION FRAMEWORK - Stuck-at Fault Coverage Evaluation")
        print("=" * 70)
        print(f"Mode: {'QUICK TEST' if quick_mode else 'FULL EXPERIMENT'}")
        print(f"Circuits to test: {len(self.circuits)}")
        print(f"Experiment configurations: {len(self.experiments)}")
        print(f"Total runs: {len(self.circuits) * len(self.experiments)}")
        print("=" * 70)
        print()
    
    def run_atalanta(self, circuit_file, experiment_config):
        """Run ATALANTA on a single circuit with given configuration"""
        
        circuit_path = os.path.join(CIRCUITS_DIR, circuit_file)
        circuit_basename = os.path.splitext(circuit_file)[0]
        exp_name = experiment_config["name"]
        
        # Output files
        log_file = os.path.join(LOGS_DIR, f"{circuit_basename}_{exp_name}.log")
        test_file = os.path.join(RESULTS_DIR, f"{circuit_basename}_{exp_name}.test")
        
        # Build ATALANTA command without shell quoting issues
        cmd_parts = [ATALANTA_EXEC]
        cmd_parts.extend(shlex.split(experiment_config["options"]))
        cmd_parts.extend(["-l", log_file, "-t", test_file, circuit_path])
        cmd = " ".join(f'"{part}"' if " " in part else part for part in cmd_parts)
        
        print(f"  Running: {circuit_file} with {exp_name} configuration...")
        print(f"  Command: {cmd}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd_parts,
                shell=False,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"  ✓ Success! (Completed in {elapsed_time:.2f}s)")
                
                # Parse the output
                parsed_results = parse_atalanta_output(result.stdout, log_file)
                
                # Add metadata
                parsed_results["experiment"] = exp_name
                parsed_results["experiment_description"] = experiment_config["description"]
                parsed_results["command"] = cmd
                parsed_results["elapsed_time"] = round(elapsed_time, 2)
                parsed_results["timestamp"] = datetime.now().isoformat()
                
                return parsed_results
            else:
                print(f"  ✗ Failed with return code {result.returncode}")
                print(f"  Error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout (exceeded 5 minutes)")
            return None
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return None
    
    def run_all_experiments(self):
        """Run experiments on all circuits with all configurations"""
        
        total_runs = len(self.circuits) * len(self.experiments)
        current_run = 0
        
        for circuit in self.circuits:
            print(f"\n{'='*70}")
            print(f"Circuit: {circuit}")
            print(f"{'='*70}")
            
            for experiment in self.experiments:
                current_run += 1
                print(f"\n[{current_run}/{total_runs}] Experiment: {experiment['name']}")
                print(f"  Description: {experiment['description']}")
                
                result = self.run_atalanta(circuit, experiment)
                
                if result:
                    self.all_results.append(result)
                
                print()
        
        print(f"\n{'='*70}")
        print(f"All experiments completed!")
        print(f"Successful runs: {len(self.all_results)}/{total_runs}")
        print(f"{'='*70}\n")
    
    def save_results(self):
        """Save all results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(RESULTS_DIR, f"experiment_results_{timestamp}.json")
        
        with open(results_file, 'w') as f:
            json.dump(self.all_results, f, indent=2)
        
        print(f"Results saved to: {results_file}")
        return results_file
    
    def generate_summary(self):
        """Generate a text summary of results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = os.path.join(REPORTS_DIR, f"summary_{timestamp}.txt")
        
        with open(summary_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("FAULT SIMULATION FRAMEWORK - EXPERIMENT SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total experiments: {len(self.all_results)}\n\n")
            
            # Group by circuit
            circuits_data = {}
            for result in self.all_results:
                circuit = result["circuit_name"]
                if circuit not in circuits_data:
                    circuits_data[circuit] = []
                circuits_data[circuit].append(result)
            
            for circuit, results in circuits_data.items():
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"Circuit: {circuit}\n")
                f.write("=" * 80 + "\n")
                
                if results:
                    struct = results[0]["circuit_structure"]
                    f.write(f"  Inputs: {struct['inputs']}, Outputs: {struct['outputs']}, ")
                    f.write(f"Gates: {struct['gates']}, Levels: {struct['level']}\n\n")
                
                f.write(f"{'Experiment':<20} {'Coverage %':<12} {'Patterns':<10} {'Faults':<15} {'Time (s)':<10}\n")
                f.write("-" * 80 + "\n")
                
                for r in results:
                    exp_name = r["experiment"]
                    tg = r["test_generation"]
                    coverage = f"{tg['fault_coverage']:.2f}%"
                    patterns = f"{tg['patterns_after_compaction']}"
                    faults = f"{tg['detected_faults']}/{tg['total_faults']}"
                    cpu_time = f"{r['performance']['total_cpu_time']:.3f}"
                    
                    f.write(f"{exp_name:<20} {coverage:<12} {patterns:<10} {faults:<15} {cpu_time:<10}\n")
        
        print(f"Summary report saved to: {summary_file}")
        
        # Also print to console
        print("\n" + "=" * 80)
        print("QUICK SUMMARY")
        print("=" * 80)
        with open(summary_file, 'r') as f:
            print(f.read())
        
        return summary_file


def main():
    """Main entry point"""
    import sys
    
    # Check if quick mode is requested
    quick_mode = "--quick" in sys.argv or "-q" in sys.argv
    
    # Initialize and run framework
    framework = FaultSimulationFramework(quick_mode=quick_mode)
    
    # Run all experiments
    framework.run_all_experiments()
    
    # Save results
    framework.save_results()
    
    # Generate summary
    framework.generate_summary()
    
    print("\n✓ Framework execution completed!")
    print(f"  - Results saved in: {RESULTS_DIR}/")
    print(f"  - Logs saved in: {LOGS_DIR}/")
    print(f"  - Reports saved in: {REPORTS_DIR}/")


if __name__ == "__main__":
    main()
