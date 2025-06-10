import yaml
import json
import re
import asyncio
from pick_domains import pick_domains

class MockProvider:
    async def chat(self, messages):
        # Symulacja odpowiedzi providera
        query = messages[1]["content"]
        if "John Wick" in query:
            return json.dumps({
                "_thoughts": "1. Core concept: John Wick movies. 2. Use movie information sites.",
                "queries": [
                    {"q": "John Wick movie series", "url": "wikipedia.org"},
                    {"q": "John Wick movie analysis", "url": "youtube.com"}
                ]
            })
        elif "functional programming" in query:
            return json.dumps({
                "_thoughts": "1. Core concept: functional programming. 2. Use programming resources.",
                "queries": [
                    {"q": "functional programming overment", "url": "youtube.com"}
                ]
            })
        elif "Nginx" in query and "DigitalOcean" in query:
            return json.dumps({
                "_thoughts": "1. Core concepts: Nginx, DigitalOcean, PostgreSQL. 2. Use official documentation.",
                "queries": [
                    {"q": "Nginx configuration DigitalOcean", "url": "digitalocean.com"},
                    {"q": "Nginx setup guide", "url": "nginx.org"},
                    {"q": "PostgreSQL performance optimization", "url": "postgresql.org"}
                ]
            })
        elif "Kubernetes" in query and "AWS" in query:
            return json.dumps({
                "_thoughts": "1. Core concepts: Kubernetes, AWS. 2. Use official documentation.",
                "queries": [
                    {"q": "Kubernetes AWS setup", "url": "kubernetes.io"},
                    {"q": "AWS EKS cluster setup", "url": "aws.amazon.com"}
                ]
            })
        elif "M1" in query and "M2" in query:
            return json.dumps({
                "_thoughts": "1. Core concepts: M1, M2, MacBook Pro. 2. Use comparison resources.",
                "queries": [
                    {"q": "M1 vs M2 MacBook Pro performance comparison", "url": "youtube.com"}
                ]
            })
        elif "Nginx" in query and "Node.js" in query:
            return json.dumps({
                "_thoughts": "1. Core concepts: Nginx, Node.js, reverse proxy. 2. Use official documentation.",
                "queries": [
                    {"q": "Nginx reverse proxy Node.js", "url": "nginx.org"}
                ]
            })
        elif "React" in query and "useEffect" in query:
            return json.dumps({
                "_thoughts": "1. Core concepts: React, useEffect, infinite loop. 2. Use React documentation.",
                "queries": [
                    {"q": "React useEffect infinite loop fix", "url": "react.dev"}
                ]
            })
        elif "Airtable" in query:
            return json.dumps({
                "_thoughts": "1. Core concepts: Airtable, open-source, alternative. 2. Use GitHub.",
                "queries": [
                    {"q": "open source Airtable alternative", "url": "github.com"}
                ]
            })
        else:
            return json.dumps({
                "_thoughts": "1. Core concept: basic query. 2. No relevant domains found.",
                "queries": []
            })

async def run_tests():
    # Wczytanie konfiguracji testów
    with open('pick_domains.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Utworzenie mock providera
    provider = MockProvider()
    
    # Uruchomienie testów
    for i, test in enumerate(config['tests'], 1):
        print(f"\nTest {i}:")
        print(f"Query: {test['vars']['query']}")
        
        # Wykonanie funkcji pick_domains
        result = await pick_domains(test['vars'], provider)
        
        # Sprawdzenie asercji
        for assertion in test['assert']:
            if assertion['type'] == 'is-json':
                try:
                    # Sprawdzenie struktury JSON
                    schema = assertion['value']
                    if schema['type'] == 'object':
                        if 'required' in schema:
                            for field in schema['required']:
                                if field not in result:
                                    print(f"✗ Missing required field: {field}")
                                    continue
                        if 'properties' in schema:
                            for field, field_schema in schema['properties'].items():
                                if field in result:
                                    if field_schema['type'] == 'array':
                                        if not isinstance(result[field], list):
                                            print(f"✗ Field {field} is not an array")
                                            continue
                                        if 'items' in field_schema:
                                            item_schema = field_schema['items']
                                            for item in result[field]:
                                                if not isinstance(item, dict):
                                                    print(f"✗ Item in {field} is not an object")
                                                    continue
                                                if 'required' in item_schema:
                                                    for req_field in item_schema['required']:
                                                        if req_field not in item:
                                                            print(f"✗ Missing required field {req_field} in item")
                                                            continue
                    print("✓ JSON validation passed")
                except Exception as e:
                    print(f"✗ JSON validation failed: {str(e)}")
            
            elif assertion['type'] == 'contains':
                if assertion['value'] not in str(result):
                    print(f"✗ Does not contain '{assertion['value']}'")
                else:
                    print(f"✓ Contains '{assertion['value']}'")
            
            elif assertion['type'] == 'not-contains':
                if assertion['value'] in str(result):
                    print(f"✗ Contains '{assertion['value']}'")
                else:
                    print(f"✓ Does not contain '{assertion['value']}'")
            
            elif assertion['type'] == 'regex':
                if not re.search(assertion['value'], str(result)):
                    print(f"✗ Regex '{assertion['value']}' did not match")
                else:
                    print(f"✓ Regex '{assertion['value']}' matched")

if __name__ == "__main__":
    asyncio.run(run_tests()) 