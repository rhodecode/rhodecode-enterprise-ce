"""gunicorn config hooks"""

import multiprocessing
import sys
import threading
import traceback


# GLOBAL #
errorlog = '-'
accesslog = '-'
loglevel = 'debug'

# SECURITY #
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SERVER MECHANICS #
# None == system temp dir #
worker_tmp_dir = None
tmp_upload_dir = None
#proc_name =

# self adjust workers based on CPU #
#workers = multiprocessing.cpu_count() * 2 + 1

access_log_format = '[%(p)s] %(h)15s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" request_time:%(L)s'

# For the gevent worker classes #
# this limits the maximum number of simultaneous clients that #
# a single process can handle. #
#worker_connections = 10

# Max requests to handle by each worker before restarting it, #
# could prevent memory leaks #
#max_requests = 1000
#max_requests_jitter = 30


# If a worker does not notify the master process in this #
# number of seconds it is killed and a new worker is spawned #
# to replace it. #
#timeout = 3600

access_log_format = (
    '[%(p)-10s] %(h)s time:%(L)s %(l)s %(u)s '
    '%(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"')


def post_fork(server, worker):
    server.log.info("[<%s>] worker spawned", worker.pid)


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    worker.log.info("[<%-10s>] worker received INT or QUIT signal", worker.pid)

    # get traceback info
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for thread_id, stack in sys._current_frames().items():
        code.append(
            "\n# Thread: %s(%d)" % (id2name.get(thread_id, ""), thread_id))
        for fname, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (fname, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    worker.log.debug("\n".join(code))


def worker_abort(worker):
    worker.log.info("[<%-10s>] worker received SIGABRT signal", worker.pid)


def pre_request(worker, req):
    return
    worker.log.debug("[<%-10s>] PRE WORKER: %s %s",
                     worker.pid, req.method, req.path)


def post_request(worker, req, environ, resp):
    return
    worker.log.debug("[<%-10s>] POST WORKER: %s %s resp: %s", worker.pid,
                     req.method, req.path, resp.status_code)