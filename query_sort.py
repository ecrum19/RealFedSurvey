import os
import json
import sys

## TODO: Split REGULAR and NO SERVICE clauses into separate functions
## TODO: Look into using rdflib-sparql parser (https://github.com/RDFLib/rdflib-sparql/blob/master/rdflib_sparql/parser.py)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 query-sort.py <input_json_file> <output_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_directory = sys.argv[2]
    # checks input file validity
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        sys.exit(1)

    working_output_dir = os.path.join(output_directory)
    # checks if specified output path is valid
    if not os.path.isdir(working_output_dir):
        print(f"Error: {output_directory} does not exist.")
        sys.exit(1)

    # Make sure the JSON has a top-level "data" key.
    if "data" not in json_data:
        print("JSON file does not contain a top-level 'data' key.")
        sys.exit(1)

    # Define the directory where query files will be stored (w/ + w/o SERVICE description).
    experiment = os.path.basename(working_output_dir)
    output_dir_s = os.path.join(experiment, "input", "queries-s")
    output_dir_ns = os.path.join(experiment, "input", "queries-ns")
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
        brace_count = 0
        curr_service = False
        for line in split_query:
            # remove SERVICE description line
            if "SERVICE" in line:
                line_s = line.split(" ")
                for s in line_s:
                    if "<" in s:
                        source = s.replace("<", "").replace(">", "")
                        if "{" in source:
                            source = source[:-1]
                ns_query_source += " %s" % source
                brace_count += 1
                curr_service = True
            
            # case where both brackets are in same line
            elif "{" in line and "}" in line and curr_service:
                ns_query_text += "%s\n" % line

            # count bracket offset
            elif "{" in line and curr_service:
                brace_count += 1
                ns_query_text += "%s\n" % line

            # find closing bracket for SERVICE clause
            elif "}" in line and curr_service:
                brace_count -= 1
                if brace_count > 0:
                    ns_query_text += "%s\n" % line
                else:
                    curr_service = False
                    brace_count = 0
            
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

        # for with SERVICE descriptions
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
