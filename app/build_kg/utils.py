import pandas as pd

from app.build_kg.database import CypherCreateQueryBuilder, Neo4jDataType


def cqb_add_property_when_value_not_absent(query_builder: CypherCreateQueryBuilder, key, value,
                                           value_type: Neo4jDataType):
    if isinstance(value, str) and value.strip() == '':
        return

    if pd.notna(value):
        query_builder.add_property(key, value, value_type)
