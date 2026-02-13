import ingest
import sys


def main():
    try:
        assert len(sys.argv) == 2, "take just on path in argument"
        path = sys.argv[1]

        print(f"Load this file : {path}")
        docs = ingest.loader(path)

        if not docs:
            print("This is an empty files or could not be loaded.")
            return
        
        print("Chunk creation")
        chunks = ingest.text_splitter(docs)

        print("Generating embeddings")
        vector_data = ingest.get_embeddings_for_chunks(chunks)

        print(f"\nTotal number of vectors created : {len(vector_data)}")
        print(f"Vector dimension : {len(vector_data[0]['embedding'])}")

        if len(vector_data[0]['embedding']) == 768:
            print("The vectors do indeed add up to 768")
        ingest.upload_data_with_snowpark(vector_data)

    except FileNotFoundError:
        print("Error : The PDF file could not be found.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    


if __name__ == "__main__":
    main()

