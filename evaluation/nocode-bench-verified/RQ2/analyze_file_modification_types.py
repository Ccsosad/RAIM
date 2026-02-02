import os
import json
import re
import pandas as pd
import argparse
from datasets import load_from_disk

def parse_feature_patch(feature_patch):

    if not feature_patch:
        return []
    

    file_pattern = re.compile(r'diff --git a/([^\s]+) b/([^\s]+)')
    matches = file_pattern.findall(feature_patch)

    python_files = set()
    for old_path, new_path in matches:

        if old_path.endswith('.py'):
            python_files.add(old_path)
        if new_path.endswith('.py'):
            python_files.add(new_path)
    
    return list(python_files)

def get_instance_file_modification_type(instance):

    feature_patch = instance.get('feature_patch', '')
    py_files = parse_feature_patch(feature_patch)
    
    if len(py_files) == 1:
        return 'single_file'
    elif len(py_files) > 1:
        return 'multi_file'
    else:
        return 'single_file'

def load_instance_types(data_path):

    print(f"Loading dataset from: {data_path}")
    dataset = load_from_disk(data_path)
    
    instance_types = {}
    
    print(f"Total instances: {len(dataset)}")
    print("Analyzing instance file modification types...")
    
    for instance in dataset:
        instance_id = instance['instance_id']
        mod_type = get_instance_file_modification_type(instance)
        instance_types[instance_id] = mod_type

    single_file_count = sum(1 for mod_type in instance_types.values() if mod_type == 'single_file')
    multi_file_count = sum(1 for mod_type in instance_types.values() if mod_type == 'multi_file')
    
    print(f"Instance types analysis:")
    print(f"- Single file modification: {single_file_count} ({single_file_count/len(instance_types)*100:.2f}%)")
    print(f"- Multi file modification: {multi_file_count} ({multi_file_count/len(instance_types)*100:.2f}%)")
    print(f"- Total: {len(instance_types)}")
    
    return instance_types

def load_evaluation_results(result_files):

    evaluation_results = {}
    
    for name, path in result_files:
        print(f"Loading result file: {name} from {path}")

        if not os.path.exists(path):
            print(f"Warning: File {path} does not exist, skipping")
            continue

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: File {path} is not valid JSON, skipping: {e}")
            continue
        
        evaluation_results[name] = data
    
    return evaluation_results

def calculate_success_rates(instance_types, evaluation_results):

    success_rates = {}
    
    for method_name, result_data in evaluation_results.items():
        print(f"Calculating success rates for method: {method_name}")
        

        stats = {
            'single_file': {
                'total': 0,
                'resolved': 0,
                'rate': 0.0
            },
            'multi_file': {
                'total': 0,
                'resolved': 0,
                'rate': 0.0
            },
            'overall': {
                'total': 0,
                'resolved': 0,
                'rate': 0.0
            }
        }
        

        repositories = result_data.get('repositories', {})
        for repo_name, repo_stats in repositories.items():
            total = repo_stats.get('total', 0)
            resolved = repo_stats.get('resolved', 0)
            

        success_rates[method_name] = stats
    
    return success_rates

