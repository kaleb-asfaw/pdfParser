import unittest, time, sys, os
# Send the root of the directory being reference DOWN 2 LEVELS
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import func.parse as parse


class TestAPI(unittest.TestCase):
    def openai_response(self):
        pass


if __name__ == '__main__':
    unittest.main()