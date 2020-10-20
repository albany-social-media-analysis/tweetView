"""
JSON Schema requires Mongo 3.6+
"""

import pymongo
import mongo_config

'''
client = pymongo.MongoClient(username=mongo_config.user, password=mongo_config.pwd, port=mongo_config.port)

db = client['test_db2']

collection1_name = 'schema_test_1'

db.create_collection(collection1_name)
'''
"""
# TO SET VALIDATION
db.command( {
   "collMod": "schema_test_1",
   "validator": { "$jsonSchema": {
      "bsonType": "object",
      "required": [ "number of individuals", "risky behavior present" ],
      "properties": {
         "number of individuals": {
            "bsonType": "int",
            "minimum": 0,
            "maximum": 10,
            "description": "must be an integer in the specified range and is required"
         },
         "risky behavior present": {
            "bsonType": "bool",
            "description": "must be true or false and is required"
         },
         "risk in text or image": {
             "enum": ["Text", "Image", None],
             "description": "must specify one of the options if the feature is present"
         }
      }
   } },
   "validationLevel": "strict",
   "validationAction": "error"
} )

# TO REMOVE VALIDATION
db.command({"collMod": "schema_test_1", "validator": {}, "validationLevel": "off"})
"""

class DataValidationTypeError(Exception):
   def __init__(self, *args):
      if args:
         self.message = args[0]
      else:
         self.message = None

   def __str__(self):
      if self.message:
         return self.message
      else:
         return "Unspecified DataValidationTypeError"


class DataValidationValueError(Exception):
   def __init__(self, *args):
      if args:
         self.message = args[0]
      else:
         self.message = None

   def __str__(self):
      if self.message:
         return self.message
      else:
         return "Unspecified DataValidationValueError"


class DataValidation:

   """
   Each object created from this class is a single field (i.e., a label) along with the possible options for the
    value for that field.

   This needs to be redesigned to match the structure of validator objects for the different types expected by Mongo.
     See https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/
   """

   def __init__(self, field_name, field_type):
      self.name = field_name
      field_type_options = ['int', 'enum', 'bool', 'str']
      if field_type in field_type_options:
         self.bsonType = field_type
      elif not field_type in field_type_options:
         raise TypeError('Invalid field data type provided. Field data type options are int, enum, bool, and str.')
      data_type = self.bsonType
      if data_type == 'int':
         self.minimum = None
         self.maximum = None
         options_description = "Users will be able to choose any integer between the minimum and maximum value."
      elif data_type == 'enum':
         self.options = []
         options_description = "Users will choose one of the provided options for this field. The options do not need" \
                               " to be the same data type, but they should be mutually exclusive options."
      elif data_type == 'bool':
         self.options = [True, False]
         options_description = "True and False will be the only options for this field."
      elif data_type == 'str':
         options_description = "Users will be able to input text for this field with no restrictions."
      self.description = options_description

   def set_options(self, **kwargs):
      if self.bsonType == 'int':
         min_value = kwargs['min_value']
         max_value = kwargs['max_value']
         if (type(min_value) == int and type(max_value) == int):
            self.minimum = min_value
            self.maximum = max_value
         else:
            raise DataValidationValueError("For int field, either the min or max value wasn't an integer.")

      elif self.bsonType == 'enum':
         options = kwargs['options']
         if type(options) == list:
            if len(options) <= 1:
               raise DataValidationValueError("Not enough options provided. Enum field requires at least 2 options.")
            elif len(options) > 1:
               self.options = options
         elif type(options) != list:
            raise DataValidationTypeError("Options for an enum field must be formatted as a list.")
