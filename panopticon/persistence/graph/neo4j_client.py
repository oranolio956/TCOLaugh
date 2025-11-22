import logging

from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


class GraphManager:
    def __init__(self, uri: str, auth: tuple):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def create_person(self, person_data: dict):
        """
        Creates a Person node in the graph.
        """
        query = """
        MERGE (p:Person {uid: $uid})
        ON CREATE SET p.name = $name, p.dob = $dob
        """
        with self.driver.session() as session:
            session.run(query, **person_data)
            logger.info(f"Created/Merged Person {person_data.get('uid')}")

    def link_identifier(
        self, person_uid: str, identifier_type: str, identifier_value: str
    ):
        """
        Links a Person to an identifier (Email, Phone, etc.)
        """
        query = f"""
        MATCH (p:Person {{uid: $uid}})
        MERGE (i:{identifier_type} {{value: $val}})
        MERGE (p)-[:HAS_IDENTIFIER]->(i)
        """
        with self.driver.session() as session:
            session.run(query, uid=person_uid, val=identifier_value)
            logger.info(f"Linked {identifier_type} to Person {person_uid}")

    def merge_identities(self, uid1: str, uid2: str):
        """
        Merges two Person nodes if they are determined to be the same entity.
        """
        query = """
        MATCH (p1:Person {uid: $uid1})
        MATCH (p2:Person {uid: $uid2})
        CALL apoc.refactor.mergeNodes([p1, p2]) YIELD node
        RETURN node
        """
        # Note: This requires APOC plugin installed in Neo4j
        with self.driver.session() as session:
            session.run(query, uid1=uid1, uid2=uid2)
            logger.info(f"Merged Person {uid1} and {uid2}")
