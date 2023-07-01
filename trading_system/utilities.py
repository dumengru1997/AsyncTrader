import subprocess


def run_command(command):
    """ execute cmd command """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Implementing real-time output
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            try:
                print(output.strip().decode('utf-8'))
            except UnicodeDecodeError:
                print(output.strip().decode('gbk'))

    rc = process.poll()
    if rc != 0:
        print(f"Error occurred while executing command: {command}")
        # error code print out
        print(f"Return code: {rc}")


def print_red(input_str: str):
    """ output display in red font """
    print(f"\n\033[1;31m> {input_str}\033[0m")


def underscore_to_camel(s):
    """  """
    components = s.split('_')
    return ''.join(x.title() for x in components)

