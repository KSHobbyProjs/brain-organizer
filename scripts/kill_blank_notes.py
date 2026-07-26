#!/usr/bin/env python3
"""
Short script that will delete all blank Keep notes from a directory
"""

from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
import re

def _get_all_files(directory: Path) -> (list[Path], list[Path], list[Path]):
    # collect all files
    tot_counter = 0
    json_files = []
    html_files = []
    others = []
    for file in directory.iterdir():
        tot_counter += 1
        if file.suffix == ".html":
            html_files.append(file)
        elif file.suffix == ".json":
            json_files.append(file)
        else:
            others.append(file)

    print(f"Total files: {tot_counter}")
    print(f"HTML files: {len(html_files)}")
    print(f"JSON files: {len(json_files)}")
    print(f"Other files: {len(others)}")
    print("----------------------------")
    return json_files, html_files, others

def _get_contents(json_files: list[Path]) -> (list[str], list[str], list[list[str]]):
    titles, texts, labels = [], [], []
    for file in json_files:
        # check json metadata to see if this note is blank
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)

            title = data.get("title", "")
            text = data.get("textContent", "")
            labels = data.get("labels", [])

            titles.append(title)
            texts.append(text)
            labels.append(labels)
    return titles, texts, labels

def _delete_notes_given_list(json_files: list[Path], delete_list: list[bool]):
    """ `json_files[i]` will be deleted if `delete_list[i]` is True """
    for i, file in enumerate(json_files):
        if delete_list[i]:
            Path.unlink(file)
            # grab html brother
            html_brother = f"{directory}/{file.stem}.html"
            if Path(f"{directory}/{file.stem}.html").exists():
                Path.unlink(Path(html_brother))
            else:
                print("No HTML brother found.")

def _get_length_stats(texts: list[str]):
    text_lengths = [len(text) for text in texts]
    print(
            f"Min, Max, Avg, Std (all text): "
            f"{min(text_lengths)}, {max(text_lengths)}, {np.mean(text_lengths):.1f}, {np.std(text_lengths):.1f}"
        )
    plt.hist(text_lengths, 100)
    plt.xticks(
            np.concatenate((
                np.arange(0, 1000, 200),
                np.arange(1000, 25000, 500)
                ))
            )
    #plt.show()

def _get_url_info(texts: list[str]):
    only_urls: list[bool] = []

    lengths = []
    URL = re.compile(r"https?://\S+")
    for text in texts:
        if re.findall(URL, text):
            text_without_url = URL.sub("", text).strip()
            if text_without_url:
                lengths.append(len(text_without_url))
                only_urls.append(False)
            else:
                only_urls.append(True)
        else:
            only_urls.append(False)

    print(
            f"Min, Max, Mean, Std (only text containing URLs): "
            f"{min(lengths)}, {max(lengths)}, {np.mean(lengths):.1f}, {np.std(lengths):.1f}"
        )
    return only_urls

    
def main(directory: str):
    directory = Path(directory)
    
    json_files, html_files, others = _get_all_files(directory)
    titles, texts, labels = _get_contents(json_files)       
    
    # grab empty notes and delete them
    has_no_text = [False if text else True for text in texts]
    #_delete_notes_given_list(json_files, has_no_text)

    _get_length_stats(texts)
    
    # grab notes with only URLs and delete them
    only_urls = _get_url_info(texts)
    #_delete_notes_given_list(json_files, only_urls)  

   
if __name__=="__main__":
    directory = "./tests/keep/"
    main(directory)
