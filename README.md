# UnrealP4Migrate
UnrealP4Migrate is an Unreal plugin that facilitates content migration between Perforce streams by way of Perforce's copy up/merge down mechanism. It addresses a common problem in stream-based Perforce scenarios, where merging in P4V by selecting a folder either merges more files than desired to the target stream, adding clutter and using unneeded disk space, or not enough, leaving missing dependencies in Unreal. This Unreal plugin crawls dependencies in Unreal to determine the precise list of files to migrate, then builds a Perforce Branch Mapping to allow easy integration to the target stream in P4V.

![Create the branch mapping in Unreal.](/Resources/docs/images/UnrealP4Migrate_demo1.gif)

## Unreal Compatibility
Intended to be compatible with 4.27+.

## Install
Clone or unzip into the Unreal project's plugin folder. Structure should look like: 
- Content
- Plugins
  - UnrealP4Migrate
    - Content
    - UnrealP4Migrate.uplugin
- MyProject.uproject

This plugin uses the embedded Python interpreter in Unreal and requires the `p4python` package be installed. The main widget will assist with installing this package if it's not available the first time it is run (see Python Packages below).

## Usage
Run the Editor Utility Widget called UnrealP4Migrate. See [Editor Utility Widgets | Unreal Engine 4.27 Documentation](https://docs.unrealengine.com/4.27/en-US/InteractiveExperiences/UMG/UserGuide/EditorUtilityWidgets) for more info.

The tool requires that your Unreal content be contained in a Perforce workspace, and that that workspace be a part of a Stream-type depot. 

### Python Packages
If it is your first time running the tool, and you do not have all the Python requirements installed in your Python environment (namely, `p4python`), you will need to install Python requirements. The first page of the tool prompts you to do this. If the installation is successful, you will move to the second page. If not, check the output log for more detail.

### Perforce Login
If you've logged into Perforce in a previous session of the Unreal Editor, your server, username, and workspace will auto-populate. Otherwise, you will need to enter these values. You will always be prompted for a password. This is not saved to disk. Once you've entered these fields, click Connect. 

### Stream Selection
Source stream will be auto-populated with the current stream of the workspace you connected to. The checkboxes filter the list of available target streams. Choose a target stream. Make sure the primary assets you want to migrate are selected in the Content Browser, then click Gather Dependencies.

### Review
Review the list of Game Dependencies and ensure it contains what you want to migrate. If any dependencies are part of a plugin, a warning will list the Plugins at the bottom. These assets will not be migrated. Give your new branch mapping a sensible name. When you're ready, click Create Branch Mapping.

### P4V
After creating the branch mapping, you should open in P4V a workspace in the target stream. Open View->Branch Mappings. Right-click the Branch Mapping and click either "Merge/Integrate Files Using Branch Mapping" or "Copy Files Using Branch Mapping" depending on which is appropriate for the stream relationship. From here, review the potential Integration, resolve any conflicts, and submit.

![Use P4V to merge or copy in the target stream.](/Resources/docs/images/UnrealP4Migrate_demo2.gif)

## Development
Development should be done in the lowest compatible version, which is at the time of this writing, 4.27. 

For now, we are trying to maintain this as a Content-only plugin, meaning it contains no C++ source code. Because it is editor-only, it uses a combination of Editor Utility Widgets and Python to do its work. This makes deployment simple.

### Python
Python code should be compatible with Python 2.7 and Python 3.7+ until support for Unreal 4.27 is dropped.
