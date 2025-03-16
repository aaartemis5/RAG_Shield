import os
import json

def combine_json_files(directory, output_file):
    # Initialize a list to hold combined data
    combined_data = []

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            # Open and load the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # If the JSON file contains a list, extend the combined_data list
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    # If the JSON file contains a single object, append it to the combined_data list
                    combined_data.append(data)

    # Write the combined data to a new JSON file as an array
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=4)

    print(f"Combined data has been written to {output_file}")

# Example usage
if __name__ == "__main__":
    # Directory containing the JSON files
    input_directory = './'
    
    # Output file where the combined JSON will be saved
    output_file = 'data.json'
    
    # Combine the JSON files
    combine_json_files(input_directory, output_file)