#!/usr/bin/env python2.7
from pypeflow.pwatcher_bridge import PypeProcWatcherWorkflow, MyFakePypeThreadTaskBase
from pypeflow.data import PypeLocalFile, makePypeLocalFile, fn
from pypeflow.task import PypeTask
from pypeflow.simple_pwatcher_bridge import (PypeTask,
        PypeLocalFile, makePypeLocalFile, fn,
        PypeProcWatcherWorkflow, MyFakePypeThreadTaskBase)
import mymod

import argparse
import ConfigParser as configparser
import json
import logging
import logging.config
import os
import pprint
import sys
import time
LOG = logging.getLogger()

default_logging_config = """
[loggers]
keys=root

[handlers]
keys=stream,file_all

[formatters]
keys=form01,form02

[logger_root]
level=NOTSET
handlers=stream,file_all

[handler_stream]
class=StreamHandler
level=DEBUG
formatter=form02
args=(sys.stderr,)

[handler_file_all]
class=FileHandler
level=DEBUG
formatter=form01
args=('all.log', 'w')

[formatter_form01]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_form02]
format=[%(levelname)s]%(message)s
"""

def _setup_logging(logging_config_fn):
    """See https://docs.python.org/2/library/logging.config.html
    """
    import StringIO
    logging.Formatter.converter = time.gmtime # cannot be done in .ini

    if logging_config_fn:
        if logging_config_fn.endswith('.json'):
            logging.config.dictConfig(json.loads(open(logging_config_fn).read()))
            #print repr(logging.Logger.manager.loggerDict) # to debug
            return
        logger_fileobj = open(logging_config_fn)
    else:
        logger_fileobj = StringIO.StringIO(default_logging_config)
    defaults = {
    }
    logging.config.fileConfig(logger_fileobj, defaults=defaults, disable_existing_loggers=False)

def setup_logger(logging_config_fn):
    try:
        _setup_logging(logging_config_fn)
        LOG.info('Setup logging from file "{}".'.format(logging_config_fn))
    except Exception:
        logging.basicConfig()
        LOG.exception('Failed to setup logging from file "{}". Using basicConfig().'.format(logging_config_fn))
    try:
        import logging_tree
        LOG.info(logging_tree.format.build_description())
    except ImportError:
        pass

def config2dict(cfg):
    d = dict()
    for section in cfg.sections():
        d[section] = dict(cfg.items(section))
    return d

def dict2config(jdict, section):
    config = configparser.ConfigParser()
    if not config.has_section(section):
        config.add_section(section)
    for k,v in jdict.iteritems():
        config.set(section, k, str(v))
    return config

def parse_config(config_fn):
    ext = os.path.splitext(config_fn)[1]
    if ext in ('.json', '.js'):
        jdict = json.loads(open(config_fn).read())
        config = dict2config(jdict, "General")
    else:
        config = configparser.ConfigParser()
        config.readfp(open(config_fn))
    return config2dict(config)

def run(wf, config,
        setNumThreadAllowed,
        ):
    exitOnFailure = True
    concurrent_jobs = 2
    setNumThreadAllowed(concurrent_jobs, concurrent_jobs)
    #try:
    #    # Make it always re-run.
    #    os.remove('out.txt')
    #except Exception:
    #    LOG.exception('could not remove out.txt')
    o0 = makePypeLocalFile('hey0/out.txt')
    make_task = PypeTask(
            inputs = {},
            outputs = {'o0': o0},
            parameters = {},
            TaskType = MyFakePypeThreadTaskBase,
    )
    t0 = make_task(mymod.say_hey0)
    o1 = makePypeLocalFile('hey1/out.txt')
    make_task = PypeTask(
            inputs = {'i0': o0},
            outputs = {'o1': o1},
            parameters = {},
            TaskType = MyFakePypeThreadTaskBase,
    )
    t1 = make_task(mymod.say_hey1)
    wf.addTasks([t0, t1]) # for new-simple-way, we could add just t1
    wf.refreshTargets(exitOnFailure=exitOnFailure)

def main1(prog_name, input_config_fn, logger_config_fn=None):
    global CFG
    setup_logger(logger_config_fn)
    LOG.info('config={!r}, log={!r}'.format(input_config_fn, logger_config_fn))
    CFG = parse_config(input_config_fn)['General']
    LOG.info('CFG=\n{}'.format(pprint.pformat(CFG)))

    wf = PypeProcWatcherWorkflow(
            job_type=CFG['job_type'],
            job_queue=CFG['job_queue'],
            watcher_type=CFG['watcher_type'],
            max_jobs=CFG.get('max_jobs', 24),
    )
    run(wf, CFG,
        setNumThreadAllowed=PypeProcWatcherWorkflow.setNumThreadAllowed)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config',
        help='.cfg/.ini/.json')
    parser.add_argument('logger',
        nargs='?',
        help='(Optional)JSON config for standard Python logging module')
    args = parser.parse_args(argv[1:])
    main1(argv[0], args.config, args.logger)

if __name__=="__main__":
    main()
