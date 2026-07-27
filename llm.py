#!/usr/bin/env python

from pathlib import Path
import ollama
import json

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
                "date": "",
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
    return json.loads(response["message"]["content"])

if __name__=="__main__":
    path = Path("tests/lmm-notes")
    
    for i in range(100):
        file_name = path / f"{i}.json"
        with open(file_name, "w") as file:
            result = create_note()
            json.dump(result, file)
