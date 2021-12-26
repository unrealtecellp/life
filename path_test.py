import os

basedir = os.path.abspath(os.path.dirname(__file__))

print(f'{"#"*80}Base directory:\n{basedir}\n{"#"*80}')

print (os.path.join(basedir, 'download', 'text'))