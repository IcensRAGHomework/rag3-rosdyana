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


def generate_hw01():
    try:
        csv_file = "COA_OpenData.csv"
        # Load CSV data
        df = pd.read_csv(csv_file)

        chroma_client = chromadb.PersistentClient(path=dbpath)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=gpt_emb_config["api_key"],
            api_base=gpt_emb_config["api_base"],
            api_type=gpt_emb_config["openai_type"],
            api_version=gpt_emb_config["api_version"],
            deployment_id=gpt_emb_config["deployment_name"],
        )

        collection = chroma_client.get_or_create_collection(
            name="TRAVEL",
            metadata={"hnsw:space": "cosine"},
            embedding_function=openai_ef,
        )

        # Prepare metadata and documents
        for _, row in df.iterrows():
            metadata = {
                "file_name": csv_file,
                "name": row["Name"],
                "type": row["Type"],
                "address": row["Address"],
                "tel": row["Tel"],
                "city": row["City"],
                "town": row["Town"],
                "date": int(
                    time.mktime(
                        datetime.datetime.strptime(
                            row["CreateDate"], "%Y-%m-%d"
                        ).timetuple()
                    )
                ),
            }
            document = row.get("HostWords", "")
            id = str(row["ID"])
            collection.add(ids=[id], documents=[document], metadatas=[metadata])

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
        # Initialize ChromaDB client and embedding function
        chroma_client = chromadb.PersistentClient(path=dbpath)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=gpt_emb_config["api_key"],
            api_base=gpt_emb_config["api_base"],
            api_type=gpt_emb_config["openai_type"],
            api_version=gpt_emb_config["api_version"],
            deployment_id=gpt_emb_config["deployment_name"],
        )

        # Get or create the collection
        collection = chroma_client.get_or_create_collection(
            name="TRAVEL",
            metadata={"hnsw:space": "cosine"},
            embedding_function=openai_ef,
        )

        # Query the collection with the question
        query_results = collection.query(query_texts=[question], n_results=10)

        # Process the query results
        matching_stores = []
        for i in range(len(query_results["ids"][0])):
            metadata = query_results["metadatas"][0][i]
            similarity = 1 - query_results["distances"][0][i]

            # Filter by similarity score
            if similarity < 0.80:
                continue

            # Filter by city (if provided)
            if city and metadata["city"] not in city:
                continue

            # Filter by store type (if provided)
            if store_type and metadata["type"] not in store_type:
                continue

            # Filter by date range
            entry_date = datetime.datetime.fromtimestamp(metadata["date"])
            if not (start_date <= entry_date <= end_date):
                continue

            # Add matching store name and similarity to the list
            matching_stores.append((metadata["name"], similarity))

        # Sort the results by similarity in descending order
        matching_stores.sort(key=lambda x: x[1], reverse=True)

        # Return only the store names
        return [name for name, _ in matching_stores]

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
        # Initialize ChromaDB client and embedding function
        chroma_client = chromadb.PersistentClient(path=dbpath)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=gpt_emb_config["api_key"],
            api_base=gpt_emb_config["api_base"],
            api_type=gpt_emb_config["openai_type"],
            api_version=gpt_emb_config["api_version"],
            deployment_id=gpt_emb_config["deployment_name"],
        )

        # Get or create the collection
        collection = chroma_client.get_or_create_collection(
            name="TRAVEL",
            metadata={"hnsw:space": "cosine"},
            embedding_function=openai_ef,
        )

        # Query the collection with the question
        query_results = collection.query(query_texts=[question], n_results=10)

        # Find the most relevant store
        most_relevant_store_id = None
        highest_similarity = -1
        for i in range(len(query_results["ids"][0])):
            metadata = query_results["metadatas"][0][i]
            similarity = 1 - query_results["distances"][0][i]
            current_id = query_results["ids"][0][i]

            # Check for filters and then check if store name matches
            if (
                similarity >= 0.80
                and (not city or metadata["city"] in city)
                and (not store_type or metadata["type"] in store_type)
                and metadata["name"] == store_name
            ):
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    most_relevant_store_id = current_id

        # Update the store if found
        if most_relevant_store_id:
            collection.update(
                ids=[most_relevant_store_id],
                metadatas=[{"name": new_store_name}],
            )
            return [most_relevant_store_id]  # Return the ID of the updated store
        else:
            print(f"No store found with name '{store_name}' matching the criteria.")
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
