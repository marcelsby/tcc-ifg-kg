import pandas as pd

from app.build_kg.database import (CypherCreateQueryBuilder, CypherQueryFilter,
                                   CypherQueryFilterType, Neo4jDataType)


def cqb_add_property_when_value_not_absent(query_builder: CypherCreateQueryBuilder, key, value,
                                           value_type: Neo4jDataType):
    if isinstance(value, str) and value.strip() == '':
        return

    if pd.notna(value):
        query_builder.add_property(key, value, value_type)


def remove_properties(properties_keys_to_be_removed: list[str], properties_keys: list[str]):
    return [prop for prop in properties_keys if prop not in properties_keys_to_be_removed]


class GeneralFilters:

    @staticmethod
    def integer_codigo_filter(codigo: int):
        return CypherQueryFilter("codigo", CypherQueryFilterType.EQUAL, codigo,
                                 Neo4jDataType.INTEGER)
