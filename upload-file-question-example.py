import os
import json
import asyncio
import aiofiles
import httpx

from eagle_download import download_file, put_request
from extract_content import extract_text

# Configure your OpenAI API key here
QUESTION = """"
avalie o conteudo e identifique se adere como evidência ao item {categorycode} do CIS CONTROL v8 '{categoryname}', 
responda retornando um objeto do tipo json com o tipo boolean no campo valid em e insira a descrição em um JSON na propriedade description que deve ser do tipo texto.
o campo description tem que ser em português, tendo no máximo 1000 caracteres
"""

# Async function to send content and question to ChatGPT
async def ask_question(file_content: str, file ) -> str:
    quest = QUESTION.format(
        categoryname=file['categoryname'],
        categorycode=file['cattegorycode']
    )
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    messages = [
        {"role": "system", "content": "Você é um analista de GRC, responsável por validar documentos."},
        {"role": "user", "content": f"Conteudo: {file_content[:4000]}"},
        {"role": "user", "content": quest},
    ]

    data = {"model": "gpt-3.5-turbo-0125", "messages": messages}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error interacting with OpenAI API: {e}"

async def read_json(file_path: str) -> list:
    """
    Reads the JSON file and extracts all necessary properties from each object.
    """
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
        content = await f.read()
        json_data = json.loads(content)
        
        # Extract relevant properties
        extracted_data = []
        for item in json_data:
            fileid = item.get('fileid')
            cattegorycode = item.get('cattegorycode')
            standartname = item.get('standartname')
            assessmentid = item.get('assessmentid')
            answerid = item.get('answerid')
            categoryname = item.get('categoryname')
            file_name = item.get('file_name')
            
            # Add the extracted properties to the result list
            extracted_data.append({
                "fileid": fileid,
                "cattegorycode": cattegorycode,
                "standartname": standartname,
                "categoryname": categoryname,
                "answerid": answerid,
                "assessmentid": assessmentid,
                "file_name": file_name
            })
        
        return extracted_data

# Main async workflow
async def process_files(json_file: str, batch_size: int = 3) -> list:
    # Load file IDs from JSON
    file_data = await read_json(json_file)
    
    results = []
    for i in range(0, len(file_data), batch_size):
        batch = file_data[i:i + batch_size]
        
        # Process a batch of tasks concurrently
        batch_tasks = [process_single_file(file) for file in batch]
        results.extend(await asyncio.gather(*batch_tasks))
        
        # Add a delay between batches if needed
        await asyncio.sleep(0.5)  # Adjust delay to suit your server's needs

# Process a single file (download -> extract -> ask question)
async def process_single_file(file: str) -> dict:
    print(f"Processing file: {file['file_name']}")
    try:
        file_path = await download_file(file)
        print(file_path)
        if not file_path:
            return {"file_id": file['fileid'], "error": "Failed to download file"}
        
        file_content = extract_text(file_path)
        if not file_content:
            return {"file_id": file["fileid"], "error": "Failed to extract content"}
        
        answer = await ask_question(file_content, file)
        body = {"file_id": file['fileid'], "answer": json.loads(answer)}
        await put_request(file['fileid'], body)

        return body
    except Exception as e:
            return f"Error: {e}"
    finally:
        os.remove(file_path)
        
# Entry point
async def main():
    json_file = "Result_7.json"
    
    await process_files(json_file)
    
    print(f"Process finished with sucess")

if __name__ == "__main__":
    asyncio.run(main())

