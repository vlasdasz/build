import os
import re
import sys


# Name of the crate to update
CRATE_NAME = sys.argv[1]

# New version number to use
NEW_VERSION = sys.argv[2]

# Find all Cargo.toml files in the current directory and its subdirectories
cargo_toml_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file == "Cargo.toml":
            cargo_toml_files.append(os.path.join(root, file))

# Update the version number in each Cargo.toml file
for cargo_toml_path in cargo_toml_files:
    print(f"Updating {cargo_toml_path}...")

    # Load the Cargo.toml file as a string
    with open(cargo_toml_path, "r") as cargo_toml_file:
        cargo_toml_str = cargo_toml_file.read()

    # Use a regular expression to find and replace the version number for the specified crate
    regex_pattern = fr"({CRATE_NAME}\s*=\s*\"(\d+\.\d+\.\d+)\"\s*)"
    lines = [line.rstrip() for line in cargo_toml_str.split("\n")]
    modified_lines = []
    num_replacements = 0
    for line in lines:
        modified_line, replacements = re.subn(
            regex_pattern,
            f'{CRATE_NAME} = "{NEW_VERSION}"',
            line,
            count=1,
        )
        modified_lines.append(modified_line)
        num_replacements += replacements
    cargo_toml_str = "\n".join(modified_lines)

    # Write the updated Cargo.toml file back to disk
    with open(cargo_toml_path, "w") as cargo_toml_file:
        cargo_toml_file.write(cargo_toml_str)

    # Log the number of replacements and the line number of the first match
    if num_replacements > 0:
        match = re.search(regex_pattern, cargo_toml_str)
        match_line_num = cargo_toml_str.count("\n", 0, match.start()) + 1
        print(f"  {num_replacements} replacements made on line {match_line_num}")

print("Done.")