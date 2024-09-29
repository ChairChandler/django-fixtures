from src.steps.outer_scope._1_.create_getter import GetterInfo


def cleanup_generators(prepared: dict[str, GetterInfo]):
    "Cleanup generators (important for memory leakage)"
    for getter_info in prepared.values():
        if getter_info['generator']:
            getter_info['generator'].close()
