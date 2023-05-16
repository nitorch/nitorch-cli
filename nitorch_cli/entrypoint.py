"""Implementation of the command-line entry point for nitorch tools."""
import sys
import yaml
import importlib
import os.path


_help = r"""[nitorch] Command-line tools

usage:
    nitorch <COMMAND>
    nitorch help <COMMAND>
        
"""


def help(registry):
    """Help for the generic 'nitorch' command.
    List all registered commands.
    """

    commandnames = sorted(registry.keys())
    length = max(len(name) for name in commandnames)
    nb_col = 76//(length+1)
    commandlist = "    "
    for d, name in enumerate(commandnames):
        commandlist += ('{:<' + str(length) + 's} ').format(name)
        if (d+1) % nb_col == 0:
            commandlist += '\n    '
    commandlist += '\n'

    return _help + commandlist


def nitorch(args=None):
    """Generic parser for nitorch commands.
    This function calls the appropriate subcommand if it is registered.
    """

    args = args or sys.argv[1:]  # remove command name
    registry = parse_registry()

    if not args:
        print(help(registry))
        return
    tag, *args = args
    if tag == 'help':
        if args:
            if args[0] in registry.keys():
                command = load_function(registry[args[0]])
                return command(['-h'])
            else:
                print(help)
                print(f'[ERROR] Unknown command "{args[0]}"', file=sys.stderr)
                return 1
        else:
            print(help(registry))
            return
    if tag in ('-h', '--help'):
        print(help(registry))
        return
    if tag not in registry.keys():
        print(help(registry))
        print(f'[ERROR] Unknown command "{tag}"', file=sys.stderr)
        return 1
    command = load_function(registry[args[0]])
    return command(args)


def parse_registry():
    this_folder = os.path.dirname(__file__)
    path_registry = os.path.join(this_folder, 'registry.yml')
    if not os.path.exists(path_registry):
        raise ValueError('Cannot find registry')
    with open(path_registry, 'r') as file:
        registry_yml = yaml.safe_load(file)

    registry = {}
    for module, commands in registry_yml.items():
        for command in commands:
            if isinstance(command, dict):
                command, path_to_entrypoint = next(command.items().__iter__())
            else:
                path_to_entrypoint = f'cli.{command}.entrypoint'
            path_to_entrypoint = module + '.' + path_to_entrypoint
            registry[command] = path_to_entrypoint
    return registry


def load_function(path):
    *path, function = path.split('.')
    path = '.'.join(path)
    module = importlib.import_module(path)
    return getattr(module, function)