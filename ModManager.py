import shutil
from datetime import datetime
from pathlib import Path

import yaml
from gridfs import GridFSBucket
from pymongo import MongoClient


class SBModeManager:
    sb_install_location: str
    instance_directory: str = 'instances'

    client: MongoClient = None
    database: str = 'sb-catalog'
    mods_collection: str = 'mods'
    packs_collection: str = 'packs'

    def __init__(self, config_file: str = 'config.ymal'):
        with open(config_file, 'r') as stream:
            config: dict = yaml.safe_load(stream)['config']

            self.sb_install_location = config['starbound install directory']
            self.client = MongoClient(config['mongo db url'])

            if 'instance directory location' in config.keys():
                self.instance_directory = config['instance directory location']

    def get_mods(self):
        return list(self.client[self.database][self.mods_collection].find())

    def get_mod_packs(self):
        return list(self.client[self.database][self.packs_collection].find())

    def create_instance(self, instance_name: str, mod_pack_id=None):
        dest: Path = Path(self.instance_directory) / instance_name
        mod_path: Path = dest / 'mods'

        if dest.exists() or not Path(self.sb_install_location).exists():
            return False

        shutil.copytree(self.sb_install_location, str(dest))
        shutil.rmtree(mod_path)
        mod_path.mkdir()

        if mod_pack_id is not None:
            self.load_mod_pack(instance_name, mod_pack_id=mod_pack_id)

        return True

    def create_mod_pack(self, mod_pack_name: str, pack_mods: list, use_mod_name=False):
        db = self.client[self.database]

        ids = []
        if use_mod_name:
            for mod in db[self.mods_collection].find({'name': {'$in': pack_mods}}):
                ids.append(mod['_id'])
        else:
            ids = pack_mods

        return db[self.packs_collection].update_one({'name': mod_pack_name}, {'$set': {'name': mod_pack_name, 'last_modified': datetime.now().timestamp(), 'mods': ids}}, upsert=True)

    def load_mod_pack(self, instance_name: str, mod_pack_id=None, mod_pack_name=None):
        if mod_pack_id is not None:
            pack_filter = {'_id': mod_pack_id}
        elif mod_pack_name is not None:
            pack_filter = {'name': mod_pack_name}
        else:
            return False

        mod_pack = self.client[self.database][self.packs_collection].find_one(pack_filter)
        if mod_pack is None:
            return False

        for mod_id in mod_pack['mods']:
            self.download_mod(instance_name, mod_id=mod_id)

        return True

    def download_mod(self, instance_name: str, mod_id=None, mod_name=None):
        if mod_id is not None:
            mod_filter = {'_id': mod_id}
        elif mod_name is not None:
            mod_filter = {'name': mod_name}
        else:
            return False

        db = self.client[self.database]

        mod = db[self.mods_collection].find_one(mod_filter)
        if mod is None or len(mod['versions']) <= 0:
            return False

        mod['versions'].sort(key=lambda ver: ver['upload_date'], reverse=True)
        mod_file_id = mod['versions'][0]['mod_id']

        file_name = db['fs.files'].find_one({'_id': mod_file_id})['filename']
        mod_install_path: Path = Path(self.instance_directory) / instance_name / 'mods'

        with open(mod_install_path / file_name, 'wb+') as mod_file_stream:
            fs = GridFSBucket(db)
            fs.download_to_stream(mod_file_id, mod_file_stream)

    def upload_mod(self, mod_name: str, version: str, mod_file: str):
        db = self.client[self.database]
        mod_path: Path = Path(mod_file)

        with mod_path.open('rb') as mod:
            fs = GridFSBucket(db)
            upload_id = fs.upload_from_stream(mod_path.name, mod)
            filter = {'name': mod_name}
            mods = [{'mod_id': upload_id, 'ver': version, 'upload_date': datetime.now().timestamp()}]
            result = db[self.mods_collection].find_one(filter)
            if result is not None:
                mods.extend(result['versions'])

            rec = {**filter, 'last_modified': datetime.now().timestamp(), 'versions': mods}
            return db[self.mods_collection].update_one(filter, {'$set': rec}, upsert=True)
