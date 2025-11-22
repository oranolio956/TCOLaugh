from neo4j import GraphDatabase
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class Neo4jManager:
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "panopticon_secret",
    ):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def add_node(self, uid: str, label: str, properties: Dict[str, Any]):
        if not self.driver:
            return
        query = f"MERGE (n:{label} {{uid: $uid}}) SET n += $props"
        with self.driver.session() as session:
            session.run(query, uid=uid, props=properties)

    def add_edge(
        self,
        source_uid: str,
        target_uid: str,
        rel_type: str,
        properties: Dict[str, Any] = {},
    ):
        if not self.driver:
            return
        # Generalized edge creation.
        # Requires both nodes to exist or be mergeable by UID.
        # We assume nodes have a 'uid' property index.
        # Correcting the syntax that Black complained about
        query = f"""
        MATCH (a {{uid: $source_uid}}), (b {{uid: $target_uid}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $props
        """
        with self.driver.session() as session:
            session.run(
                query, source_uid=source_uid, target_uid=target_uid, props=properties
            )

    def get_subgraph(self, start_uid: str, hops: int = 2) -> Dict[str, Any]:
        if not self.driver:
            return {}

        query = """
        MATCH (start {uid: $start_uid})
        CALL apoc.path.subgraphAll(start, {
            maxLevel: $hops
        })
        YIELD nodes, relationships
        RETURN nodes, relationships
        """

        with self.driver.session() as session:
            result = session.run(query, start_uid=start_uid, hops=hops)
            record = result.single()
            if not record:
                return {"nodes": {}, "edges": []}

            nodes_out = {}
            for node in record["nodes"]:
                # Neo4j Node -> Dict
                labels = list(node.labels)
                primary_label = labels[0] if labels else "Unknown"
                props = dict(node)
                uid = props.get("uid", str(node.id))
                nodes_out[uid] = {"type": primary_label, "properties": props}

            edges_out = []
            for rel in record["relationships"]:
                edges_out.append(
                    {
                        "source": rel.start_node.get("uid"),
                        "target": rel.end_node.get("uid"),
                        "type": rel.type,
                        "properties": dict(rel),
                    }
                )

            return {"nodes": nodes_out, "edges": edges_out}
