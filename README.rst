freepacktbook
=============

.. image:: https://img.shields.io/circleci/project/bogdal/freepacktbook/master.svg
    :target: https://circleci.com/gh/bogdal/freepacktbook/tree/master
    
.. image:: https://img.shields.io/pypi/v/freepacktbook.svg   
     :target: https://pypi.python.org/pypi/freepacktbook
  

Claim Your `Free PacktPub eBook <https://www.packtpub.com/packt/offers/free-learning>`_ automatically.

**Quickstart:**

.. code-block:: bash

  $ pip install freepacktbook

  $ export PACKTPUB_EMAIL=my@email.com
  $ export PACKTPUB_PASSWORD=my_password
  
  $ claim_free_ebook
  
Claim your daily free PacktPub ebook and download it:

.. code-block:: bash

    $ export PACKTPUB_BOOKS_DIR=/path/to/my/books
    
    $ claim_free_ebook --download
    
**Download all your ebooks:**

``freepacktbook`` allows you to backup all your ebooks and code files.

.. code-block:: bash

    $ download_ebooks --formats mobi pdf --with-code-files


To see more information:

.. code-block:: bash

    $ download_ebooks -h

**Cron configuration:**

Edit the current crontab:

.. code-block:: bash

    $ crontab -e
    
Add the following lines:

.. code-block:: bash

    #!/bin/bash
    SHELL=/bin/bash
    PACKTPUB_EMAIL='my@email.com'
    PACKTPUB_PASSWORD='my_password'
    
    0 8 * * * /path/to/claim_free_ebook >> /tmp/claim_free_ebook.log 2>&1
    
This command shows the direct path to ``claim_free_ebook``:

.. code-block:: bash
    
    which claim_free_ebook
    

Notifications (optional)
------------------------

``Slack`` **integration**

Set additionally the following environment variables:

.. code-block:: bash

  export SLACK_URL=https://hooks.slack.com/services/...
  export SLACK_CHANNEL=random
  
  $ claim_free_ebook --slack

.. image:: https://github-bogdal.s3.amazonaws.com/freepacktbook/slack.png

Docker image
------------

You can build your own docker image containing configured cron service. By default, the ``claim_free_ebook`` command is run daily at 8:00am CEST. See `Dockerfile <https://github.com/bogdal/freepacktbook/blob/master/Dockerfile>`_.

Build an image:

.. code-block:: bash

    $ docker build -t freepacktbook .
    
Run a new container:

.. code-block:: bash

    $ docker run \
     --env PACKTPUB_EMAIL=${PACKTPUB_EMAIL} \
     --env PACKTPUB_PASSWORD=${PACKTPUB_PASSWORD} \
     --detach \
     --name freepacktbook \
     freepacktbook

