
.. _config-celery:

Install Celery
--------------

To improve |RCM| performance you should install Celery_ as it makes
asynchronous tasks work efficiently. If you
install Celery you also need multi-broker support. The recommended message
broker is rabbitmq_. |RCM| works in sync
mode, but running Celery_ will give you a large speed improvement when
managing many big repositories.

If you want to run |RCM| with Celery you need to run ``celeryd`` using the
``paster`` command and the message broker.
The ``paster`` command is already installed during |RCM| installation.

To install and configure Celery, use the following steps:

1. Install Celery and RabbitMQ, see the documentation on the Celery website for
   `Celery installation`_ and `rabbitmq installation`_.
2. Enable Celery in the
   :file:`home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file.
3. Run the Celery daemon with the ``paster`` command,
   using the following example
   ``.rccontrol/enterprise-1/profile/bin/paster celeryd .rccontrol/enterprise-1/rhodecode.ini``

.. code-block:: ini

    # Set this section of the ini file to match your Celery installation
    ####################################
    ###        CELERY CONFIG        ####
    ####################################
    ## Set to true
    use_celery = false
    broker.host = localhost
    broker.vhost = rabbitmqhost
    broker.port = 5672
    broker.user = rabbitmq
    broker.password = qweqwe

    celery.imports = rhodecode.lib.celerylib.tasks

    celery.result.backend = amqp
    celery.result.dburi = amqp://
    celery.result.serialier = json

    #celery.send.task.error.emails = true
    #celery.amqp.task.result.expires = 18000

    celeryd.concurrency = 2
    #celeryd.log.file = celeryd.log
    celeryd.log.level = debug
    celeryd.max.tasks.per.child = 1

    ## tasks will never be sent to the queue, but executed locally instead.
    celery.always.eager = false

.. code-block:: bash

    # Once the above is configured and saved
    # Run celery with the paster command and specify the ini file
    .rccontrol/enterprise-1/profile/bin/paster celeryd .rccontrol/enterprise-1/rhodecode.ini

.. _python: http://www.python.org/
.. _mercurial: http://mercurial.selenic.com/
.. _celery: http://celeryproject.org/
.. _rabbitmq: http://www.rabbitmq.com/
.. _rabbitmq installation: http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html
.. _Celery installation: http://docs.celeryproject.org/en/latest/getting-started/introduction.html#bundles
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
