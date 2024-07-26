import os
import unreal as ue
import json


"""Keep settings as basic types for interoperability with Unreal Engine."""


DIR_NAME = "UnrealP4Migrate"
FILE_NAME = "unrealp4migrate_settings.json"


def get_dir():
    # type: () -> str
    save_dir = ue.Paths.project_saved_dir()
    folder = os.path.join(save_dir, DIR_NAME)
    return folder


def get_filepath():
    # type: () -> str
    folder = get_dir()
    filepath = os.path.join(folder, FILE_NAME)
    return filepath


def save_settings_to_disk(port, user, client, stream_option, stream, dry_run, remap_key, remap_value):
    # type: (str, str, str, str, str, bool, dict[str, str]) -> None
    """
    Raises:
        RuntimeError: If the directory cannot be created or the file cannot be written.
    """
    save_dir = get_dir()
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
        except OSError as e:
            raise RuntimeError("Failed to create directory: {}".format(e))

    settings_data = {
        "port": port,
        "user": user,
        "client": client,
        "stream_option": stream_option,
        "stream": stream,
        "dry_run": dry_run,
        "remap_key": remap_key,
        "remap_value": remap_value,
    }

    # Write settings to disk
    filepath = get_filepath()
    try:
        with open(filepath, "w") as f:
            json.dump(settings_data, f, indent=4)
    except Exception as e:
        raise RuntimeError("Failed to write settings to disk: {}".format(e))


def load_settings_from_disk():
    # type: () -> tuple[str, str, str, str, str, bool, str, str
    filepath = get_filepath()
    if not os.path.exists(filepath):
        raise RuntimeError("Settings file not found: {}".format(filepath))

    try:
        with open(filepath, "r") as f:
            settings_data = json.load(f)
            port = settings_data.get("port", "")
            user = settings_data.get("user", "")
            client = settings_data.get("client", "")
            stream_option = settings_data.get("stream_option", [])
            stream = settings_data.get("stream", "")
            dry_run = settings_data.get("dry_run", False)
            remap_key = settings_data.get("remap_key", "")
            remap_value = settings_data.get("remap_value", "")
    except Exception as e:
        ue.log_error("Failed to load settings from disk: {}".format(e))
        return "", "", "", "", False, {}

    return port, user, client, stream_option, stream, dry_run, remap_key, remap_value
