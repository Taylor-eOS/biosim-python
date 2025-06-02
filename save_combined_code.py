filenames = ['genome.py', 'brain.py', 'individual.py', 'simulation.py', 'run.py']
output_file = 'combined_code.txt'

def remove_imports(lines):
    i = 0
    for line in lines:
        if line.startswith('import') or line.startswith('from'):
            i += 1
        else:
            break
    return lines[i:]

with open(output_file, 'w') as outfile:
    for filename in filenames:
        try:
            with open(filename, 'r') as infile:
                lines = infile.readlines()
            lines = remove_imports(lines)
            content = ''.join(lines).lstrip('\n').rstrip('\n')
            outfile.write(f"{filename}\n```\n{content}\n```\n\n")
        except FileNotFoundError:
            print(f"Warning: {filename} not found, skipping...")
print(f"Combined code written to {output_file}")
