import os
import json
import sys

def main():
    path = os.getcwd
    if len(sys.argv) < 2:
        print("Usage: python3 query-sort.py <input_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        sys.exit(1)

    # Make sure the JSON has a top-level "data" key.
    if "data" not in json_data:
        print("JSON file does not contain a top-level 'data' key.")
        sys.exit(1)

    # Define the directory where query files will be stored.
    output_dir = "queries-alt"
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over each item in the "data" dictionary.
    past_names = []
    for item_key, item_value in json_data["data"].items():
        query_text = item_value.get("query")
        if query_text is None:
            print(f"Skipping item '{item_key}': no 'query' property found.")
            continue

        
        # Generate a safe filename.
        # Here we use os.path.basename to extract the last part of the URL.
        base_name = os.path.basename(item_key)
        # In case the key does not have a proper basename, replace unsafe characters.
        if not base_name:
            base_name = item_key.replace('https://', '').replace('/', '_')
        
        if base_name in past_names:
            base_name = base_name.join("a")
        past_names.append(base_name)

        # Append the .sparql extension.
        output_filename = f"{base_name}.sparql"
        full_output_path = os.path.join(output_dir, output_filename)

        try:
            with open(full_output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(query_text)
            print(f"Created file: {output_filename}")
        except Exception as e:
            print(f"Error writing {output_filename}: {e}")


if __name__ == "__main__":
    main()
