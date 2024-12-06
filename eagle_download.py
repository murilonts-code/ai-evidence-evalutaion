# Async function to download a file
import os
from typing import Optional

import aiofiles
import httpx

BASE_URL = "https://apicloud.networksecure.com.br/api/v1/grc/assessments/{assessment_id}/answers/{answer_id}/files/{file_id}"
TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0aFhCckJHa2lwWXNFTDJhMVZrYm1CaXdVZWdKcWxvemJucFNkWTJkY0tjIn0.eyJleHAiOjE3MzM1MTQ4OTksImlhdCI6MTczMzQ3ODg5OSwianRpIjoiOTFkNTRiYmQtOWIwOS00ZTMwLWE2ZTgtMDc0ZWEwM2JiNTYzIiwiaXNzIjoiaHR0cDovL2FwaWNsb3VkLm5ldHdvcmtzZWN1cmUuY29tLmJyL2F1dGgvcmVhbG1zL1JlZFRlYW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiOWNlMmEyMjktYzJlNC00ZTQxLWJlMWQtZDRjNjc4NWMyODRiIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoicnQtZWFnbGUiLCJzZXNzaW9uX3N0YXRlIjoiMzRkY2MyNTAtOTBhNi00NzdjLWE3NGEtNWEyYjQ3YTVhOGE2IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3JlZHZpZXcubmV0d29ya3NlY3VyZS5jb20uYnIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJBZG1pbmlzdHJhZG9yIiwiZGVmYXVsdC1yb2xlcy1yZWR0ZWFtIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJzaWQiOiIzNGRjYzI1MC05MGE2LTQ3N2MtYTc0YS01YTJiNDdhNWE4YTYiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImN1c3RvbWVySWQiOiI5OTQ2ZTM3ZS02M2EzLTQ2MmItOWY0Mi1lZmY0NTYxZDY1MTEiLCJuYW1lIjoibXVyaWxvIC0gdGVzdGUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJtdXJpbG9jaXJpbm9udHNAZ21haWwuY29tIiwiZ2l2ZW5fbmFtZSI6Im11cmlsbyAtIHRlc3RlIiwibG9jYWxlIjoicHQtQlIiLCJlbWFpbCI6Im11cmlsb2Npcmlub250c0BnbWFpbC5jb20iLCJtb2R1bGVzIjpbIlJlZCBWaWV3IiwiUmVzcG9zdGEgYSBJbmNpZGVudGVzIiwiSU5GT1NFQyIsIkdSQyIsIlRocmVhdCBJbnRlbGxpZ2VuY2UiLCJHZXJlbmNpYW1lbnRvIGRlIFZ1bG5lcmFiaWxpZGFkZXMiLCJFYWdsZSJdfQ.awYkj41s7hqIEPesDdpQeTDxXvrmtroWKdze5eWMtdXSvmTziavkbJjRvQp4_QfP6zhm6ZhMChJLlNKBIp65LBbj9UNK7LxAEjxbn2hSq-DyysIUTvL1E8OJhtgrJ8mZl-mKYBSk6A0T9XQrled_YOc7HQaMpgxgrrJ6YYrQ_w4OeiBfqBG-dZUjcQzBBC38ZESpLyQUYG2kod_ahQS_ArcOhWV0O-dnRYecQsQ0IdMpSjek8ajSncYA41zlMzSQhkg_El0hLAw1LPaKJ4eJfbQVDSZRhViKUAM6SxMr_wQiacfGmZAla3jwHEejh1QWdZemqpD3yi83zGlDoi7B-g"

async def download_file(file) -> Optional[str]:
    url = BASE_URL.format(
        assessment_id=file['assessmentid'],
        answer_id=file['answerid'],
        file_id=file['fileid'],
    )

    # file_name_split = file['file_name'].split('.')
    file_path = os.path.join('./', f'{file['fileid']}-{file['file_name']}')
    headers = {
                "Authorization": f"Bearer {TOKEN}"
            }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(response.content)
            return file_path
        except Exception as e:
            print(f"Error downloading file {file['file_name']}: {e}")
            return None
        

async def put_request(file_id: str, data: dict):
    url = f"https://apicloud.networksecure.com.br/api/v1/grc/assessments/files/{file_id}/ai"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as session:
        try: 
            response = await session.put(url, json=data, headers=headers)
            if response.status == 200:
                return await response.json()  # Parse the JSON response if needed
            else:
                return {
                    "status": response.status,
                    "message": await response.text()
                }
        except Exception as e:
            print(f"Error {e}")
            return None