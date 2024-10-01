from __future__ import annotations

import os
import sys
import warnings
from collections.abc import Mapping
from typing import Any, ClassVar

import django.core.management
import django.core.management.commands.shell


class Command(django.core.management.commands.shell.Command):
    shells = ['ptpython'] + django.core.management.commands.shell.Command.shells

    ptpython_autocomplete_while_typing_enabled_by_default: ClassVar[bool] = False
    ptpython_history_search_enabled_by_default: ClassVar[bool] = True
    ptpython_mouse_enabled_by_default: ClassVar[bool] = False
    ptpython_show_function_signatures_enabled_by_default: ClassVar[bool] = True
    ptpython_code_color_scheme: ClassVar[str] = 'monokai'
    ptpython_title: ClassVar[str] = 'Django'
    ptpython_title_env_var: ClassVar[str] = 'DJANGO_SHELL_PTPYTHON_TITLE'

    def add_arguments(self, parser: django.core.management.CommandParser) -> None:
        super().add_arguments(parser)

        ptpython_only_help_text: str = '(Ptpython only)'

        parser.add_argument(
            (
                '--ptpython-no-autocomplete-while-typing'
                if self.ptpython_autocomplete_while_typing_enabled_by_default
                else '--ptpython-autocomplete-while-typing'
            ),
            dest='ptpython_autocomplete_while_typing',
            action=(
                'store_false'
                if self.ptpython_autocomplete_while_typing_enabled_by_default
                else 'store_true'
            ),
            help=(
                'Autocomplete while typing'
                ' instead of requiring to press Tab to show autocompletion menu {ptpython_only}.'
                " Conflicts with 'history search'.".format(
                    ptpython_only=ptpython_only_help_text,
                )
            ),
        )
        parser.add_argument(
            (
                '--ptpython-no-history-search'
                if self.ptpython_history_search_enabled_by_default
                else '--ptpython-history-search'
            ),
            dest='ptpython_history_search',
            action=(
                'store_false' if self.ptpython_history_search_enabled_by_default else 'store_true'
            ),
            help=(
                '{action} history search {ptpython_only}.'
                " Conflicts with 'autocomplete while typing'.".format(
                    action=(
                        'Disable' if self.ptpython_history_search_enabled_by_default else 'Enable'
                    ),
                    ptpython_only=ptpython_only_help_text,
                )
            ),
        )
        parser.add_argument(
            (
                '--ptpython-no-mouse'
                if self.ptpython_mouse_enabled_by_default
                else '--ptpython-mouse'
            ),
            dest='ptpython_mouse',
            action='store_false' if self.ptpython_mouse_enabled_by_default else 'store_true',
            help=(
                '{action} mouse support {ptpython_only}.'.format(
                    action='Disable' if self.ptpython_mouse_enabled_by_default else 'Enable',
                    ptpython_only=ptpython_only_help_text,
                )
            ),
        )
        parser.add_argument(
            (
                '--ptpython-hide-function-signatures'
                if self.ptpython_show_function_signatures_enabled_by_default
                else '--ptpython-show-function-signatures'
            ),
            dest='ptpython_show_function_signatures',
            action=(
                'store_false'
                if self.ptpython_show_function_signatures_enabled_by_default
                else 'store_true'
            ),
            help=(
                '{action} function signatures {ptpython_only}.'.format(
                    action=(
                        'Hide'
                        if self.ptpython_show_function_signatures_enabled_by_default
                        else 'Show'
                    ),
                    ptpython_only=ptpython_only_help_text,
                )
            ),
        )
        parser.add_argument(
            '--ptpython-code-color-scheme',
            dest='ptpython_code_color_scheme',
            type=str,
            default=self.ptpython_code_color_scheme,
            metavar='COLOR_SCHEME',
            help='Color scheme to use for Python code {ptpython_only}.'.format(
                ptpython_only=ptpython_only_help_text
            ),
        )
        parser.add_argument(
            '--ptpython-title',
            dest='ptpython_title',
            type=str,
            default=os.getenv(self.ptpython_title_env_var) or self.ptpython_title,
            metavar='TITLE',
            help=(
                'Title to be displayed in the terminal {ptpython_only}.'
                ' If this is not provided, the {env_var} environment variable will be used,'
                ' or the default {default!r}.'.format(
                    ptpython_only=ptpython_only_help_text,
                    env_var=self.ptpython_title_env_var,
                    default=self.ptpython_title,
                )
            ),
        )
        parser.add_argument(
            '--ptpython-show-useless-warnings',
            dest='ptpython_show_useless_warnings',
            action='store_true',
            help='Do not hide useless warnings {ptpython_only}.'.format(
                ptpython_only=ptpython_only_help_text
            ),
        )

    def ptpython(self, options: Mapping[str, Any]) -> None:
        import ptpython.repl

        if not sys.warnoptions and not options['ptpython_show_useless_warnings']:
            warnings.filterwarnings(
                action='ignore',
                message=r'^coroutine .* was never awaited$',
                category=RuntimeWarning,
                # Source:
                #   https://github.com/python/cpython/blob/v3.10.14/Lib/asyncio/__main__.py#L84-L87
            )

        def configure_ptpython(repl: ptpython.repl.PythonRepl) -> None:
            """
            Configure the Ptpython REPL (Read–Eval–Print Loop).

            Example:
                https://github.com/prompt-toolkit/ptpython/blob/3.0.28/examples/ptpython_config/config.py
            """
            repl.complete_while_typing = options['ptpython_autocomplete_while_typing']
            repl.enable_history_search = options['ptpython_history_search']
            repl.enable_mouse_support = options['ptpython_mouse']
            repl.show_signature = options['ptpython_show_function_signatures']

            if options['ptpython_code_color_scheme']:
                repl.use_code_colorscheme(options['ptpython_code_color_scheme'])

            if options['ptpython_title']:
                repl.title = options['ptpython_title']

        ptpython.repl.embed(globals(), locals(), configure=configure_ptpython)
