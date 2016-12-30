import unittest
# TEST RESOURCES
import os
import sys
import platform
import subprocess
import time

import core as c


print(time.ctime())
print('os.name: %s' % os.name)
print('platform.system: %s' % platform.system())
print('platform.release: %s' % platform.release())
print('PingStats version: %s' % c.version)
print('Python version (via sys.version): %s' % sys.version)
pipe = subprocess.PIPE
p = subprocess.Popen(['git', 'log', '--oneline', '-n 1'], stdout=pipe,
                     stderr=pipe)
stdout, stderr = p.communicate()
p.kill()
print('stdout: \n%s\nstderr:\n%s\n\n' % (stdout, stderr))

print('\n\nIf `test_instantiate_with_good_ip (test_animateplot.'
      'AnimatePlot_test)` fails, please run the tests again.\n\n')
time.sleep(0.3)

loader = unittest.TestLoader()
tests = loader.discover('tests/')
runner = unittest.TextTestRunner(buffer=True, verbosity=2)
runner.run(tests)
