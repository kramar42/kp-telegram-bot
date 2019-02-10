#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import hashlib
import importlib
import logging
import os
import traceback


MODULES_PATH = 'modules/*.py'
modules = {}


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


def load_modules():
    files = set(glob.glob(MODULES_PATH))
    global modules
    loaded_files = set(m.path for m in modules.values())
    new_files = files - loaded_files

    new_modules = []
    existing_modules = [modules[get_name(p)] for p in files & loaded_files]
    old_modules = [modules[get_name(p)] for p in loaded_files - files]

    log = logging.getLogger()

    # load new modules
    for file in new_files:
        try:
            module = Module(file)
            modules[module.name] = module
            new_modules.append(module)
            log.info("imported '%s' module", module.name)
        except Exception as e:
            log.error("importing of '%s' module failed: %s", get_name(file), e)
            log.debug('%s', traceback.format_exc())

    # get handler dispatcher from core module
    dispatcher = modules['core'].module.dispatcher
    def add_handlers(handlers):
        for handler in handlers:
            dispatcher.add_handler(handler)
    def remove_handlers(handlers):
        for handler in handlers:
            dispatcher.remove_handler(handler)

    # reload existing modules
    for module in (m for m in existing_modules if sha256sum(m.path) != m.hashsum):
        remove_handlers(module.handlers)
        module.reload()
        new_modules.insert(0, module)
        log.info("reloaded '%s' module", module.name)

    # start modules
    for module in new_modules:
        module.start()
        add_handlers(module.handlers)
        log.info("started '%s' module", module.name)

    # remove old modules
    for module in old_modules:
        remove_handlers(module.handlers)
        del modules[module.name]
        log.info("removed '%s' module", module.name)


def get_module(name):
    global modules
    return modules[name].module if name in modules else None


def sha256sum(path):
    with open(path, encoding='utf8') as f:
        return hashlib.sha256(f.read().encode('utf8')).hexdigest()


def get_name(path):
    return os.path.splitext(os.path.basename(path))[0]
