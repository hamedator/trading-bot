import ast

def update_config_value(file_path, key, value):
    """
    Updates or adds a key-value pair in a Python config file.
    Tries to parse the value to its correct Python type using ast.literal_eval,
    otherwise treats it as a string.

    Args:
        file_path (str): Path to the config file to update.
        key (str): The config key to update or add.
        value (str): The new value as a string.
    """
    try:
        # Try to interpret the string value as a Python literal (int, float, bool, list, dict, etc.)
        parsed_value = ast.literal_eval(value)
    except Exception:
        # If parsing fails, keep the value as a string
        parsed_value = value

    lines = []
    found = False

    # Read existing config file lines
    with open(file_path, 'r') as f:
        for line in f:
            # Check if line starts with the key to update
            if line.strip().startswith(f"{key} ="):
                # Replace the line with the new key-value pair
                new_line = f"{key} = {repr(parsed_value)}\n"
                lines.append(new_line)
                found = True
            else:
                lines.append(line)

    # If key was not found, append it at the end
    if not found:
        lines.append(f"{key} = {repr(parsed_value)}\n")

    # Write updated lines back to the file
    with open(file_path, 'w') as f:
        f.writelines(lines)
