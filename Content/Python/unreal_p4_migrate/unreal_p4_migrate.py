import P4
import unreal as ue
try:
    from typing import Union, Tuple, Optional
    Text = Union[str, ue.Text]
except ImportError:
    # Not built-in in Py2. Only needed for dev.
    pass

from . import utils
from .dependency_search import DependencySearch


class UnrealP4Migrate(object):
    """
    Singleton class to be used by the UnrealP4Migrate editor
    utility widget.
    """
    __instance = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            return cls.__call__()
        return cls.__instance

    def __new__(cls):
        if UnrealP4Migrate.__instance is None:
            UnrealP4Migrate.__instance = object.__new__(cls)
        return UnrealP4Migrate.__instance

    def __init__(self):
        self.p4_obj = None  # type: P4.P4
        self.dependency_search = None  # type: DependencySearch

        self.p4_depot = None

    def reset(self, reset_p4=False):
        # type: (bool) -> None
        if reset_p4 or not self.is_connected():
            self.p4_obj = None
        self.dependency_search = None

    def is_connected(self):
        # type: () -> bool
        return self.p4_obj and self.p4_obj.connected()

    def connect(self, port, user, password, client):
        # type: (Text, Text, Text, Text) -> bool
        self.p4_obj = utils.connect_p4(str(port), str(user), str(password), str(client))
        if not self.p4_obj:
            ue.log_error("Failed to connect to Perforce")
            return False
        return True

    def get_stream(self):
        # type: () -> str
        if self.is_connected():
            return utils.get_current_stream(self.p4_obj)

    def get_depot(self):
        # type: () -> str
        if self.is_connected():
            depot_name = utils.get_depot(self.p4_obj)["Depot"]
            return "//" + depot_name

    def get_workspace_root(self):
        client_spec = self.p4_obj.fetch_client(self.p4_obj.client)

        client = client_spec["Root"]

        # Clean up slashes
        if "\\" in client:
            client = client.replace("\\", "/")
        while "//" in client:
            client = client.replace("//", "/")

        return client

    def gather_dependencies(self, asset_paths):
        self.dependency_search = DependencySearch(asset_paths)
        self.dependency_search.gather_all_dependencies()

    def _make_mapping(self, target_stream):
        """
        Iterates over the list of assets to merge,
        finds their path on disk, then finds the depot path,
        then from that makes the target depot path, and
        stores this mapping as a space-separated string (because
        that is what Perforce requires).

        Examples:
            //BDH/main/file //BDH/test/file

        Args:
            List[str]:

        Returns:
            List[str]
        """
        mapping = list()
        workspace_root = self.get_workspace_root()

        for asset in self.dependency_search.game_dependencies:
            try:
                on_disk = utils.get_on_disk_path(asset)
            except utils.FileNotFoundError:
                ue.log_warning("{} not found on disk".format(asset))
                continue
            source = utils.convert_local_path_to_depot(self.p4_obj, on_disk)
            if not source:
                ue.log_warning("{} does not exist on the depot".format(source))
                continue
            target = on_disk.replace(workspace_root, target_stream)
            mapping.append("{} {}".format(source, target))

        return mapping

    def create_branch_mapping(self, mapping_name, target_stream):
        """

        Args:
            mapping_name (str): What to call the new branch mapping
            target_stream (str): e.g. "//SomeDepot/somestream"

        Returns:

        """
        if not self.dependency_search:
            ue.log_error("Can't create branch mapping. Dependencies not yet gathered.")
            return

        mapping = self._make_mapping(target_stream)
        try:
            branch = self.p4_obj.fetch_branch(mapping_name)
            branch["View"] = mapping
            self.p4_obj.save_branch(branch)
        except P4.P4Exception as e:
            ue.log_error("Failed to create branch mapping. Perforce Error: {}".format(e))
        else:
            ue.log_warning("Branch mapping successfully created.")


def get_instance():
    # type: () -> UnrealP4Migrate
    return UnrealP4Migrate.instance()
