import datetime
import chromadb
import pandas as pd
import time
import traceback
from openai import APIError, APIStatusError

from chromadb.utils import embedding_functions

from model_configurations import get_model_configuration

gpt_emb_version = "text-embedding-ada-002"
gpt_emb_config = get_model_configuration(gpt_emb_version)

dbpath = "./"
csv_file = "COA_OpenData.csv"


def generate_hw01():
    try:
        # Create embedding function
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=gpt_emb_config["api_key"],
            api_base=gpt_emb_config["api_base"],
            api_type=gpt_emb_config["openai_type"],
            api_version=gpt_emb_config["api_version"],
            deployment_id=gpt_emb_config["deployment_name"],
        )

        # Create chromadb
        chroma_client = chromadb.PersistentClient(path=dbpath)

        # Create new collection to store or retrieve data
        collection = chroma_client.get_or_create_collection(
            name="TRAVEL",
            metadata={"hnsw:space": "cosine"},
            embedding_function=openai_ef,
        )

        if collection.count() == 0:
            # Read data from csv file
            data = pd.read_csv(csv_file)
            for index, row in data.iterrows():
                id = str(row["ID"])
                metadata = {
                    "file_name": csv_file,
                    "name": row["Name"],
                    "type": row["Type"],
                    "address": row["Address"],
                    "tel": row["Tel"],
                    "city": row["City"],
                    "town": row["Town"],
                    "date": int(
                        datetime.datetime.strptime(
                            row["CreateDate"], "%Y-%m-%d"
                        ).timestamp()
                    ),
                }
                document = row["HostWords"]

                # Add metadata and document to the collection
                collection.add(ids=id, metadatas=metadata, documents=document)

        return collection

    except APIStatusError as api_error:
        print(f"API Status Error: {api_error}")
        print(f"Status code: {api_error.status_code}")
        print(f"Response: {api_error.response}")
        print(f"Body: {api_error.body}")
        print(traceback.format_exc())
        return None
    except APIError as api_error:
        print(f"API error: {api_error}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())
        return None


def generate_hw02(question, city, store_type, start_date, end_date):
    try:
        collection = generate_hw01()

        # Convert datetime to timestamps
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # Build where conditions for the query
        where_conditions = [
            {"city": {"$in": city}},
            {"type": {"$in": store_type}},
            {"date": {"$gte": start_timestamp}},
            {"date": {"$lte": end_timestamp}},
        ]

        # Query stores based on the question and filters
        result = collection.query(
            query_texts=[question],
            n_results=10,
            where={"$and": where_conditions},
            include=["metadatas", "distances"],
        )

        # Process and return results
        if result.get("metadatas") and result.get("distances"):
            # Return store names that meet the similarity threshold
            matching_stores = []
            for metadata, distance in zip(
                result["metadatas"][0], result["distances"][0]
            ):
                # Convert distance to similarity (1 - distance)
                similarity = 1 - distance
                if similarity >= 0.80:  # Keep the 0.80 threshold as per requirements
                    matching_stores.append((metadata["name"], similarity))

            # Sort by similarity in descending order
            matching_stores.sort(key=lambda x: x[1], reverse=True)
            return [name for name, _ in matching_stores]

        return []

    except APIStatusError as api_error:
        print(f"API Status Error: {api_error}")
        print(f"Status code: {api_error.status_code}")
        print(f"Response: {api_error.response}")
        print(f"Body: {api_error.body}")
        print(traceback.format_exc())
        return []
    except APIError as api_error:
        print(f"API error: {api_error}")
        print(traceback.format_exc())
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())
        return []


def generate_hw03(question, store_name, new_store_name, city, store_type):
    try:
        collection = generate_hw01()

        # Find the exact store using both query and where condition
        results = collection.query(
            query_texts=[store_name], n_results=10, where={"name": {"$eq": store_name}}
        )

        # Update store if found
        if results["ids"][0]:
            # Get the first matching store's metadata
            new_metadata = results["metadatas"][0][0]
            # Add new_store_name to metadata instead of replacing the original name
            new_metadata["new_store_name"] = new_store_name

            # Update the store with new metadata
            collection.delete(ids=[results["ids"][0][0]])
            collection.add(
                ids=[results["ids"][0][0]],
                documents=results["documents"][0],
                metadatas=[new_metadata],
            )

        # Build where conditions for the main query
        where_conditions = []
        if city:
            where_conditions.append({"city": {"$in": city}})
        if store_type:
            where_conditions.append({"type": {"$in": store_type}})

        where_clause = {"$and": where_conditions} if where_conditions else None

        # Query stores based on the question and filters
        result = collection.query(
            query_texts=[question],
            where=where_clause,
            include=["metadatas", "distances"],
            n_results=10,
        )

        # Process and return results
        if result.get("metadatas") and result.get("distances"):
            # Return store names, using new_store_name if available
            matching_stores = []
            for metadata, distance in zip(
                result["metadatas"][0], result["distances"][0]
            ):
                # Convert distance to similarity (1 - distance)
                similarity = 1 - distance
                if similarity >= 0.80:  # Keep the 0.80 threshold as per requirements
                    store_name = metadata.get(
                        "new_store_name", metadata.get("name", "Store name not found")
                    )
                    matching_stores.append((store_name, similarity))

            # Sort by similarity in descending order
            matching_stores.sort(key=lambda x: x[1], reverse=True)
            return [name for name, _ in matching_stores]

        return []

    except APIStatusError as api_error:
        print(f"API Status Error: {api_error}")
        print(f"Status code: {api_error.status_code}")
        print(f"Response: {api_error.response}")
        print(f"Body: {api_error.body}")
        print(traceback.format_exc())
        return []
    except APIError as api_error:
        print(f"API error: {api_error}")
        print(traceback.format_exc())
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())
        return []


def demo(question):
    chroma_client = chromadb.PersistentClient(path=dbpath)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=gpt_emb_config["api_key"],
        api_base=gpt_emb_config["api_base"],
        api_type=gpt_emb_config["openai_type"],
        api_version=gpt_emb_config["api_version"],
        deployment_id=gpt_emb_config["deployment_name"],
    )
    collection = chroma_client.get_or_create_collection(
        name="TRAVEL", metadata={"hnsw:space": "cosine"}, embedding_function=openai_ef
    )

    return collection


print(generate_hw01().count())
print(
    generate_hw02(
        question="我想要找有關茶餐點的店家",
        city=["宜蘭縣", "新北市"],
        store_type=["美食"],
        start_date=datetime.datetime(2024, 4, 1),
        end_date=datetime.datetime(2024, 5, 1),
    )
)
print(
    generate_hw03(
        question="我想要找南投縣的田媽媽餐廳，招牌是蕎麥麵",
        store_name="耄饕客棧",
        new_store_name="田媽媽（耄饕客棧）",
        city=["南投縣"],
        store_type=["美食"],
    )
)
