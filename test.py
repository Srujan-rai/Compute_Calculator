import json

def load_index(file_path):
    
    with open(file_path, 'r') as file:
        return json.load(file)


def get_index(variable_name, indices):
    
    return indices.get(variable_name, None)


# Load the index file
index_file = "index.json"
indices = load_index(index_file)

# Query the index
machine_family_index = get_index("General Purpose", indices)
series_index = get_index("N1", indices)
machine_type_index = get_index("c4a-highcpu-72", indices)

print(f"Machine Family Index: {machine_family_index}")
print(f"Series Index: {series_index}")
print(f"Machine Type Index: {machine_type_index}")