def main():
    parser = argparse.ArgumentParser(description='Analyze success rates by file modification type')
    parser.add_argument('--data_path', type=str, 
                        default='/data/home/ccsosd/ccsosd/CoSIL/ncbench_data/NoCode-bench_Verified_test',
                        help='Path to NoCode-bench Verified test data')
    parser.add_argument('-r', '--result', action='append', nargs=2, metavar=('NAME', 'PATH'),
                        help='Add an evaluation file, format: NAME PATH')
    parser.add_argument('--output_excel', type=str, 
                        default='/data/home/ccsosd/ccsosd/NoCode-bench/evaluation_models/file_modification_stats.xlsx',
                        help='Path to output Excel file')
    parser.add_argument('--output_latex', type=str, default='',
                        help='Path to output LaTeX file')
    
    args = parser.parse_args()

    if not args.result:
        parser.error('-r/--result')

    instance_types = load_instance_types(args.data_path)
    

    print(f"Loading evaluation details from {len(args.result)} files")
    
    method_results = {}
    
    for method_name, file_path in args.result:
        print(f"Loading evaluation details for method: {method_name}")
        

        if not os.path.exists(file_path):
            continue
        
        instance_results = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    instance_id = obj['instance_id']
                    resolved = obj['resolved']
                    instance_results[instance_id] = resolved
                except Exception as e:
                    print(f"Error parsing line: {line.strip()}")
                    print(f"Error: {e}")
                    continue
        
        method_results[method_name] = instance_results
        print(f"- Loaded {len(instance_results)} results")
    

    print("Calculating success rates...")
    
    success_stats = {}
    
    for method_name, results in method_results.items():
        print(f"Calculating success rates for method: {method_name}")
        
        stats = {
            'single_file': {
                'total': 0,
                'resolved': 0,
                'rate': 0.0
            },
            'multi_file': {
                'total': 0,
                'resolved': 0,
                'rate': 0.0
            },
            'overall': {
                'total': 0,
                'resolved': 0,
                'rate': 0.0
            }
        }
        
        for instance_id, resolved in results.items():
            if instance_id not in instance_types:
                continue
            
            mod_type = instance_types[instance_id]
            stats[mod_type]['total'] += 1
            stats['overall']['total'] += 1
            
            if resolved:
                stats[mod_type]['resolved'] += 1
                stats['overall']['resolved'] += 1
        

        for mod_type in ['single_file', 'multi_file', 'overall']:
            if stats[mod_type]['total'] > 0:
                stats[mod_type]['rate'] = stats[mod_type]['resolved'] / stats[mod_type]['total']
        
        success_stats[method_name] = stats

        print(f"- Single file modification: {stats['single_file']['resolved']}/{stats['single_file']['total']} ({stats['single_file']['rate']:.2%})")
        print(f"- Multi file modification: {stats['multi_file']['resolved']}/{stats['multi_file']['total']} ({stats['multi_file']['rate']:.2%})")
        print(f"- Overall: {stats['overall']['resolved']}/{stats['overall']['total']} ({stats['overall']['rate']:.2%})")

    print("Generating tables...")
    

    table_data = []
    for method_name, stats in success_stats.items():

        table_data.append({
            'Method': method_name,
            'Modification Type': 'Single File',
            'Total': stats['single_file']['total'],
            'Resolved': stats['single_file']['resolved'],
            'Success Rate': stats['single_file']['rate']
        })

        table_data.append({
            'Method': method_name,
            'Modification Type': 'Multi File',
            'Total': stats['multi_file']['total'],
            'Resolved': stats['multi_file']['resolved'],
            'Success Rate': stats['multi_file']['rate']
        })

        table_data.append({
            'Method': method_name,
            'Modification Type': 'Overall',
            'Total': stats['overall']['total'],
            'Resolved': stats['overall']['resolved'],
            'Success Rate': stats['overall']['rate']
        })

    df = pd.DataFrame(table_data)

    single_file_total = sum(1 for mod_type in instance_types.values() if mod_type == 'single_file')
    multi_file_total = sum(1 for mod_type in instance_types.values() if mod_type == 'multi_file')
    total_instances = len(instance_types)

    if not df.empty:
        print(f"Saving Excel table to: {args.output_excel}")
        with pd.ExcelWriter(args.output_excel, engine='openpyxl') as writer:

            df['Success Rate (%)'] = df['Success Rate'].map(lambda x: f"{x:.2%}")
            df[['Method', 'Modification Type', 'Total', 'Resolved', 'Success Rate (%)']].to_excel(writer, sheet_name='details', index=False)
            

            pivot_df = df.pivot(index='Method', columns='Modification Type', values='Success Rate')
            pivot_df_percent = pivot_df.map(lambda x: f"{x:.2%}")
            pivot_df_percent.to_excel(writer, sheet_name='table')

    if args.output_latex:
        print(f"Saving LaTeX table to: {args.output_latex}")

        pivot_df = df.pivot(index='Method', columns='Modification Type', values='Success Rate')

        pivot_df = pivot_df[['Single File', 'Multi File', 'Overall']]
        

        with open(args.output_latex, 'w', encoding='utf-8') as f:

            f.write('\\documentclass{article}\n')
            f.write('\\usepackage{booktabs}\n')
            f.write('\\begin{document}\n\n')

            pivot_df_percent = pivot_df * 100

            latex_table = pivot_df_percent.to_latex(
                float_format="%.2f\\%%",
                caption="File Modification Type Success Rates",
                label="tab:file_modification_rates",
                position="htbp"
            )
            

            f.write(latex_table)
            f.write('\n\n')

            f.write('\\end{document}\n')
    
    print("Analysis completed!")

if __name__ == "__main__":
    main()