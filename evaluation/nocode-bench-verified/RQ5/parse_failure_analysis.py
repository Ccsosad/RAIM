import argparse
import re
import pandas as pd
import os

# Regular expressions to extract the required information
PATTERNS = {
    'total_instances': r'Total Instances:\s*(\d+)',
    'success': r'Successfully Resolved:\s*(\d+)\s*\(([\d.]+)%\)',
    'failure': r'Failed to Resolve:\s*(\d+)\s*\(([\d.]+)%\)',
    'regression_p2p': r'1\. Regression Errors \(P2P\):\s*(\d+)\s*\(([\d.]+)%\)',
    'new_feature_f2p': r'2\. New Feature Implementation Errors \(F2P\):\s*(\d+)\s*\(([\d.]+)%\)',
    'both_errors': r'3\. Both Types of Errors:\s*(\d+)\s*\(([\d.]+)%\)',
}

def parse_failure_analysis(file_path):
    """
    Parse the failure analysis section from the given file.
    """
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the Failure Type Analysis section
    analysis_start = content.find('Failure Type Analysis')
    if analysis_start == -1:
        print(f"Warning: 'Failure Type Analysis' section not found in {file_path}")
        return None
    
    # Extract the required information
    result = {
        'total_instances': 0,
        'success_count': 0,
        'success_percent': 0.0,
        'failure_count': 0,
        'failure_percent': 0.0,
        'regression_p2p_count': 0,
        'regression_p2p_percent': 0.0,
        'new_feature_f2p_count': 0,
        'new_feature_f2p_percent': 0.0,
        'both_errors_count': 0,
        'both_errors_percent': 0.0,
    }
    
    # Parse all patterns from the entire file
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, content)
        if match:
            if key == 'total_instances':
                result['total_instances'] = int(match.group(1))
            else:
                result[f'{key}_count'] = int(match.group(1))
                result[f'{key}_percent'] = float(match.group(2))
        else:
            print(f"Warning: {key} not found in {file_path}")
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Parse failure analysis results from evaluation files.')
    parser.add_argument('results', nargs='+', help='Method name and result file path pairs, e.g., "Method1 /path/to/result1.txt" "Method2 /path/to/result2.txt"')
    parser.add_argument('--output', '-o', default='failure_analysis_summary.xlsx', help='Output file path (default: failure_analysis_summary.xlsx)')
    
    args = parser.parse_args()
    
    # Process the results
    data = []
    for i in range(0, len(args.results), 2):
        if i + 1 >= len(args.results):
            print(f"Warning: Missing file path for method {args.results[i]}")
            continue
        
        method_name = args.results[i]
        file_path = args.results[i + 1]
        
        print(f"Processing {method_name}: {file_path}")
        analysis = parse_failure_analysis(file_path)
        
        if analysis:
            row = {
                'Method': method_name,
                'Total Instances': analysis['total_instances'],
                'Success Count': analysis['success_count'],
                'Success %': analysis['success_percent'],
                'Failure Count': analysis['failure_count'],
                'Failure %': analysis['failure_percent'],
                'regression_p2p_count': analysis['regression_p2p_count'],
                'regression_p2p_percent': analysis['regression_p2p_percent'],
                'new_feature_f2p_count': analysis['new_feature_f2p_count'],
                'new_feature_f2p_percent': analysis['new_feature_f2p_percent'],
                'both_errors_count': analysis['both_errors_count'],
                'both_errors_percent': analysis['both_errors_percent'],
            }
            data.append(row)
    
    if not data:
        print("No valid data parsed.")
        return
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Reorder columns for better readability (Excel version) with new error type columns
    excel_columns = [
        'Method', 'Total Instances',
        'Success Count', 'Success %',
        'Failure Count', 'Failure %',
        'regression_p2p_count', 'regression_p2p_percent',
        'new_feature_f2p_count', 'new_feature_f2p_percent',
        'both_errors_count', 'both_errors_percent'
    ]
    df_excel = df[excel_columns]
    
    # Rename columns for better readability in Excel
    df_excel = df_excel.rename(columns={
        'regression_p2p_count': 'Regression Errors (P2P) Count',
        'regression_p2p_percent': 'Regression Errors (P2P) %',
        'new_feature_f2p_count': 'New Feature Implementation Errors (F2P) Count',
        'new_feature_f2p_percent': 'New Feature Implementation Errors (F2P) %',
        'both_errors_count': 'Both Types of Errors Count',
        'both_errors_percent': 'Both Types of Errors %'
    })
    
    # Print the full table to console
    print("\n=== Failure Analysis Summary ===")
    print(df_excel.to_string(index=False))
    
    # Save full data to Excel
    df_excel.to_excel(args.output, index=False)
    print(f"\nSummary saved to: {args.output}")
    
    # Prepare LaTeX table with only the requested columns, adding Model column
    df_latex = df.copy()
    
    # Split Method into Method and Model columns
    # This is a simple split - adjust the logic based on your actual naming convention
    def split_method_model(method_name):
        # Simple logic: split on first hyphen, but handle cases with multiple hyphens
        parts = method_name.split('-', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            return parts[0], ''
    
    df_latex[['Method', 'Model']] = df_latex['Method'].apply(
        lambda x: pd.Series(split_method_model(x))
    )
    
    # Calculate New Feature Implementation Error as the percentage of new feature errors
    # from the new error type distribution
    df_latex['New Feature Implementation Error'] = df_latex['new_feature_f2p_percent']
    
    # Use Regression Error from the new error type distribution
    df_latex['Regression Error %'] = df_latex['regression_p2p_percent']
    
    # === Calculate relative error changes compared to RAIM method for same model ===
    # Define columns for relative changes
    rel_regression_col = 'Rel Regression Error (%)'
    rel_feature_col = 'Rel New Feature Error (%)'
    
    # Initialize new columns
    df_latex[rel_regression_col] = 0.0
    df_latex[rel_feature_col] = 0.0
    
    # Group by Model and calculate relative changes compared to RAIM
    for model, group in df_latex.groupby('Model'):
        # Find RAIM method in this model group (assuming method name contains 'RAIM' or is exactly 'RAIM')
        raim_rows = group[group['Method'].str.contains('RAIM', case=False, na=False)]
        if not raim_rows.empty:
            # Get RAIM's error rates as baseline
            raim_reg_error = raim_rows['Regression Error %'].iloc[0]
            raim_feature_error = raim_rows['New Feature Implementation Error'].iloc[0]
            
            # Calculate relative change for each method in the group
            for idx in group.index:
                if df_latex.loc[idx, 'Method'] not in raim_rows['Method'].values:
                    current_reg = df_latex.loc[idx, 'Regression Error %']
                    current_feature = df_latex.loc[idx, 'New Feature Implementation Error']
                    
                    # Calculate relative change: (current - raim) / raim * 100
                    if raim_reg_error != 0:
                        rel_reg = ((current_reg - raim_reg_error) / raim_reg_error) * 100
                    else:
                        rel_reg = 0.0
                    
                    if raim_feature_error != 0:
                        rel_feature = ((current_feature - raim_feature_error) / raim_feature_error) * 100
                    else:
                        rel_feature = 0.0
                    
                    df_latex.loc[idx, rel_regression_col] = rel_reg
                    df_latex.loc[idx, rel_feature_col] = rel_feature
    
    # Sort the dataframe: first by Model, then by Method (RAIM first if present)
    # Create a custom sort key to put RAIM at the top of each model group
    df_latex['sort_key'] = df_latex['Method'].apply(lambda x: 0 if 'RAIM' in x.upper() else 1)
    df_latex = df_latex.sort_values(['Model', 'sort_key', 'Method']).drop('sort_key', axis=1)
    
    # Reorder columns for LaTeX table with relative change columns
    latex_columns = [
        'Method', 'Model', 'Success %', 
        'Regression Error %', rel_regression_col, 
        'New Feature Implementation Error', rel_feature_col
    ]
    df_latex = df_latex[latex_columns]
    
    # Save to LaTeX table with custom formatting for relative changes (show signs)
    latex_output = args.output.replace('.xlsx', '.tex')
    # Create a custom formatter to show signs for relative changes
    def format_with_sign(x):
        if pd.isna(x):
            return ''
        return f"{'+' if x > 0 else ''}{x:.2f}"
    
    # Generate LaTeX table with formatted values
    latex_table = df_latex.to_latex(index=False, float_format="%.2f", 
                                      formatters={
                                          rel_regression_col: format_with_sign,
                                          rel_feature_col: format_with_sign
                                      })
    
    # Write the LaTeX table to file
    with open(latex_output, 'w', encoding='utf-8') as f:
        f.write(latex_table)
    print(f"LaTeX table saved to: {latex_output}")

if __name__ == "__main__":
    main()
