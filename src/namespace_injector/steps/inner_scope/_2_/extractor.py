from src.namespace_injector.steps.outer_scope._1_.create_getter import GetterInfo


def extract_values(prepared: dict[str, GetterInfo]):
    "Add only values (omit generators)"
    return {
        k: v['value']
        for k, v in prepared.items()
    }
