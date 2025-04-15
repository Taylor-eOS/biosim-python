filenames = ['genome.py', 'brain.py', 'individual.py', 'simulation.py', 'run.py']
output_file = 'combined_code.txt'

with open(output_file, 'w') as outfile:
    for filename in filenames:
        try:
            with open(filename, 'r') as infile:
                content = infile.read().rstrip('\n')
            outfile.write(f"{filename}\n```\n{content}\n```\n\n")
        except FileNotFoundError:
            print(f"Warning: {filename} not found, skipping...")
print(f"Combined code written to {output_file}")
