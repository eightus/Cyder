import operator

from vfssh.vfs.Command import Command
from vfssh.vfs.error import VFSError
from vfssh.vfs.fs_directory import FolderObject
from vfssh.vfs.fs_object import FileObject
from math import ceil
import copy

class ls(Command):
    def __init__(self, vfs=None):
        super().__init__('ls')
        self.set_vfs(vfs)
        self.param_false = ['a', 'l', 'F']

    def process(self, **kwargs):
        full, cmd, args, obj = kwargs['full'], kwargs['cmd'], kwargs['args'], kwargs['obj']
        width = obj._chan.get_terminal_size()[0]
        if len(args) == 0:
            self.write(self.default(width))
            return None
        try:
            fmt_args = self.arg_check(args)
        except VFSError.InvalidArgument as e:
            self.write("ls: invalid option -- '{}'\n".format(e.extra.get('arg')))
            return
        except VFSError.MissingParameter as e:
            self.write("ls: parameter not specified -- '{}'".format(e.extra.get('arg')))
            return

        if fmt_args.get('a', False) and not fmt_args.get('l', False):
            self.write(self.default(width, view_hidden=True))
        elif fmt_args.get('a', False) and fmt_args.get('l', False):
            #  TODO: ls -al command
            self.write(self.long_listing_format(view_hidden=True))
            pass
        elif not fmt_args.get('a', False) and fmt_args.get('l', False):
            #  TODO: ls -l command
            self.write(self.long_listing_format(view_hidden=False))
            pass

        return None

    def long_listing_format(self, view_hidden=False):
        block_size = 0
        output = ''
        if view_hidden:
            file_list = [copy.copy(self.vfs.head), copy.copy(self.vfs.parse_input('..'))]
            file_list[0].name, file_list[1].name = '.', '..'
            file_list.extend(sorted([x for x in self.vfs.head.list_obj()], key=operator.attrgetter('name')))
        else:
            file_list = sorted([x for x in self.vfs.head.list_obj() if not x.name.startswith('.')], key=str.lower)

        space_count = 1
        space_owner = max([len(i.owner) for i in file_list]) + 1
        space_group = max([len(i.group) for i in file_list]) + 1
        space_size = len(str(max([i.size for i in file_list]))) + 1
        for i in file_list:
            block_size += i.size
            count = len(i.list_obj('name')) if type(i) == FolderObject else 1
            if len(str(count)) > space_count:
                print(True)
                space_count = len(str(count))
            #  TODO: Timestamp format (take from eskibana)
            timestamp = '{m:4}{d:3}{t:6}'.format(m='Dec', d='15', t='15:03')
            output += "{attributes:11}{count:>{space_count}}{owner:>{space_owner}}{group:>{space_group}}" \
                      "{size:>{space_size}}{timestamp:>14}{name}\n".format(
                       attributes=i.attributes, count=str(count), space_count=space_count, owner=i.owner,
                       space_owner=space_owner, group=i.group, space_group=space_group, size=str(i.size),
                       space_size=space_size, timestamp=timestamp, name=i.name)
        return 'total {}\n'.format(ceil(block_size/1024)) + output

    def default(self, width, view_hidden=False):
        """
        Reference: https://stackoverflow.com/questions/25026556/output-list-like-ls

        :param view_hidden: Show Hidden Files
        :param width: Width of terminal
        :return: Terminal output
        """

        if view_hidden:
            file_list = ['.', '..']
            file_list.extend(sorted([x.name for x in self.vfs.head.list_obj()], key=str.lower))
        else:
            file_list = sorted([x.name for x in self.vfs.head.list_obj() if not x.name.startswith('.')], key=str.lower)
        if len(file_list) == 0:
            return None
        output = ''
        min_chars_between = 2
        usable_term_width = width - 2
        min_element_width = min(len(x) for x in file_list)
        max_element_width = max(len(x) for x in file_list)
        if max_element_width >= usable_term_width:
            ncol = 1
            col_widths = [1]
        else:
            ncol = int(min(len(file_list), usable_term_width/min_element_width))
            while True:
                col_widths = [max(len(x) + min_chars_between
                              for j, x in enumerate(file_list) if j % ncol == i)
                              for i in range(ncol)]
                if sum(col_widths) <= usable_term_width:
                    break
                else:
                    ncol -= 1
        for i, x in enumerate(file_list):
            output += x.ljust(col_widths[i % ncol])
            if i == len(file_list) - 1:
                output += '\n'
            elif (i+1) % ncol == 0:
                output += '\n'
        return output

