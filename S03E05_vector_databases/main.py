import os
import requests
from dotenv import load_dotenv
from neo4j import GraphDatabase
import json
from typing import List, Dict
import urllib3

# Wyłącz ostrzeżenia o niezabezpieczonym połączeniu HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ładowanie zmiennych środowiskowych
load_dotenv()

API_DB_URL = os.getenv("API_DB_URL")
REPORT_URL = os.getenv("REPORT_URL")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
API_KEY = os.getenv("AIDEVS_API_KEY")

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            self.driver.verify_connectivity()
        except Exception as e:
            print(f"Neo4j connection error: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def clear_database(self):
        if not self.driver: return
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def create_person(self, name, person_id):
        if not self.driver: return
        with self.driver.session() as session:
            session.run(
                "MERGE (p:Person {personId: $personId}) SET p.name = $name",
                name=name, personId=person_id
            )

    def create_connection(self, person1_id, person2_id):
        if not self.driver: return
        with self.driver.session() as session:
            session.run(
                """
                MATCH (p1:Person {personId: $person1_id})
                MATCH (p2:Person {personId: $person2_id})
                MERGE (p1)-[:KNOWS]->(p2)
                """,
                person1_id=person1_id, person2_id=person2_id
            )

    def find_shortest_path(self, start_name, end_name) -> List[str]:
        if not self.driver: return []
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH p = shortestPath((start:Person {name: $start_name})-[*]-(end:Person {name: $end_name}))
                RETURN [node IN nodes(p) | node.name] AS path_names
                LIMIT 1
                """,
                start_name=start_name, end_name=end_name
            )
            record = result.single()
            return record["path_names"] if record else []

def get_database_data() -> tuple[List[Dict], List[Dict]]:
    try:
        users_payload = {
            "apikey": API_KEY,
            "task": "database",
            "query": "SELECT id, username FROM users ORDER BY id"
        }
        users = requests.post(API_DB_URL, json=users_payload, verify=False).json().get('reply', [])
        users = [
            {'id': int(u['id']), 'username': u['username']}
            for u in users if 'id' in u and 'username' in u
        ]
        connections_payload = {
            "apikey": API_KEY,
            "task": "database",
            "query": "SELECT * FROM connections"
        }
        connections = requests.post(API_DB_URL, json=connections_payload, verify=False).json().get('reply', [])
        connections = [
            {'user1_id': int(c['user1_id']), 'user2_id': int(c['user2_id'])}
            for c in connections if 'user1_id' in c and 'user2_id' in c
        ]
        return users, connections
    except Exception as e:
        print(f"Błąd pobierania danych: {e}")
        return [], []

def main():
    neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    if not neo4j_conn.driver:
        print("Brak połączenia z Neo4j.")
        return
    try:
        neo4j_conn.clear_database()
        users, connections = get_database_data()
        if not users:
            print("Brak danych użytkowników.")
            return
        for user in users:
            neo4j_conn.create_person(user['username'], user['id'])
        for connection in connections:
            neo4j_conn.create_connection(connection['user1_id'], connection['user2_id'])
        start_person_name = "Rafał"
        end_person_name = "Barbara"
        path_names = neo4j_conn.find_shortest_path(start_person_name, end_person_name)
        if path_names:
            answer = ",".join(path_names)
            print(f"Ścieżka: {answer}")
            response_payload = {
                "task": "connections",
                "apikey": API_KEY,
                "answer": answer
            }
            try:
                r = requests.post(REPORT_URL, json=response_payload)
                print(f"Odpowiedź wysłana. Status: {r.status_code}, Treść: {r.text}")
            except Exception as e:
                print(f"Błąd wysyłania odpowiedzi: {e}")
        else:
            print("Nie znaleziono ścieżki.")
    finally:
        neo4j_conn.close()

if __name__ == "__main__":
    main()