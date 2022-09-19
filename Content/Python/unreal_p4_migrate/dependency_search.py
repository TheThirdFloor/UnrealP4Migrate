from . import utils
import unreal as ue
try:
    from typing import List, Iterable
except ImportError:
    # Not built-in in Py2. Only needed for dev.
    pass


class DependencySearch(object):
    default_options = ue.AssetRegistryDependencyOptions(include_soft_package_references=True,
                                                        include_hard_package_references=True,
                                                        include_searchable_names=False,
                                                        include_soft_management_references=False,
                                                        include_hard_management_references=False)

    def __init__(self, asset_paths):
        # type: (Iterable[str]) -> None
        self.asset_paths = set([str(a) for a in asset_paths])  # type: Set[str]
        self._asset_registry = ue.AssetRegistryHelpers.get_asset_registry()

        self._visited = set() # type: Set[str]

        self.engine_dependencies = set()  # type: Set[str]
        self.script_dependencies = set()  # type: Set[str]
        self.plugin_dependencies = set()  # type: Set[str]
        self.game_dependencies = set()  # type: Set[str]

    def gather_all_dependencies(self):
        """
        From the provided asset paths, gathers all dependencies. These will
        be sorted into engine, script, plugin, and game dependencies. Can be used
        for processes other than packaging. In that case, pass prep_output=False to
        skip disk checks.

        Returns:
            bool: Whether the gather completed successfully or not.
        """
        for asset_path in self.asset_paths:
            print(asset_path)
            if not utils.is_game_asset(asset_path):
                ue.log_error("{} is not in Game content. Can only find dependencies for Game content.")
                return False
            self.game_dependencies.add(asset_path)
            self._add_dependencies_recursive(asset_path)
        return True

    def _add_dependencies_recursive(self, asset_path):
        # type: (str) -> None
        self._visited.add(asset_path)
        dependencies = self._get_dependencies(asset_path)

        for dependency in dependencies:
            if dependency in self._visited:
                continue

            if utils.is_engine_asset(dependency):
                self.engine_dependencies.add(dependency)
                continue
            elif utils.is_script_asset(dependency):
                self.script_dependencies.add(dependency)
                continue
            elif utils.is_plugin_asset(dependency):
                self.plugin_dependencies.add(dependency)
                continue

            self.game_dependencies.add(dependency)
            self._add_dependencies_recursive(dependency)

    def _get_dependencies(self, asset_path):
        """ Wrapper on AssetRegistry.get_dependencies. Ensures that a list[str] is returned.

        Args:
            asset_path (str): The package path of the asset to get dependencies for.

        Returns:
            List[str]
        """
        dependencies = self._asset_registry.get_dependencies(asset_path, self.default_options)
        if dependencies:
            return [str(dep) for dep in dependencies]
        return []

    def get_required_plugins(self):
        # type: () -> Set[str]
        required_plugins = set()
        for asset_path in self.plugin_dependencies:
            # Asset path in the form "/PluginName/Folder/Asset"
            plugin = asset_path.split("/")[1]
            required_plugins.add(plugin)
        return required_plugins
