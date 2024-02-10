from typing import List

from fastapi import FastAPI, File, UploadFile, status
import uvicorn

from utils import process_json_file, process_xml_file, merge_documents, normalize_document_values

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello World, this is an exctractor"}


@app.post("/upload_files")
def process_files(files: List[UploadFile] = File(...)):
    """
    Processes multiple XML and JSON files uploaded in a request.

    Args:
        files: List of files sent in the request.

    Returns:
        Dictionary containing the processed information from all documents,
        or an error message if processing fails.
    """
    
    processed_documents = []
    for file in files:        
        if file.content_type not in ("application/xml", "application/json"):
            return {"error": "Unsupported file type. Only XML and JSON are allowed."}, status.HTTP_400_BAD_REQUEST
        
        filename = file.filename
        if file.content_type == "application/xml":
            processed_doc = process_xml_file(filename)
        elif file.content_type == "application/json":
            processed_doc = process_json_file(filename)
        if processed_doc:
            processed_documents.append(processed_doc)
    
    if len(processed_documents) >= 1:    
        common_document = merge_documents(processed_documents)
        final_result = normalize_document_values(common_document)    
        return {'data': final_result}, status.HTTP_200_OK
    else:
        return {"error": "No valid files were processed."}, status.HTTP_400_BAD_REQUEST



if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)