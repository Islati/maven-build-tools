from unittest import TestCase
import os
import glob


#Todo implement input streams from: click.pocoo.org/5/testing/ for proper testing.

class CraftTest(TestCase):
    def tearDown(self):
        # Clear out the local folder of all jar files.

        for jar_file in glob.glob("*.jar"):
            os.remove(jar_file)


