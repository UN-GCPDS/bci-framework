import os

files = os.listdir()

files = filter(lambda s:s.endswith('.svg'), files)
files = filter(lambda s:not s.startswith('__'), files)
files =  sorted(files)

W = 400
H = 100
COLOR = '#4dd0e1'

#----------------------------------------------------------------------
def replace_color(file, old, new):
    """"""

    with open(file, 'r') as file_r:
        content = file_r.read()


    colors = [old] + [''.join(list(old)[:i] + ['\\\n'] + list(old)[i:]) for i in range(1, 7)]
    for c in colors:
        content = content.replace(c, new)

    with open(file, 'w') as file_w:
        file_w.write(content)



for file in files:

    #


    replace_color(file, '#0000ff', COLOR)
    command = f'inkscape -z -e {file.replace(".svg", ".png")} -w {W} -h {H} {file}'
    os.system(command)
    replace_color(file, COLOR, '#0000ff')

os.system('convert -dispose 2 -delay 50 *.png connecting.gif')
os.system('rm *.png')
# files
