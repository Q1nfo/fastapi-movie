from enum import Enum


class Indexes(Enum):
    genre = {
        "mappings": {
            "properties": {
                "id": {
                    "type": "keyword",
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
                "description": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            }
        }
    }
    person = {
        "mappings": {
            "properties": {
                "id": {
                    "type": "keyword",
                },
                "full_name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
                "birth_date": {
                    "type": "keyword",
                },
            }
        }
    }

