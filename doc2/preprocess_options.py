from six import iteritems


def process_options(root, file_name, iline, line):
    file_path = root + '/' + file_name
    
    embed_num_indent = line.find('.. embed-options-table')

    if 'embed-options-table-method' in line:
        type_ = 'methods'
    elif 'embed-options-table-problem' in line:
        type_ = 'problems'
    else:
        raise Exception('embed-options-table is an invalid name')

    if line[:embed_num_indent] != ' ' * embed_num_indent:
        return line

    split_line = line.replace(' ', '').split('::')
    if len(split_line) != 2:
        raise Exception('Invalid format for embed-options-table in file {} line {}'.format(
            file_path, iline + 1))

    class_name = split_line[1]

    exec('from smt.{} import {}'.format(type_, class_name), globals())
    exec('sm_class = {}'.format(class_name), globals())

    sm = sm_class()
    options = sm.options

    outputs = []
    for option_name, option_data in iteritems(options._declared_entries):
        name = option_name
        default = option_data['default']
        values = option_data['values']
        types = option_data['types']
        desc = option_data['desc']

        if types is not None:
            if not isinstance(types, (tuple, list)):
                types = (types,)

            types = [type_.__name__ for type_ in types]

        if values is not None:
            if not isinstance(values, (tuple, list)):
                values = (values,)

            values = [value for value in values]

        outputs.append([name, default, values, types, desc])

    replacement_lines = []
    replacement_lines.append(' ' * embed_num_indent
        + '.. list-table:: List of options\n')
    replacement_lines.append(' ' * embed_num_indent
        + ' ' * 2 + ':header-rows: 1\n')
    replacement_lines.append(' ' * embed_num_indent
        + ' ' * 2 + ':widths: 15, 10, 20, 20, 30\n')
    replacement_lines.append(' ' * embed_num_indent
        + ' ' * 2 + ':stub-columns: 0\n')
    replacement_lines.append('\n')
    replacement_lines.append(' ' * embed_num_indent
        + ' ' * 2 + '*  -  Option\n')
    replacement_lines.append(' ' * embed_num_indent
        + ' ' * 2 + '   -  Default\n')
    replacement_lines.append(' ' * embed_num_indent
        + ' ' * 2 + '   -  Acceptable values\n')
    replacement_lines.append(' ' * embed_num_indent
        + ' ' * 2 + '   -  Acceptable values\n')
    replacement_lines.append(' ' * embed_num_indent
        + ' ' * 2 + '   -  Description\n')

    for output in outputs:
        for entry in [output[0]]:
            replacement_lines.append(' ' * embed_num_indent
                + ' ' * 2 + '*  -  %s\n' % entry)
        for entry in output[1:]:
            replacement_lines.append(' ' * embed_num_indent
                + ' ' * 2 + '   -  %s\n' % entry)

    return replacement_lines
