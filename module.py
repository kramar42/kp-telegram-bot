#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import hashlib
import importlib
import logging
import os
import traceback


class Module:
    def __init__(self, path):
        self.name = get_name(path)
        self.path = path
        self.hashsum = sha256sum(self.path)

        importing_name = self.path.replace(os.sep, '.').replace('.py', '')
        self.module = importlib.import_module(importing_name)
        self.handlers = []

    def reload(self):
        self.hashsum = sha256sum(self.path)
        self.module = importlib.reload(self.module)

    def start(self):
        self.handlers = self.module.start() or []


class ModulesManager:
    def __init__(self, path):
        self.path = path
        self.log = logging.getLogger()
        self.modules = {}
        self.new_modules = []


    def import_new_modules(self):
        files = set(glob.glob(self.path))
        loaded_files = set(m.path for m in self.modules.values())
        new_files = files - loaded_files

        # load new modules
        for file in new_files:
            try:
                module = Module(file)
                self.modules[module.name] = module
                self.new_modules.append(module)
                self.log.info("imported '%s' module", module.name)
            except Exception as e:
                self.log.error("importing of '%s' module failed: %s", get_name(file), e)
                self.log.debug('%s', traceback.format_exc())


    def start_modules(self, dispatcher):
        self.dispatcher = dispatcher

        for module in self.new_modules:
            module.start()
            for handler in module.handlers:
                self.dispatcher.add_handler(handler)
            self.log.info("started '%s' module", module.name)

        self.new_modules.clear()


    def reload_modules(self):
        # helper function
        def remove_handlers(handlers):
            for handler in handlers:
                self.dispatcher.remove_handler(handler)

        files = set(glob.glob(self.path))
        loaded_files = set(m.path for m in self.modules.values())
        old_modules = [self.modules[get_name(p)] for p in loaded_files - files]
        # remove old modules
        for module in old_modules:
            remove_handlers(module.handlers)
            del self.modules[module.name]
            self.log.info("removed '%s' module", module.name)

        # reload existing modules
        for module in (m for m in self.modules.values() if sha256sum(m.path) != m.hashsum):
            remove_handlers(module.handlers)
            try:
                module.reload()
                self.new_modules.append(module)
                self.log.info("reloaded '%s' module", module.name)
            except Exception as e:
                self.log.error("reloading of '%s' module failed: %s", get_name(file), e)
                self.log.debug('%s', traceback.format_exc())

        self.import_new_modules()
        self.start_modules(self.dispatcher)


    def get_module(self):
        return self.modules[name].module if name in self.modules else None


def get_module(name):
    global manager
    return manager.get_module(name)


def sha256sum(path):
    with open(path, encoding='utf8') as f:
        return hashlib.sha256(f.read().encode('utf8')).hexdigest()


def get_name(path):
    return os.path.splitext(os.path.basename(path))[0]


MODULES_PATH = 'modules/*.py'
manager = ModulesManager(MODULES_PATH)
