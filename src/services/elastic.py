import json
from dataclasses import dataclass
from typing import Tuple, List

import backoff
import psycopg2
import requests
from elasticsearch import Elasticsearch, NotFoundError
from psycopg2.extras import DictCursor, RealDictCursor


@dataclass
class IndexBuilder:
    index_name: str
    model_from_postgres: str
    fields: list


class Indexer(object):

    def __init__(self, elasticsearch_client: Elasticsearch, new_index: IndexBuilder, body: dict):
        self.elastic = elasticsearch_client
        self.elastic_request = 'http://localhost:9200'
        self.index_name = new_index.index_name
        self.fields = new_index.fields
        self.model = new_index.model_from_postgres
        self.pg_conn = self._connection_postgres()
        self.cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
        self.body = body

    @staticmethod
    def _connection_postgres():
        """Подключение к POSTGRES."""
        dsl = {'dbname': 'movies_yandex', 'user': 'postgres', 'password': 12345, 'host': 'db,', 'port': 5432}

        return psycopg2.connect(**dsl, cursor_factory=DictCursor)

    def _execute_query(self, query: str, params: Tuple[str]) -> List[dict]:
        """
        Выполнение запроса к POSTGRES.
        В случае ошибки, проверка соединения и повторное попытка в соответсвии с модулем backoff
        """
        if not self.pg_conn or self.pg_conn.closed:
            self.pg_conn = self._connection_postgres()
            self.cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)

        self.cursor.execute(query, params)

        return self.cursor.fetchall()

    def _check_index(self, index_name: str):
        """Проверяет наличие индекса, если он есть возвращает его"""
        result = requests.get(f'{self.elastic_request}/{index_name}')
        if result:
            return result
        return False

    def _build_new_cards_index(self):
        """Если индекса еще не существует то создает его"""
        index = self._check_index(self.index_name)
        if index:
            return index
        else:
            index = self.create_empty_cards_index(self.index_name)

        return index

    def _collect_card_from_sql(self):
        """Собирает данные из Postgres"""
        query = f"""
                SELECT *
                FROM {self.model}            
        """
        cards = self._execute_query(query, params=('',))

        return cards

    def _transform_cards_to_elastic_format(self, cards):
        """Трансформирует данные для ELASTIC"""
        card_data = {}
        for row in cards:
            if row['id'] in card_data:
                data_card = card_data[row['id']]
            else:
                data_card = {}
                for field in self.fields:
                    data_card[field] = row[field]

                card_data[row['id']] = data_card

        return card_data.values()

    @backoff.on_exception(backoff.expo,
                          Exception,
                          jitter=None,
                          max_tries=10)
    def request_post(self, query: str) -> str:
        """
        Отправка запроса в ES и возврат ответа
        """

        return requests.post(
            f'{self.elastic_request}/{self.index_name}/_bulk',
            data=query,
            headers={
                'Content-type': 'application/x-ndjson'
            }
        ).content.decode()

    def _get_es_bulk_query(self, rows: List[dict], index_name: str) -> List[str]:
        """
        подготовка bulk запроса в Elasticsearch
        """
        prepared_query = []
        for row in rows:
            prepared_query.extend([
                json.dumps({'index': {'_index': index_name, '_id': row['id']}}),
                json.dumps(row)
            ])
        return prepared_query

    def load_to_es(self, records: List[dict], index_name: str) -> None:
        """
        Отправка запроса и разбор его ошибок
        """
        print('start WORK')
        prepared_query = self._get_es_bulk_query(records, index_name)
        str_query = '\n'.join(prepared_query) + '\n'

        self.request_post(str_query)

    def create_empty_cards_index(self, index_name):
        """Создает новый индекс"""
        try:
            new_index = self.elastic.create(index=index_name, body=self.body)
        except Exception as e:
            print(e)
            new_index = None

        return new_index

    def complete_index(self):
        """MAIN функция которые создает наполняет и возвращает индекс"""
        self._build_new_cards_index()

        cards = self._collect_card_from_sql()

        if cards:
            data = self._transform_cards_to_elastic_format(cards)
            self.load_to_es(records=data, index_name=self.index_name)
            return True

        return False
