# UnrealP4Migrate
An Unreal plugin to facilitate content migration between Perforce streams by way of Perforce's copy up/merge down mechanism.

## Unreal Compatibility
Intended to be compatible with 4.27+. Development should be done in the lowest compatible version. 

## Install
Clone or unzip into the Unreal project's plugin folder. Structure should look like: 
- Content
- Plugins
  - UnrealP4Migrate
    - Content
    - UnrealP4Migrate.uplugin
- MyProject.uproject

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