from pypeflow.pwatcher_bridge import PypeProcWatcherWorkflow, MyFakePypeThreadTaskBase
from pypeflow.data import PypeLocalFile, makePypeLocalFile, fn
from pypeflow.task import PypeTask
from pypeflow.simple_pwatcher_bridge import (PypeTask,
        PypeLocalFile, makePypeLocalFile, fn,
        PypeProcWatcherWorkflow, MyFakePypeThreadTaskBase)
from pypeflow.simple_pwatcher_bridge import fn

def say_hey0(self):
    o0 = fn(self.o0)
    print 'hey', o0
    script = """\
#!/bin/bash

echo hey0
touch %(o0)s
""" % locals()
    script_fn = 'run-hey.sh'
    with open(script_fn, 'w') as ofs:
        ofs.write(script)
    self.generated_script_fn = script_fn

def say_hey1(self):
    o1 = fn(self.o1)
    i0 = fn(self.i0)
    script = """\
#!/bin/bash

echo hey1
touch %(o1)s
""" % locals()
    script_fn = 'run-hey.sh'
    with open(script_fn, 'w') as ofs:
        ofs.write(script)
    self.generated_script_fn = script_fn
