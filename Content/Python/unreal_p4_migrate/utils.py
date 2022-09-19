import os
try:
    import configparser
except ImportError:
    # Py 2.7 compat
    import ConfigParser as configparser
try:
    from typing import List, Tuple, Optional
except ImportError:
    # Not built-in in Py2. Only needed for dev.
    pass

import P4

import unreal as ue


CONTENT_DIR = ue.Paths.project_content_dir()
UE_FILE_EXTENSIONS = [".uasset", ".umap"]


class FileNotFoundError(Exception):
    pass


def connect_p4(port, user, password, client):
    """

    Args:
        port (str):
        user (str):
        client (str):
        password (str):

    Returns:
        Optional[P4.P4]
    """
    p4 = P4.P4()
    p4.port = port
    p4.user = user
    p4.client = client
    p4.password = password

    try:
        p4.connect()
        p4.run_login()
        return p4
    except P4.P4Exception as e:
        print("Failed to connect to Perforce:")
        print(e)


def get_depot(p4_obj):
    # type: (P4.P4) -> P4.Spec
    stream = p4_obj.fetch_client(p4_obj.client)["Stream"]
    return get_depot_from_stream(p4_obj, stream)


def get_depot_from_stream(p4_obj, stream):
    # type: (P4.P4, str) -> P4.Spec
    for depot in p4_obj.iterate_depots():
        if stream.startswith("//{}/".format(depot["Depot"])):
            return depot


def get_current_stream(p4_obj):
    # type: () -> str
    client = p4_obj.fetch_client(p4_obj.client)
    return client["Stream"]


def get_all_streams(p4_obj, depot):
    """
    Returns all streams in the depot specified by the Show Config.

    Args:
        p4_obj (P4.P4):
        depot (str): Depot name, e.g. "//SomeDepot"

    Returns:
        List[str]: The stream path and stream name. See comment below.
    """
    streams = list()

    stream_data = p4_obj.run_streams("{}/...".format(depot))
    for stream_spec in stream_data:
        stream_path = stream_spec["Stream"]  # e.g. //BDH/test
        # stream_name = stream_spec["Name"]  # e.g. test
        streams.append(stream_path)
    return streams


def get_child_streams(p4_obj, depot, stream):
    """
    Returns streams that are children of the Stream. Does not
    return children's children.

    Args:
        p4_obj (P4.P4):
        depot (str):
        stream (str): Stream path, e.g. "//SomeDepot/main"

    Returns:
        List[str]: The stream path and stream name. See comment below.
    """
    streams = list()
    parent_stream = "{}/{}".format(depot, stream)

    stream_data = p4_obj.run_streams("{}/...".format(depot))
    for stream_spec in stream_data:
        parent = stream_spec["Parent"]
        if parent.lower() != parent_stream.lower():
            continue
        stream_path = stream_spec["Stream"]  # e.g. //BDH/test
        # stream_name = stream_spec["Name"]  # e.g. test
        streams.append(stream_path)
    return streams


def get_parent_stream(p4_obj, stream):
    """
    Returns streams that are children of the Stream.

    Args:
        p4_obj (P4.P4):
        stream (str): Stream path, e.g. "//SomeDepot/main"

    Returns:
        str: The parent's stream name, or "" if there is no parent.
    """
    streams = list()

    stream_spec = p4_obj.fetch_stream(stream)
    parent = stream_spec.get("Parent")
    if parent == 'none':
        parent = ""
    return parent


def convert_local_path_to_depot(p4_obj, local_path):
    """
    Tries to convert a path on disk, i.e. in a local
    workspace, to a depot path.

    Args:
        p4_obj (P4.P4):
        local_path (str): The local path

    Returns:
        Optional[str]: The path if found, else None.
    """
    try:
        specs = p4_obj.run("where", local_path)
    except P4.P4Exception:
        print("Could not convert {} to a depot path. ".format(local_path))
        return None

    for spec in specs:
        """
        'unmap' basically means the file doesn't actually live in that stream, 
        but because of certain stream rules (probably `import` or `import+`), 
        it presents as if it lives in that stream. We don't want that stream; 
        we want the stream the file actually lives in.
        """
        if "unmap" in spec:
            continue
        return spec.get("depotFile")


def is_engine_asset(asset_path):
    # type: (str) -> bool
    return asset_path.lower().startswith("/engine/")


def is_script_asset(asset_path):
    # type: (str) -> bool
    return asset_path.lower().startswith("/script/")


def is_game_asset(asset_path):
    # type: (str) -> bool
    return asset_path.lower().startswith("/game/")


def is_plugin_asset(asset_path):
    # type: (str) -> bool
    return not any([is_game_asset(asset_path),
                    is_script_asset(asset_path),
                    is_engine_asset(asset_path)]
                   )


def get_ue_version_as_float():
    version = ue.SystemLibrary.get_engine_version()
    tokens = version.split(".")
    return float("{}.{}".format(tokens[0], tokens[1]))


def get_cached_perforce_settings():
    """
    If Source Control is connected in Unreal and prefs have been saved,
    we can parse the current settings from SourceControlSettings.ini

    Example config (..\Saved\Config\Windows\SourceControlSettings.ini):

    [PerforceSourceControl.PerforceSourceControlSettings]
        Port=
        UserName=
        Workspace=
        HostOverride=
    [SourceControl.SourceControlSettings]
        Provider=Perforce
    """
    ue_version = get_ue_version_as_float()
    port = user = client = ""
    platform_token = 'Windows' if ue_version < 5.0 else 'WindowsEditor'
    cfg_path = os.path.join(ue.Paths.project_saved_dir(), 'Config', platform_token,
                            'SourceControlSettings.ini')
    if not os.path.exists(cfg_path):
        return None

    config = configparser.RawConfigParser()
    config.read(cfg_path)

    port = config.get("PerforceSourceControl.PerforceSourceControlSettings", "Port")
    user = config.get("PerforceSourceControl.PerforceSourceControlSettings", "UserName")
    client = config.get("PerforceSourceControl.PerforceSourceControlSettings", "Workspace")
    return port, user, client


def get_on_disk_path(asset_path):
    """
    To be run within Unreal. Forms and validates an on-disk path for the asset.
    Raises errors if path is not in the main content folder or if the asset does not exist on disk.

    Args:
        asset_path (str): The asset path relative to the content root, e.g. "/Game/Example"

    Returns:
        str: The absolute path on disk.

    Raises:
        FileNotFoundError
    """
    if not asset_path.startswith("/Game/"):
        raise FileNotFoundError("{} is not a valid game asset path. Must start with '/Game/".format(asset_path))

    pkg_dir = ue.Paths.get_path(asset_path).replace("/Game", "").lstrip("/")
    pkg_name = ue.Paths.get_base_filename(asset_path)

    print(CONTENT_DIR)
    print(pkg_dir)

    for ext in UE_FILE_EXTENSIONS:
        disk_path = ue.Paths.combine([CONTENT_DIR,
                                      pkg_dir,
                                      pkg_name + ext])
        print(disk_path)
        if os.path.exists(disk_path):
            return disk_path
    else:
        raise FileNotFoundError("No file exists on disk for asset path: {}".format(asset_path))
