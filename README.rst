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

* We recommend creating a virtual environment using conda

.. code-block:: bash

   conda create -n myenv python=3.6

Alternatively, with a path name

.. code-block:: bash

   conda create -p /path/to/myenv python=3.6

* Activate virtual environment

.. code-block:: bash

   conda activate /path/to/myenv


* Install dependencies

Navigate to the root directory of adviser, where you see `requirements_soloist_recipe.txt`

.. code-block:: bash

   pip install -r requirements_soloist_recipe.txt

* Download pretrained model
   
   * gtg_pretrained 
   https://drive.google.com/file/d/1BNhY_GCx5f_Ubv_8mx6PHa6mFDAG7ujh/view?usp=drive_link
   
   * finetuned_models
   https://drive.google.com/drive/folders/1VjnxouEe04yrokzllFpevXi7Jw-h_JDK?usp=sharing

* Copy ``gtg_pretrained`` and ``finetuned_models`` to the same directory where you see soloist_train.py, that is:

.. code-block:: bash

   soloist/soloist/gtg_pretrained
   soloist/soloist/finetuned_models

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

**Training**

Please refer to documentation in `submodule <https://github.com/Yen444/soloist>`_ SOLOIST. 

**Interaction** 

* Under adviser/adviser directory

.. code-block:: bash
   
   python run_chat_recipe.py
  

Belows is the chat history using the baseline model. Note that there're some errors in belief states prediction, fortunately the model still outputs reasonable responses. For a detailed error analysis, please refer to our  `report <https://docs.google.com/document/d/1F-HPy6cI-tPWWeAzBCw6Mpq-yxSDs__dQhwoWS1HvEc/edit?usp=sharing/>`_.

.. code-block:: bash
>>> hi i want to make a main dish with beef
***Belief States tracker: {'type': 'main dish', 'ingredients': 'beef'}***
***Delexicalized response: Sure ! I have a delicious recipe for [recipe_name_1] . What do you think ?***
System: Sure ! I have a delicious recipe for Beef Tacos with Chipotle Sauce . What do you think ?
>>> what do i need for that recipe?
***Belief States tracker: {'equipment': 'beef', 'type': 'main dish', 'ingredients': 'not mentioned', 'name': '[recommended_recipe_name_1]'}***
***Delexicalized response: You will need [recipe_ingredients] for the recipe .***
System: You will need '1 lb ground beef', '1 onion, chopped', '2 cloves garlic, minced', '1 tbsp chipotle pepper in adobo sauce, minced', '1 tsp ground cumin', '1 tsp chili powder', 'Salt and pepper to taste', '8 small flour tortillas', 'Toppings: shredded lettuce, diced tomatoes, shredded cheese, sour cream', 'Optional garnish: fresh cilantro, lime wedges' for the recipe .
>>> and how long does it take?
***Belief States tracker: {'type': 'main dish', 'ingredients': 'beef', 'name': '[recommended_recipe_name_1]'}***
***Delexicalized response: it takes [recipe_time] .***
System: it takes 30 minutes .
>>> sounds good, give me the instruction
***Belief States tracker: {'ingredients': 'negative mustard', 'type': 'main dish', 'name': '[recommended_recipe_name_2]'}***
***Delexicalized response: Here are the instructions : [recipe_instructions] , [recipe_instructions]***
System: Here are the instructions : 'In a large skillet, cook the ground beef over medium heat until browned.', 'Add the chopped onion, minced garlic, chipotle pepper, cumin, chili powder, salt, and pepper. Cook for an additional 5 minutes.', 'Warm the flour tortillas in a separate skillet or in the microwave.', 'Assemble the tacos by placing a spoonful of the beef mixture onto each tortilla. Add your desired toppings.', 'Garnish with fresh cilantro and serve with lime wedges on the side.', 'Enjoy your delicious beef tacos with chipotle sauce!' , 'In a large skillet, cook the ground beef over medium heat until browned.', 'Add the chopped onion, minced garlic, chipotle pepper, cumin, chili powder, salt, and pepper. Cook for an additional 5 minutes.', 'Warm the flour tortillas in a separate skillet or in the microwave.', 'Assemble the tacos by placing a spoonful of the beef mixture onto each tortilla. Add your desired toppings.', 'Garnish with fresh cilantro and serve with lime wedges on the side.', 'Enjoy your delicious beef tacos with chipotle sauce!'
