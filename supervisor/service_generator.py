import argparse

from jinja2.loaders import FileSystemLoader
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from jinja2 import Environment, FileSystemLoader

def main(fname):
    env = Environment(
        loader=FileSystemLoader('./templates', encoding='utf-8')
    )

    with open(fname, 'r') as ifp:
        data = load(ifp, Loader=Loader)
        global_vars = data['global_vars']
        for row in data['services']:
            tmpl = env.get_template(row['template']['src'])
            with open(f'./available/{row["template"]["dest"]}', 'w') as ofp:
                print(f'Generate: {row["template"]["dest"]}')
                ofp.write(tmpl.render({**row['vars'], **global_vars})+'\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Supervisor service file generator')
    parser.add_argument('configfile', help='Config filename')
    args = parser.parse_args()
    main(args.configfile)
