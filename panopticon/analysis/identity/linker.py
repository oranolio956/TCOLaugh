import logging
import pandas as pd
import duckdb
from typing import List, Dict, Any
from panopticon.persistence.sqlite_manager import db_instance

logger = logging.getLogger(__name__)

# Splink Import Strategy
try:
    from splink import Linker, block_on
    from splink.backends.duckdb import DuckDBAPI
    SPLINK_AVAILABLE = True
except ImportError:
    logger.warning("Splink not available. Using simple exact matching.")
    SPLINK_AVAILABLE = False

class IdentityLinker:
    """
    Uses Probabilistic Record Linkage (Splink) to resolve disconnected identities.
    """
    def __init__(self):
        pass
        
    def resolve_entities(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a list of flattened records (id, email, username, name...)
        and returns them with a 'cluster_id'.
        """
        if not records:
            return []

        df = pd.DataFrame(records)
        
        # Ensure ID column exists
        if "unique_id" not in df.columns:
            df["unique_id"] = range(len(df))

        # Basic cleanup
        for col in ["email", "username", "first_name", "last_name", "phone"]:
            if col not in df.columns:
                df[col] = None
            else:
                df[col] = df[col].astype(str).str.lower().replace("nan", None).replace("none", None)

        if SPLINK_AVAILABLE:
            return self._resolve_splink(df)
        else:
            return self._resolve_simple(df)

    def _resolve_splink(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        try:
            # Splink 4+ Configuration
            db_api = DuckDBAPI()
            
            settings = {
                "link_type": "dedupe_only",
                "unique_id_column_name": "unique_id",
                "blocking_rules_to_generate_predictions": [
                    block_on("email"),
                    block_on("username"),
                    block_on("phone"),
                ],
                "comparisons": [
                    {
                        "output_column_name": "email",
                        "comparison_levels": [
                            {
                                "sql_condition": "email_l IS NULL OR email_r IS NULL",
                                "label_for_charts": "Null",
                                "is_null_level": True
                            },
                            {
                                "sql_condition": "email_l = email_r",
                                "label_for_charts": "Exact match",
                                "m_probability": 0.9,
                                "u_probability": 0.01
                            },
                            {
                                "sql_condition": "ELSE",
                                "label_for_charts": "All other comparisons",
                                "m_probability": 0.1,
                                "u_probability": 0.99
                            }
                        ],
                        "comparison_description": "Exact match vs. anything else"
                    },
                    {
                        "output_column_name": "username",
                        "comparison_levels": [
                            {
                                "sql_condition": "username_l IS NULL OR username_r IS NULL",
                                "label_for_charts": "Null",
                                "is_null_level": True
                            },
                            {
                                "sql_condition": "username_l = username_r",
                                "label_for_charts": "Exact match",
                                "m_probability": 0.9,
                                "u_probability": 0.01
                            },
                            {
                                "sql_condition": "ELSE",
                                "label_for_charts": "All other comparisons",
                                "m_probability": 0.1,
                                "u_probability": 0.99
                            }
                        ]
                    },
                     {
                        "output_column_name": "phone",
                        "comparison_levels": [
                            {
                                "sql_condition": "phone_l IS NULL OR phone_r IS NULL",
                                "label_for_charts": "Null",
                                "is_null_level": True
                            },
                            {
                                "sql_condition": "phone_l = phone_r",
                                "label_for_charts": "Exact match",
                                "m_probability": 0.9,
                                "u_probability": 0.01
                            },
                            {
                                "sql_condition": "ELSE",
                                "label_for_charts": "All other comparisons",
                                "m_probability": 0.1,
                                "u_probability": 0.99
                            }
                        ]
                    }
                ],
                "retain_matching_columns": True,
                "retain_intermediate_calculation_columns": False,
                "additional_columns_to_retain": ["email", "username", "phone"]
            }

            linker = Linker(df, settings, db_api=db_api)
            
            # Predict
            df_predict = linker.inference.predict(threshold_match_probability=0.9)
            
            # Cluster
            df_clusters = linker.clustering.cluster_pairwise_predictions_at_threshold(df_predict, 0.9)
            
            # Merge back
            # df_clusters has 'unique_id' and 'cluster_id'
            # Convert Splink DataFrame to Pandas
            try:
                clusters_pdf = df_clusters.as_pandas_dataframe()
            except AttributeError:
                 # Try older/other method if as_pandas_dataframe fails
                clusters_pdf = df_clusters.to_pandas()

            result = df.merge(clusters_pdf, on="unique_id", how="left")
            
            # Convert back to list of dicts
            results = result.to_dict(orient="records")
            for r in results:
                r["match_type"] = "probabilistic"
                r["match_confidence"] = 0.9 # The threshold we used
                r["resolution_engine"] = "Splink (Fellegi-Sunter)"
            return results
            
        except Exception as e:
            logger.error(f"Splink resolution failed: {e}. Fallback to simple.")
            return self._resolve_simple(df)

    def _resolve_simple(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Simple exact match clustering on Email or Username.
        """
        clusters = {}
        next_cluster_id = 1
        
        # Map email/user to cluster_id
        email_map = {}
        user_map = {}
        
        result = df.to_dict(orient="records")
        
        for row in result:
            cid = None
            email = row.get("email")
            user = row.get("username")
            
            if email and email in email_map:
                cid = email_map[email]
            elif user and user in user_map:
                cid = user_map[user]
                
            if cid is None:
                cid = next_cluster_id
                next_cluster_id += 1
                
            if email: email_map[email] = cid
            if user: user_map[user] = cid
            
            row["cluster_id"] = cid
            row["match_type"] = "deterministic"
            row["match_confidence"] = 1.0
            row["resolution_engine"] = "Exact Match"
            
        return result

    def sync_to_graph(self, resolved_records: List[Dict[str, Any]]):
        """
        Updates the graph with Cluster Nodes.
        """
        for rec in resolved_records:
            cluster_id = rec.get("cluster_id")
            if not cluster_id:
                continue
                
            # Create Cluster Node
            c_uid = f"cluster:{cluster_id}"
            db_instance.add_node(c_uid, "IdentityCluster", {"cluster_id": str(cluster_id)})
            
            # Link attributes to Cluster
            if rec.get("email"):
                db_instance.add_edge(c_uid, f"email:{rec['email']}", "CONTAINS_IDENTITY")
            if rec.get("username"):
                db_instance.add_edge(c_uid, f"user:{rec['username']}", "CONTAINS_IDENTITY")
