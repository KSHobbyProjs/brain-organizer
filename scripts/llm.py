#!/usr/bin/env python

from pathlib import Path
import ollama
import json
import datetime

def create_note():
    response = ollama.chat(
            model="gemma4:latest",
            messages=[
                {
                    "role": "system",
                    "content": """
            You are a note generator.

            Generate a random note with a topic chosen from:
            - quantum physics
            - philosophy
            - psychology
            - existentialism
            - sociology

            Create: 
            - a title
            - a date
            - 2 sentences to 3 paragraphs of note content
            - relevant labels

            The notes should not be written from a first person 
            perspective. They are to be "summary"-like entries of a 
            specific topic.
            
            Return ONLY valid JSON.

            Schema:
            {
                "title": "",
                "date": "%Y-%m-%d",
                "text": "",
                "labels": []
            }
            """
                },
                {
                    "role": "user",
                    "contact": "Generate a note."
                }
            ],
            format="json"
        )
    return response["message"]["content"]

def _validate_note(result):
    try:
        result = json.loads(result)
        date = datetime.datetime.fromisoformat(result["date"])
        result["date"] = date.date().isoformat()
        result["title"] = str(result["title"])
        result["text"] = str(result["text"])
        result["labels"] = [str(l) for l in result["labels"]]
        return result
    except Exception as e:
        print(e)
        return False





if __name__=="__main__":
    path = Path("../tests/llm-notes")
   
    count = 100
    for i in range(100):
        file_name = path / f"{i}.json"
       
        result = _validate_note(create_note())
        if not result:
            count -= 1
            continue
        
        with open(file_name, "w") as file:
            json.dump(result, file)

    print(f"created {count} files.")
