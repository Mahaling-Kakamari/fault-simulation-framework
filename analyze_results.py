#!/usr/bin/env python3
"""
Analysis and visualization script for fault simulation results
Generates comparison charts and detailed analysis
"""

import json
import os
import glob
from config import RESULTS_DIR, REPORTS_DIR


class ResultsAnalyzer:
    """Analyze and visualize fault simulation results"""
    
    def __init__(self, results_file=None):
        if results_file:
            self.results_file = results_file
        else:
            # Find the most recent results file
            json_files = glob.glob(os.path.join(RESULTS_DIR, "experiment_results_*.json"))
            if not json_files:
                raise FileNotFoundError("No results files found!")
            self.results_file = max(json_files, key=os.path.getctime)
        
        print(f"Analyzing results from: {self.results_file}")
        
        with open(self.results_file, 'r') as f:
            self.results = json.load(f)
    
    def generate_comparison_report(self):
        """Generate detailed comparison report"""
        
        report_file = os.path.join(REPORTS_DIR, "detailed_analysis.txt")
        
        with open(report_file, 'w') as f:
            f.write("=" * 100 + "\n")
            f.write("DETAILED FAULT SIMULATION ANALYSIS\n")
            f.write("=" * 100 + "\n\n")
            
            # 1. Coverage Analysis
            f.write("\n1. FAULT COVERAGE ANALYSIS\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Circuit':<20} {'Experiment':<20} {'Coverage %':<15} {'Detected':<15} {'Total':<10}\n")
            f.write("-" * 100 + "\n")
            
            for r in self.results:
                circuit = r["circuit_name"]
                exp = r["experiment"]
                tg = r["test_generation"]
                f.write(f"{circuit:<20} {exp:<20} {tg['fault_coverage']:<15.2f} "
                       f"{tg['detected_faults']:<15} {tg['total_faults']:<10}\n")
            
            # 2. Test Pattern Efficiency
            f.write("\n\n2. TEST PATTERN EFFICIENCY\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Circuit':<20} {'Experiment':<20} {'Before':<10} {'After':<10} "
                   f"{'Reduction %':<15} {'Efficiency':<15}\n")
            f.write("-" * 100 + "\n")
            
            for r in self.results:
                circuit = r["circuit_name"]
                exp = r["experiment"]
                tg = r["test_generation"]
                before = tg["patterns_before_compaction"]
                after = tg["patterns_after_compaction"]
                reduction = ((before - after) / before * 100) if before > 0 else 0
                efficiency = (tg["detected_faults"] / after) if after > 0 else 0
                
                f.write(f"{circuit:<20} {exp:<20} {before:<10} {after:<10} "
                       f"{reduction:<15.2f} {efficiency:<15.2f}\n")
            
            # 3. Performance Analysis
            f.write("\n\n3. PERFORMANCE ANALYSIS\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Circuit':<20} {'Experiment':<20} {'Total Time':<15} "
                   f"{'Fault Sim':<15} {'FAN Time':<15}\n")
            f.write("-" * 100 + "\n")
            
            for r in self.results:
                circuit = r["circuit_name"]
                exp = r["experiment"]
                perf = r["performance"]
                f.write(f"{circuit:<20} {exp:<20} {perf['total_cpu_time']:<15.3f} "
                       f"{perf['fault_simulation_time']:<15.3f} {perf['fan_time']:<15.3f}\n")
            
            # 4. Circuit Complexity Analysis
            f.write("\n\n4. CIRCUIT COMPLEXITY vs FAULT COVERAGE\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Circuit':<20} {'Gates':<10} {'Inputs':<10} {'Outputs':<10} "
                   f"{'Levels':<10} {'Avg Coverage':<15}\n")
            f.write("-" * 100 + "\n")
            
            # Group by circuit
            circuits_data = {}
            for r in self.results:
                circuit = r["circuit_name"]
                if circuit not in circuits_data:
                    circuits_data[circuit] = []
                circuits_data[circuit].append(r)
            
            for circuit, results in circuits_data.items():
                struct = results[0]["circuit_structure"]
                avg_coverage = sum(r["test_generation"]["fault_coverage"] for r in results) / len(results)
                
                f.write(f"{circuit:<20} {struct['gates']:<10} {struct['inputs']:<10} "
                       f"{struct['outputs']:<10} {struct['level']:<10} {avg_coverage:<15.2f}\n")
            
            # 5. Best Configuration Analysis
            f.write("\n\n5. BEST CONFIGURATIONS PER CIRCUIT\n")
            f.write("-" * 100 + "\n")
            
            for circuit, results in circuits_data.items():
                f.write(f"\nCircuit: {circuit}\n")
                
                # Find best coverage
                best_coverage = max(results, key=lambda x: x["test_generation"]["fault_coverage"])
                f.write(f"  Best Coverage: {best_coverage['experiment']} "
                       f"({best_coverage['test_generation']['fault_coverage']:.2f}%)\n")
                
                # Find most efficient (patterns vs coverage)
                best_efficiency = min(results, 
                    key=lambda x: x["test_generation"]["patterns_after_compaction"] 
                                  / max(x["test_generation"]["fault_coverage"], 0.1))
                f.write(f"  Most Efficient: {best_efficiency['experiment']} "
                       f"({best_efficiency['test_generation']['patterns_after_compaction']} patterns, "
                       f"{best_efficiency['test_generation']['fault_coverage']:.2f}% coverage)\n")
                
                # Find fastest
                fastest = min(results, key=lambda x: x["performance"]["total_cpu_time"])
                f.write(f"  Fastest: {fastest['experiment']} "
                       f"({fastest['performance']['total_cpu_time']:.3f}s)\n")
        
        print(f"\nDetailed analysis saved to: {report_file}")
        
        # Print to console
        with open(report_file, 'r') as f:
            print("\n" + f.read())
        
        return report_file
    
    def print_key_insights(self):
        """Print key insights from the analysis"""
        
        print("\n" + "=" * 100)
        print("KEY INSIGHTS")
        print("=" * 100)
        
        # Overall statistics
        total_experiments = len(self.results)
        avg_coverage = sum(r["test_generation"]["fault_coverage"] for r in self.results) / total_experiments
        
        print(f"\n✓ Total Experiments Run: {total_experiments}")
        print(f"✓ Average Fault Coverage: {avg_coverage:.2f}%")
        
        # Best overall result
        best = max(self.results, key=lambda x: x["test_generation"]["fault_coverage"])
        print(f"\n✓ Best Result:")
        print(f"  Circuit: {best['circuit_name']}")
        print(f"  Configuration: {best['experiment']}")
        print(f"  Coverage: {best['test_generation']['fault_coverage']:.2f}%")
        print(f"  Test Patterns: {best['test_generation']['patterns_after_compaction']}")
        
        # Fastest result
        fastest = min(self.results, key=lambda x: x["performance"]["total_cpu_time"])
        print(f"\n✓ Fastest Execution:")
        print(f"  Circuit: {fastest['circuit_name']}")
        print(f"  Time: {fastest['performance']['total_cpu_time']:.3f}s")
        
        print("\n" + "=" * 100)


def main():
    """Main entry point"""
    import sys
    
    results_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        analyzer = ResultsAnalyzer(results_file)
        analyzer.generate_comparison_report()
        analyzer.print_key_insights()
        
        print("\n✓ Analysis completed!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run experiments first using: python3 run_experiments.py")


if __name__ == "__main__":
    main()
