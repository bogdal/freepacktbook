freepacktbook
=============

.. image:: https://img.shields.io/circleci/project/bogdal/freepacktbook/master.svg
    :target: https://circleci.com/gh/bogdal/freepacktbook/tree/master
    
.. image:: https://img.shields.io/pypi/v/freepacktbook.svg   
     :target: https://pypi.python.org/pypi/freepacktbook
  

Claim Your `Free PacktPub eBook <https://www.packtpub.com/packt/offers/free-learning>`_ automatically.

.. code-block:: bash

  $ pip install freepacktbook

  $ export PACKTPUB_EMAIL=my@email.com
  $ export PACKTPUB_PASSWORD=my_password
  $ export PACKTPUB_BOOKS_DIR=/books (optional)
  
  $ claim_free_ebook


Notifications (optional)
------------------------

``Slack`` **integration**

Set additionally the following environment variables:

.. code-block:: bash

  export SLACK_URL=https://hooks.slack.com/services/...
  export SLACK_CHANNEL=#random

.. image:: https://github-bogdal.s3.amazonaws.com/freepacktbook/slack.png
