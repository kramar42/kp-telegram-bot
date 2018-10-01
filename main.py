#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from module import load_modules, get_module


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(module)s][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    load_modules()
    get_module('core').updater.idle()


if __name__ == '__main__':
    main()
