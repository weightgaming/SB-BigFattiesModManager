import argparse

from ModManager import SBModManager

parser = argparse.ArgumentParser(description='Creates instances and loads mods for starbound clients')
parser.add_argument('-c', '--create', action='store_true',
                    help='Creates a new instance of starbound and loads a specfied mod pack')
parser.add_argument('-l', '--load', action='store_true',
                    help='Load a specified mod or modpack')
parser.add_argument('-i', '--instance', type=str, default=None,
                    help='Instance Name')
parser.add_argument('-n', '--name', type=str, default=None,
                    help='Mod name')
parser.add_argument('-p', '--pack', type=str, default=None,
                    help='Modpack name')
parser.add_argument('-k' '--key', type=str, default=None,
                    help='Modpack Id')


def main():
    args = parser.parse_args()

    if args.instance is not None:
        manager = SBModManager()
        if args.create:
            manager.create_instance(args.instance, args.k__key)
        elif args.load:
            if args.pack is not None or args.k__key is not None:
                manager.load_mod_pack(args.instance, mod_pack_id=args.k__key, mod_pack_name=args.pack)
            else:
                manager.download_mod(args.instance, mod_name=args.name)


if __name__ == '__main__':
    main()
