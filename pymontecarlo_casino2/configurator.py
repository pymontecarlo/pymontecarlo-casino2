""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.program.configurator import Configurator, FileType

# Globals and constants variables.

class Casino2Configurator(Configurator):

    def prepare_parser(self, parser, program=None):
        parser.description = 'Configure Casino 2.'

        kwargs = {}
        kwargs['metavar'] = 'FILE'
        kwargs['help'] = 'Path to executable of Casino 2'
        if program is not None:
            kwargs['default'] = program.executable
            kwargs['help'] += ' (current: {})'.format(program.executable)
        else:
            kwargs['required'] = True
        kwargs['type'] = FileType
        parser.add_argument('--executable', **kwargs)

    def create_program(self, namespace, clasz):
        return clasz(namespace.executable)

    @property
    def fullname(self):
        return 'Casino 2'
