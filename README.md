# Mongo Endjin
A re-imagining of MongoEngine

Why Mongo Endjin?
- The goal of mongoendjin is to stay as true as possible to Django.
    - The project structure, classes, methods, etc are written as close to Django as possible.
  
 Where does Mongo Endjin deviate from Django?
 - mongoendjin deviates from Django only where it makes sense for MongoDB
    - There are no relational fields as MongoDB is not a relational database.
    - All Field classes are MongoDB data types.
    - All MongoDB specific logic is located in mongoendjin.models.nosql
  
  




