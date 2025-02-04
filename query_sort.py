import os
import json
import sys

def main():
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

    # Define the directory where query files will be stored (w/ + w/o SERVICE description).
    output_dir_s = os.path.join("real-fed-init", "input", "queries-s")
    output_dir_ns = os.path.join("real-fed-init", "input", "queries-ns")
    os.makedirs(output_dir_s, exist_ok=True)
    os.makedirs(output_dir_ns, exist_ok=True)



    # Iterate over each item in the "data" dictionary.
    past_names = []
    for item_key, item_value in json_data["data"].items():
        s_query_text = item_value.get("query")
        s_query_source = item_value.get("target")

        if s_query_text is None:
            print(f"Skipping item '{item_key}': no 'query' property found.")
            continue

        
        # generate no SERVICE description query
        ns_query_source = s_query_source
        split_query = s_query_text.split("\n")
        ns_query_text = ""
        squigle = None
        level = 0
        curr_service = False
        for line in split_query:
            # remove service description line
            if "SERVICE" in line:
                line_s = line.split(" ")
                source = line_s[1].replace("<", "").replace(">", "")
                ns_query_source += " %s" % source
                squigle = 1
                level = 0
                curr_service = True
            
            # case where both brackets are in same line
            elif "{" in line and "}" in line:
                ns_query_text += "%s\n" % line

            # for incase there is an inner clause
            elif "{" in line:
                squigle = 0
                level += 1
                ns_query_text += "%s\n" % line

            # close the inner clause
            elif "}" in line and squigle == 0:
                if level > 0:
                    level -= 1
                    ns_query_text += "%s\n" % line
                elif curr_service and curr_service:
                    squigle = 1
                    ns_query_text += "%s\n" % line
                else:
                    ns_query_text += "%s\n" % line
            
            # the close of the service clause
            elif "}" in line and squigle == 1 and curr_service:
                squigle = 0
                curr_service = False

            # for normal query lines
            else:
                ns_query_text += "%s\n" % line


        # Generate a safe filename.
        # Here we use os.path.basename to extract the last part of the URL.
        base_name = os.path.basename(item_key)

        # In case the key does not have a proper basename, replace unsafe characters.
        if not base_name:
            base_name = item_key.replace('https://', '00').replace('/', '_')
        
        # Case where file name is repeated
        if base_name in past_names:
            base_name = base_name.join("a")
        past_names.append(base_name)

        # Append the .sparql extension.
        s_output_filename = f"{base_name}.sparql"
        ns_output_filename = f"{base_name}_ns.sparql"
        s_full_output_path = os.path.join(output_dir_s, s_output_filename)
        ns_full_output_path = os.path.join(output_dir_ns, ns_output_filename)

        # for with SERVICE DESCRIPTIONS
        try:
            with open(s_full_output_path, 'w', encoding='utf-8') as out_file:
                out_file.write("# Datasources: %s\n%s" % (s_query_source, s_query_text))
            # print(f"Created file: {output_filename}")
        except Exception as e:
            print(f"Error writing {s_output_filename}: {e}")

        # for without SERVICE descriptions
        try:
            with open(ns_full_output_path, 'w', encoding='utf-8') as out_file:
                out_file.write("# Datasources: %s\n%s" % (ns_query_source, ns_query_text))
            # print(f"Created file: {output_filename}")
        except Exception as e:
            print(f"Error writing {ns_output_filename}: {e}")


if __name__ == "__main__":
    main()
