from pathlib import Path
from langchain_pipeline.retriever.vector_db import ingest_documents_from_folder
if __name__ == "__main__":
    docs_path = Path("langchain_pipeline/retriever/index/docs")
    result = ingest_documents_from_folder(docs_path)
    if result[0] is not None:
        print(f"문서 인덱싱 완료: {len(result[1])}개 청크")
    else:
        print("문서 인덱싱 실패")