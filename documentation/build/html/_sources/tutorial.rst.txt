Tutorial
=========

In ``product-analytics-group-project-deepvision/code/user_definition.py``:

    1. Replace the current ``ec2_address`` with your instance's ec2 public DNS address.

    2. Replace the current ``key_file`` path with the path  to your own pem file to access your instance.

    3. We assume that the conda environment points to a ``.conda`` file that is in the home directory of the user environment
Afterward, in the command line, go to ``product-analytics-group-project-deepvision/code/`` and run ``$ python deploy_script.py``.

Input your GitHub username, which should be the same one stored on the remote machine. The webpage should be running on the specified ec2 address and the port specified by ``FLASK_RUN_PORT`` in ``.flaskenv``.
