import subprocess
import argparse
import sys
import yaml

def run_script(script_name, args):
    """Helper function to run a script with the provided arguments"""
    # print current directory
    command = ['python', script_name]
    for key, value in args.items():
        if value is None:
            continue
        if key.startswith('__NO_ARG_NAME__'):
            if not isinstance(value, list):
                value = [value]
            command.extend([str(v) for v in value])
        elif isinstance(value, list):
            command.extend([f"--{key.replace('_', '-')}", ' '.join(map(str, value))])
        elif value is not None:
            command.extend([f"--{key.replace('_', '-')}", str(value)])
    print(f"Running {' '.join(command)}")
    subprocess.run(command, check=True)

def main(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    for step in config['steps']:
        script = step['script']
        args = step['args']
        run_script(script, args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build an audio processing pipeline.")
    parser.add_argument("config", type=str, help="Path to the pipeline configuration file (YAML)")

    args = parser.parse_args()
    main(args.config)
