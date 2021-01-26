import zlib


def action_control(file, control_list):

    with open(file, 'rb') as fr:
        data = zlib.decompress(fr.read())

    with open('control_file_copy.py', 'w') as fw:
        fw.write(data.decode())

    import control_file_copy

    cnt = control_file_copy.Control(control_list)
    cnt.action()
