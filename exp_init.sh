#!/bin/bash

# Loop over directories matching the pattern "survey-exp-<number>"
max=0
for item in *; do
    # Check if the item is a directory
    if [[ -d "$item" ]]; then
        # Check if the directory name matches the pattern survey-exp-[number]
        if [[ "$item" =~ ^survey-exp-([0-9]+)$ ]]; then
            # Extract the number from the directory name
            num=${BASH_REMATCH[1]}
            # Update max if this number is greater than the current max
            if (( num > max )); then
                max=$num
            fi
        fi
    fi
done
# Determine the next number (if max is 0, this will be 1)
next=$((max + 1))

# Initialize the jbr experiment with new directory name
npm run jbr -- init -c sparql-custom survey-exp-$next


# TODO: copy jbr-combinations-master.json ++ jbr-experiment_master.json.template to created directory (with proper names)

# add queries to new experiment inputs
python3 query_sort.py sib-swiss-federated-queries.json survey-exp-$next


# TODO: change directory to /survery-exp-n
# TODO: jbr set-hook hookSparqlEndpoint sparql-endpoint-comunica
# TODO: jbr generate-combinations
# TODO: jbr prepare


# TODO: jbr run

