import json
import os 
import sys
from pysondb import db
import numpy as np
import sqlite3
import random

def lower_case(json_list):
   new_list = []
   for dict_item in json_list:
      new_dict = dict((str(k).lower(), str(v).lower()) for k,v in dict_item.items())
      new_list.append(new_dict)
   return new_list

def create_database():

   with open("recipe_db.json", "r") as json_file:
      data_json = json.load(json_file)

   os.remove('recipes.db')
   conn = sqlite3.connect('recipes.db')
   cursor = conn.cursor()
   cursor.execute('''CREATE TABLE Recipes 
               (id INT PRIMARY KEY NOT NULL, 
               name TEXT,
               type TEXT,
               ingredients TEXT,
               instructions TEXT,
               substitution TEXT,
               equipment TEXT,
               time TEXT, 
               is_quick TEXT,
               difficulty TEXT,
               is_vegan TEXT);''')

   conn.commit()



   for data_idx in range(len(data_json)):
      entry = data_json[data_idx]

      #time_entry = entry['time'].split(" ")
      #time_entry = time_entry[0].split("-")
      #time_entry = int(np.round(float(time_entry[0]))) # just ignore stuff like 1.5 to 2.0 hours
      cursor.execute(f'''INSERT INTO Recipes (id, name, type, ingredients, instructions, 
               substitution, equipment, time, is_quick, difficulty, is_vegan) \n
               VALUES ({data_idx}, \"{entry['name']}\", \"{entry['type']}\", \"{entry['ingredients']}\",
               \"{entry['instructions']}\", \"{entry['substitution']}\", \"{entry['equipment']}\",
               \"{entry['time']}\",\"{entry['is_quick']}\", \"{entry['difficulty']}\", \"{entry['is_vegan']}\");''')

   conn.commit()
   conn.close()

def query_database(belief : dict, response: str, db_state=None):
   """
   argurment: 
      belief_state:
      response:
   return:
      lexicalized response to be shown in the bot
      db_state to keep track of recommended recipes
   """

   # initialize db_state
   if db_state is None:
      db_state = {}
   
   # query database from belief states
   query = "SELECT * FROM Recipes WHERE"
   for slot, val in belief.items():
      #get rig of some strange tokens
      val = val.replace('<EOB> <EOKB> <EODP>', '')
      val = val.strip()
      if 'recommended_recipe_name_1' in val:
         if 'recommended_recipe_name_1' in db_state.keys():
            name = db_state['recommended_recipe_name_1']
            name = "'" f'%{name}%' + "'"
            query = f'SELECT * FROM Recipes WHERE name LIKE {name}'
            break
         else:
            continue
      elif 'recommended_recipe_name_2' in val:
         if 'recommended_recipe_name_2' in db_state.keys():
            name = db_state['recommended_recipe_name_2']
            name = "'" f'%{name}%' + "'"
            query = f'SELECT * FROM Recipes WHERE name LIKE {name}'
            break
         elif 'recommended_recipe_name_1' in db_state.keys():
            name = db_state['recommended_recipe_name_1']
            name = "'" f'%{name}%' + "'"
            query = f'SELECT * FROM Recipes WHERE name LIKE {name}'
            break
         else:
            continue
      else: 
         if val == 'dont care' or val == 'not mentioned' or val == "don't care":
            query = query
         elif 'negative' in val:
            val_neg = val.split(' ')
            val_neg = "'" + f'%{val_neg[-1]}%' + "'"
            if query.endswith('WHERE'):
               query += f' {slot} NOT LIKE {val_neg}'
            else:
               query += f' AND {slot} NOT LIKE {val_neg}'
         else:
            val_pos = "'" f'%{val}%' + "'"
            if query.endswith('WHERE'):
               query += f' {slot} LIKE {val_pos}'
            else:
               query += f' AND {slot} LIKE {val_pos}'
   
   # get matches from db
   if query.endswith('WHERE'):
      query = query.replace('WHERE', '')
   #print(query)
   conn = sqlite3.connect('recipes.db')
   cursor = conn.cursor()
   cursor.execute(query)  
   matches = cursor.fetchall() 
   random.shuffle(matches)

   # lexicalize response
   if len(matches) == 0:
      response = 'Sorry. I do not have any recipe that meet your requests at the moment. What else can I help you?'
   else:
      if 'recipe_name_1' in response:
         name = matches[0][1]
         response = response.replace('recipe_name_1', name)
         db_state['recommended_recipe_name_1'] = name 
      if 'recipe_name_2' in response:
         if len(matches) > 1:
            name = matches[1][1]
            response = response.replace('recipe_name_2', name)
            db_state['recommended_recipe_name_2'] = name
         else:
            if 'recommended_recipe_name_1' not in db_state.keys():
               name = matches[0][1]
               response = response.replace('recipe_name_2', name)
               db_state['recommended_recipe_name_1'] = name 
            else:
               response = 'Sorry. That is the only recipe I have that meet your request. What else can I help you?'
      if 'recipe_type' in response:
         type = matches[0][2]
         response = response.replace('recipe_type', type)
      if 'recipe_ingredients' in response:
         ingredients = matches[0][3]
         response = response.replace('recipe_ingredients', ingredients)
      if 'recipe_instructions' or 'values_instructions' in response:
         instructions = matches[0][4]
         response = response.replace('recipe_instructions', instructions)
         response = response.replace('values_instructions', instructions)
      if 'recipe_substituion' in response:
         substitution = matches[0][5]
         response = response.replace('recipe_substituion', substitution)
      if 'recipe_equipment' in response:
         equipment = matches[0][6]
         response = response.replace('recipe_equipment', equipment)
      if 'recipe_time' in response:
         time = matches[0][7]
         response = response.replace('recipe_time', time)
      if 'recipe_is_quick' in response:
         is_quick = matches[0][8]
         response = response.replace('recipe_is_quick', is_quick)
      if 'recipe_difficulty'  in response:
         difficulty = matches[0][9]
         response = response.replace('recipe_difficulty', difficulty)
      if 'recipe_is_vegan' in response:
         is_vegan = matches[0][10]
         response = response.replace('recipe_is_vegan', is_vegan)
      #confirm ingredient
      if 'recipe_ingredient_value' in response:
         for slot, val in belief.items():
            if 'ingredient' in slot:
               ingredient_value = val
               ingredient_value = ingredient_value.replace('negative', '')
         ingredient_value = f'out {ingredient_value}' if 'negative' in val else f'{ingredient_value}' # when confirm the ingredients that user wants or doesn't want
         response = response.replace('recipe_ingredient_value', ingredient_value)

      # get rid of remaining brackets
      response = response.replace('[', '')
      response = response.replace(']', '')
      
   return response, db_state

if __name__ == "__main__":
   pass
   #create_database()
   #response, db = query_database({'type': 'main dish', 'ingredients': 'negative chicken'}, "so you are looking for a recipe with [recipe_ingredient_value]? I would recommend [recipe_name_1]")
   #print(response)