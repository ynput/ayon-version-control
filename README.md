Version control addon
---------------------

This addon tries to implement generic API for various version control system.

Currently contains WIP implementation of Perforce, but there might be more in the future.

Implementation tries to use only single dependency `p4python` which is binary dependent on version of python used. (Which might be different in different DCCs, different versions of Unreal etc.)
Currently implements REST api to run p4 commands only on separate webserver which contains `p4python` and REST stub class which might be used in each DCC that has `requests` library.

This addon is WIP, for testing please `pip install p4python` to your `ayon-launcher .venv`.
