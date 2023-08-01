|release| |nbsp| |license|

.. |release| image:: https://img.shields.io/github/v/release/digitalphonetics/adviser?sort=semver
   :target: https://github.com/DigitalPhonetics/adviser/releases
.. |license| image:: https://img.shields.io/github/license/digitalphonetics/adviser
   :target: #license
.. |nbsp| unicode:: 0xA0
   :trim:

Documentation
=============
* For Adviser 2.0, please refer to the `README <https://github.com/DigitalPhonetics/adviser>`_
* Here we only explain briefly how to integrate an end-to-end dialogue system, namely SOLOIST to Adviser
* Please see the `report <https://docs.google.com/document/d/1F-HPy6cI-tPWWeAzBCw6Mpq-yxSDs__dQhwoWS1HvEc/edit?usp=sharing/>`_ for more details.

Installation
============

* Clone the repository by entering in a terminal window:

.. code-block:: bash

    git clone https://github.com/nguyenhongquy/adviser.git

* change to the directory of soloist (adviser/soloist)
.. code-block:: bash

   git submodule init
   git submodule update

Training Data Preparation
=========================
**Data format**

.. code-block:: json

    {
        "history": [
            "user : I'm in the mood for a dessert. Can you suggest something sweet? "
        ],
        "kb": "kb : more than three",
        "belief": "belief : type = dessert ; ingredients = not mentioned ",
        "reply": "system : Sure! I have a few recipes for dessert. Do you have any preferences or restrictions?",
        "dp": "dp : request ( ingredients ) "
    }

We use json to represent a training example. As shown in the example, it contains the following fields:

* **history** - The context from session beginning to current turn.

* **belief** - The belief state of the user (slot - value pair). 

* **kb** - Database query results. If not blank, inference is slower but better.

* **reply** - The target system respose. It can be a template, an api call or natural language.

* **dp** - The system action or dialogue policy.

We create a mini corpus with 40 training dialogues, 10 for validation and 20 for testing purpose. Each split is in the same format of SOLOIST training data.

**Training***

Please refer to documentation in `submodule <https://github.com/Yen444/soloist>`_ SOLOIST. 

**Interaction** 

.. code-block:: bash

   # under adviser/adviser directory
   python run_chat_recipe.py
