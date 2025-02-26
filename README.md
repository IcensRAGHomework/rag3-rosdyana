[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/SQDH8b2K)
# Chromadb Assignment

## Assignment Content

Please use the **chromadb** package to complete the following tasks. Write the `COA_OpenData.csv` file into chroma.sqlite3 (you need to upload this file), and implement the following method in **`student_assignment.py`**: `generate_hw01-03(question)`
#### Create a `.env` file (for student use)

In this assignment, you will need to set up the necessary parameters in your local development environment to support the program's operation. To simplify the management of environment variables, please create a file named `.env` in the project root directory and define the environment variables in it.

The main purpose of this `.env` file is to allow you to implement it on your own computer and provide the necessary parameters for the `model_configurations.py` file. We will provide specific parameter values for you to fill in when participating in the assignment. Below is a sample format of the .env file:

```makefile
AZURE_OPENAI_EMBEDDING_ENDPOINT=your_endpoint_here
AZURE_OPENAI_EMBEDDING_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_EMBEDDING=your_deployment_embedding_here
AZURE_OPENAI_VERSION=your_api_version_here
AZURE_OPENAI_DEPLOYMENT_EMBEDDING_MODEL_NAME="text-embedding-ada-002"
AZURE_OPENAI_TYPE=your_openai_type_here
```
#### Notes

- **Do not upload the `.env` file to any version control system (e.g., GitHub)** to avoid leaking sensitive information.
- The `.env` file is only for use in your local environment and does not need to be included when submitting the assignment.


---

### Assignment 1: Initialize the Database and Add Metadata

1. **Description**: You need to store the data into the database (ChromaDB) first. This data includes the store's description text, basic information (such as name, type, address, etc.), which will serve as the basis for queries and filtering.
2. **Steps**
   - 1. Use the specified CSV file
      Please use the specified CSV file named `COA_OpenData.csv`. This file already contains all the required field data.
   - 2. Create a Collection
         Before writing data into the database, you need to create or obtain a Collection. Please ensure to use the following parameters to create the Collection:
          - **name**: `"TRAVEL"`, this is the name of the Collection, used to identify the purpose of this dataset.
          - **metadata**: `{"hnsw:space": "cosine"}`, this is the parameter for setting the similarity calculation, `cosine` means using cosine similarity for distance calculation.
   - 3. Metadata Content
      When initializing the database, you need to extract the relevant fields of each record from the CSV file and store them as Metadata in ChromaDB. Metadata includes the following information:
         - **file_name**: Source file name (`COA_OpenData.csv`).
         - **name**: Store name.
         - **type**: Store type, such as "Food", "Travel".
         - **address**: Store address.
         - **tel**: Store contact number.
         - **city**: Store city.
         - **town**: Store town.
         - **date**: Data creation date, needs to be converted to timestamp format (seconds) from the `CreateDate` field.
   - 4. Document Data (`documents`)
     Extract the content of the `HostWords` field from the CSV file as text data and store it in ChromaDB. This data is the core for similarity calculation during queries.
3. **Method**: Implement the `generate_hw01()` method, returning a collection object.
4. **Output Format**: Return a collection object `chromadb.api.models.Collection.Collection` (you need to upload the chroma.sqlite3 file first)
---

### Assignment 2

1. **Description**: `Query specific types of stores based on the document content and filter out results with a similarity score above **0.80** (presented in list format, sorted in descending order of similarity score)`
2. **Example**: `I want to find stores related to tea and snacks`
3. **Method**: Implement the `generate_hw02(question, city, store_type, start_date, end_date)` method to complete the following functions:
   - Accept user input questions and filter conditions to query stores that meet the conditions from the database.
   - When verifying the answer, the input filter parameters may not all be used.
   - Only return store names with a similarity score greater than or equal to **0.80**.
   - Set the number of query results to `10` (`n_results=10`).
4. **Parameters**:
   - `question` (str): User's query question, such as `"I want to find stores related to tea and snacks"`.
   - `city` (list): List of cities to filter, such as `["Yilan County", "New Taipei City"]`.
   - `store_type` (list): List of store types to filter, such as `["Food"]`.
   - `start_date` (datetime.datetime): Start date for filtering, such as `datetime.datetime(2024, 4, 1)`.
   - `end_date` (datetime.datetime): End date for filtering, such as `datetime.datetime(2024, 5, 1)`.
   
5. **Output Format**:
   - Format as follows:
     ```python
     ['Tea Village', 'Mountain Tea Garden', 'Happy Farmer Rice Shop', 'Sea View Cafe', 'Countryside Flavor Restaurant', 'Jade Dew Tea Station', 'Yijia Village Health Restaurant', 'North Sea Station Stone Meat Dumplings']
     ```

---

### Assignment 3

1. **Description**: Students need to complete the following two tasks:
   1. Update the information of a specified store in the database.
   2. According to the query conditions, the store names listed should be determined by the new parameters, and filter out results with a similarity score above **0.80** (presented in list format, sorted in descending order of similarity score)`
2. **Method**:
   - Implement the `generate_hw03(question, store_name, new_store_name, city, store_type)` method to complete the following functions:  
     1. Find the specified store and add a new parameter named `new_store_name` in the Metadata.  
     2. For the store names obtained through the question, if the store's Metadata has the `new_store_name` parameter, please use this parameter to display the new store name.  
     3. Set the number of query results to `10` (`n_results=10`).
3. **Parameters**:
   - `question` (str): User's query question, such as `"I want to find a Tien Mama restaurant in Nantou County, with buckwheat noodles as the signature dish"`.
   - `store_name` (str): Store name to search, such as `"Mao Tao Inn"`.
   - `new_store_name` (str): New parameter name to add, such as `"Tien Mama (Mao Tao Inn)"`.
   - `city` (list): List of cities to filter, such as `["Nantou County"]`.
   - `store_type` (list): List of store types to filter, such as `["Food"]`.
4. **Output Format**:
   - Format as follows
     ```python
     ['Tien Mama Community Restaurant', 'Dream Workshop', 'Mulberry Garden Workshop', 'Tien Mama (Mao Tao Inn)', 'Ren Shang Flavor Restaurant', 'Tien Mama Food Hall']
     ```

---

### Notes
- You must use the **Chromadb** package to complete the method implementation.
- Ensure the output format is consistent with the examples.

### Reference
- [Chromadb](https://docs.trychroma.com/guides)

