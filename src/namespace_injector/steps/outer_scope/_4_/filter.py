def filter_fixtures(fixtures_getters: dict, func_args_names: list[str]):
    "Set values for fixtures to be used in injector"
    return {
        prop_name: getter
        # we have to iterate over namespace class to have
        # exactly the same order of injecting properties
        # from top to bottom
        for (prop_name, getter) in fixtures_getters.items()
        if prop_name in func_args_names
    }
