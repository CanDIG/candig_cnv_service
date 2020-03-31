.. _development:

-----------------
Development Setup
-----------------

******************************
Standalone CNV Service  Setup
******************************

You will need Python 3.6.x to successfully run the service.

First, create and activate a  virtualenv with Python 3.6.x:

.. code-block:: bash
   
    python -m venv venv_name
   source venv_name/bin/activate

Once your virtual environment is created, run:

.. code-block:: bash
   
   pip clone git@github.com:CanDIG/candig_cnv_service.git
   pip install -r requirements_dev.txt


Then you can go to the cloned directory and run:

.. code-block:: bash
   
    python -m candig_cnv_service

By default it will run on address 0.0.0.0 and port 8870. You can change by running the previous command adding  the desired address and port:

.. code-block:: bash
   
    python -m candig_cnv_service --host 127.0.0.1--port 8080
