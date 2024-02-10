import json
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List
import dateparser
from pymorphy2 import MorphAnalyzer


def normalize_date(date):
    """Parses a date string and returns it in the format '%d.%m.%Y'."""

    try:
        parsed_date = dateparser.parse(date)
        return parsed_date.strftime('%d.%m.%Y')        
    except Exception as e:        
        return None
             
    
def normalize_term(duration_string: str) -> str:
    """
    Normalizes a duration string to a format of `years_months_weeks_days`.

    Args:
        duration_string: The duration string to normalize.

    Returns:
        The normalized duration string in the format `years_months_weeks_days`.
    """
    
    duration_mapping = {"год": "years", "года": "years", "лет": "years","месяц": "months", "месяца": "months", "месяцев": "months",
                        "неделя": "weeks", "недели": "weeks", "недель": "weeks", "день": "days", "дня": "days", "дней": "days",
                        "полгода": "months", "полгод": "months"}
    numbers_dict = {"ноль": 0, "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7,
                    "восемь": 8, "девять": 9, "десять": 10, "одиннадцать": 11, "двенадцать": 12, "тринадцать": 13, "четырнадцать": 14,
                    "пятнадцать": 15, "шестнадцать": 16, "семнадцать": 17, "восемнадцать": 18, "девятнадцать": 19, "двадцать": 20, "тридцать": 30}

    result_delta = {'years': 0, 'months': 0, 'weeks': 0, 'days': 0}
    words = duration_string.split()
    for i, word in enumerate(words):
        if word in duration_mapping:
            if words[i-1].isdigit():
                value = int(words[i-1])
            else:
                morph_analyzer = MorphAnalyzer()
                if words[i-1] in numbers_dict:
                    value = numbers_dict[words[i-1]]
                elif morph_analyzer.parse(words[i-1])[0].normal_form in numbers_dict:
                    value = numbers_dict[morph_analyzer.parse(words[i-1])[0].normal_form]
                elif word == 'полгода':
                    value = 6
                else:
                    break
                
            result_delta[duration_mapping[word]] = value

    return f"{result_delta['years']}_{result_delta['months']}_{result_delta['weeks']}_{result_delta['days']}"


def normalize_document_values(document: Dict) -> Dict:
    """
    Normalizes dates and durations in a document.

    Args:
        document: The document to normalize.

    Returns:
        The document with normalized dates and durations.
    """

    for key, value in document.items():
        normalized_value = None
        if type(value) == dict:
            document[key] = normalize_document_values(value)
        if 'дата' in key.lower():
            normalized_value = normalize_date(value)            
        elif 'срок' in key.lower():
            normalized_value = normalize_term(value)
        if normalized_value is not None:
            document[key] = normalized_value
    return document   


def xml_to_dict(xml_element) -> Dict:
    """
    Converts an XML tree to a dictionary.

    Args:
        element: The XML tree to convert.

    Returns:
        A dictionary representing the XML tree.
    """
    
    result = {}
    for child in xml_element:
        if len(child) == 0:
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child.text)
            else:
                result[child.tag] = child.text
        else:
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(xml_to_dict(child))
            else:
                result[child.tag] = xml_to_dict(child)
    return result   


def json_to_dict(data )-> Dict:
    """
    Converts an JSON tree to a dictionary.

    Args:
        element: The JSON tree to convert.

    Returns:
        A dictionary representing the JSON tree.
    """
    
    if isinstance(data, list):
        return list(set(data))
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, list) and all(isinstance(item, dict) and len(item) == 1 for item in value):
                result[key] = [list(item.values())[0] for item in value]
            elif isinstance(value, dict):
                result[key] = json_to_dict(value)
            else:
                result[key] = value
        return result
    return data


def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return xml_to_dict(root)
    except Exception as e:
        print(e)
        return None 


def parse_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
        updated_data = json_to_dict(json_data)
        return updated_data
    

def process_xml_file(file_path):
    result = parse_xml(file_path)
    return result    


def process_json_file(file_path):
    result = parse_json(file_path)
    return result


def merge_documents(processed_documents: List[Dict]) -> Dict:
    """Merges all documents from the list.

    Args:
        processed_documents: The list of processed documents.
        merge_strategy: The first document is treated as the current one,
                        and each subsequent document is compared with the current one,
                        and the next comparison result is assigned to the current one.

    Returns:
        A merged document, `result`, containing the merged keys and values from all documents.   
    """
    
    result = processed_documents[0]
    for processed_document in processed_documents[1:]:            
        for key, value in processed_document.items():
            if key in result and isinstance(result[key], dict):
                result[key].update(value)
                if isinstance(result[key], list):
                    result[key] = {k: v for d in result[key] for k, v in d.items()}
            else:
                result[key] = value

    return result