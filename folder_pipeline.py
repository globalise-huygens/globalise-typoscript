import pandas as pd
import os
import sys
import numpy as np

def build_mapping(df):
    output = {}
    for i, row in df.iterrows():
        output[df.loc[i, "File Name"]] = df.loc[i, "inv_no"]
    return output

def clean_nan_rows(df):
    condition = df.iloc[:, 1].apply(identify_document_name_rows) & df.iloc[:, 2:].isna().all(axis=1)
    output = df[~condition]
    return output

def identify_document_name_rows(cell):
    if isinstance(cell, str):
        if ".png" in cell or ".jpg" in cell:
            return True
    return False

def safe_split_page_nos(row):
    try:
        start, end = split_page_nos(row)
        return start, end
    except Exception as e:
        print(f"Error processing row: {row}, Error: {e}")
        return None, None

def split_page_nos(cell):
    dividers = [' a ', '-', '—']
    if isinstance(cell, str):
        for divider in dividers:
            if divider in cell:
                parts = [part.strip() for part in cell.split(divider)]
                if len(parts) == 2:
                    return parts[0], parts[1]
        return cell, cell
    return str(cell), str(cell)

def rename_col_by_index(dataframe, index_mapping):
    dataframe.columns = [index_mapping.get(i, col) for i, col in enumerate(dataframe.columns)]
    return dataframe

def add_invno(value, png_mapping):
    return png_mapping.get(value, None)

def process_file(input_file, output_folder, png_mapping):
    df = pd.read_excel(input_file, header=None)
    print(f"Initial columns in {input_file}: {df.columns}")  # Debugging output
    df = clean_nan_rows(df)
    
    # Map columns
    new_column_mapping = {0: 'transkribus_no', 1: 'scan_name', 2: "og_page_no", 3: "doc_name"}
    df = rename_col_by_index(df, new_column_mapping)
    
    # Validate column presence
    if 'og_page_no' not in df.columns:
        raise KeyError(f"Expected column 'og_page_no' not found in file {input_file}. Check file format.")
    
    df['start_page_no'], df['end_page_no'] = zip(*df['og_page_no'].apply(safe_split_page_nos))
    df['na_inv_no'] = df['scan_name'].apply(add_invno, args=(png_mapping,))
    
    output_file = os.path.join(output_folder, os.path.basename(input_file))
    df.to_excel(output_file, index=False)
    print(f"Processed and saved: {output_file}")


def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_folder> <output_folder> <png_mapping_csv>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    png_mapping_csv = sys.argv[3]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    png_mapping_df = pd.read_csv(png_mapping_csv)
    png_mapping = build_mapping(png_mapping_df)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.xlsx'):
            input_file = os.path.join(input_folder, file_name)
            process_file(input_file, output_folder, png_mapping)

if __name__ == "__main__":
    main()
