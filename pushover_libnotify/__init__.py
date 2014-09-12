#!/usr/bin/env python
#

import logging
import pushover_libnotify

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    pushover_libnotify.pushover_libnotify()

if __name__ == "__main__":
    main()
