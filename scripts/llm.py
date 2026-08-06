#!/usr/bin/env python

from pathlib import Path
import ollama
import json
import datetime
import random

from pydantic import BaseModel, ValidationError
from datetime import date

class Note(BaseModel):
    title: str
    date: date
    text: str
    labels: list[str]

class Topic(BaseModel):
    name: str
    parent: str
    subtopics: list[str]

class Angles(BaseModel):
    angles: list[str]

class Topics(BaseModel):
    topics: list[Topic]

def create_angles(num_angles: int):
    response = ollama.chat(
            model="gemma4:latest",
            messages=[
                {
                "role": "system",
                "content": f"""

            You are generating writing angles for notes in a semantic knowledge graph.

            A semantic knowledge graph is a collection of notes where related concepts
            are connected based on meaning. The notes will be embedded using a language
            model, so the goal is to create diverse perspectives that produce meaningful
            connections between related concepts.

            Generate {num_angles} unique angles.

            Examples of angles:
            - historical development
            - common misconception
            - practical applications
            - major debates
            - connections to other fields
            - unanswered questions

            Avoid angles that are too generic. 
            
            Return ONLY valid JSON.

            Schema:
            {{
                "angles": []
            }}
            """
                },
                {
                    "role": "user",
                    "content": "Generate angles."
                }
            ],
            format="json"
        )
    return response["message"]["content"]


def create_topics(num_topics: int, num_subtopics: int=5):
    response = ollama.chat(
            model="gemma4:latest",
            messages=[
                {
                "role": "system",
                "content": f"""
            You are generating writing topics for notes in a semantic knowledge graph.

            A semantic knowledge graph is a collection of notes where related concepts
            are connected based on meaning. The notes will be embedded using a language
            model, so the goal is to create diverse topics that produce meaningful
            connections between related concepts.

            Generate {num_topics} unique topics. For each topic,
            generate {num_subtopics} subtopics and a parent topic.

            Include some interdisciplinary topics that connect
            multiple fields. Include broad topics and niche topics.
 
            Return ONLY valid JSON.

            Schema:
            {{
                "topics": [
                    {{
                        "name": "",
                        "parent": "",
                        "subtopics": []

                    }}
                ]
            }}

            Example:
            {{
                "topics": [
                    {{
                    "name": "Quantum Physics",
                    "parent": "Physics",
                    "subtopics": [
                        "Measurement Problem",
                        "Quantum Information",
                        "Entanglement"
                        ]
                    }}
                ]
            }}
            """
                },
                {
                    "role": "user",
                    "content": "Generate topics."
                }
            ],
            format="json"
        )
    return response["message"]["content"]

def create_note(
        subtopic: str, 
        topic: str, 
        parent: str, 
        angle: str,
        avoids: list[str],
        temperature: float
    ):
    response = ollama.chat(
            model="gemma4:latest",
            messages=[
                {
                    "role": "system",
                    "content": f"""
            You are generating notes in a semantic knowledge graph.

            A semantic knowledge graph is a collection of notes where related concepts
            are connected based on meaning. The notes will be embedded using a language
            model, so the goal is to create diverse perspectives that produce meaningful
            connections between related concepts.

            Generate a note on subtopic {subtopic}, with topic {topic}, and umbrella topic
            {parent}. Write the note in the style of the following angle: {angle}.

            Avoid these previous topics:
            {json.dumps(avoids)}

            
            Create: 
            - a title
            - a date
            - 2 sentences to 3 paragraphs of note content
            - relevant labels

            The notes should not be written from a first person 
            perspective. They are to be "summary"-like entries of a 
            specific topic. Use the following angle: {angle}.
            
            Return ONLY valid JSON.
            
            Schema:
            {{
                "title": "",
                "date": "%Y-%m-%d",
                "text": "",
                "labels": []
            }}
            """
                },
                {
                    "role": "user",
                    "content": "Generate a note."
                }
            ],
            options={
                "temperature": temperature
            },
            format="json"
        )
    return response["message"]["content"]

def get_main_notes(
        path: Path,
        notes_per_topic: int, 
        topics: Topics, 
        angles: Angles, 
        temperature: float, 
        verbose: bool=True
    ):
    i = 0
    avoids = []
    
    for topic in topics.topics:
        for subtopic in topic.subtopics:
            for _ in range(notes_per_topic):
                angle = random.choice(angles.angles)
                run = True
                while run:
                    try: 
                        result = Note.model_validate_json(
                                create_note(
                                    subtopic,
                                    topic.name,
                                    topic.parent,
                                    angle,
                                    avoids, 
                                    temperature
                                )
                            )
                        run = False
                        i += 1
                    except ValidationError as e:
                        if verbose: 
                            print("\tNOTICE: Rejected Note.")
                if verbose: print(f"\tGenerated Note {i}.")
                
                avoids.append(result.title + result.text[:100])

                file_name = path / f"{i}.json"
                with open(file_name, "w") as file:
                    file.write(result.model_dump_json())
    return i

def validate(model: type[BaseModel], create_func, **kwargs):
    run = True
    while run:
        try:
            result = model.model_validate_json(create_func(**kwargs))
            run = False
        except ValidationError as e:
            print("\tRestarting...")
    return result

if __name__=="__main__":
    path = Path("../tests/llm-notes")

    num_topics = 10
    num_subtopics = 5
   
    num_angles = 10
    
    notes_per_topic = 2
    temperature = 1.2
   
    print("Getting angles...")
    angles = validate(Angles, create_angles, num_angles=num_angles)
    print(f"Got {len(angles.angles)} angles.")
   
    print("Getting topics...")
    topics = validate(Topics, create_topics, num_topics=num_topics, num_subtopics=num_subtopics) 
    print(f"Got {len(topics.topics)} topics.")
    print("Getting notes...")   
    i = get_main_notes(
            path, 
            notes_per_topic, 
            topics, 
            angles,
            temperature,
            verbose=True
        )
    print(f"Created {i} notes.")
