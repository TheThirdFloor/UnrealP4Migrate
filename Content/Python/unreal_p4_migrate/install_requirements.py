import os
import sys
import subprocess


REQUIREMENTS = os.path.join(os.path.dirname(__file__), "requirements.txt")


def get_python_exe():
	# type: () -> str
	if os.path.isabs(sys.prefix):
		return sys.executable
	python_dir = os.path.abspath(os.path.join(os.path.dirname(sys.executable), sys.prefix))	
	return os.path.join(python_dir, "python.exe")


def main():
	"""
	Returns True if install is successful or requirements
	already installed. Currently requirements are only p4python.
	Try to have minimal dependencies.

	Returns:
		bool
	"""
	try:
		import p4python
		print("p4python is already installed.")
		return True
	except ImportError:
		pass

	exe = get_python_exe()

	command = [exe, "-m", "pip", "install", "-r", REQUIREMENTS]

	# TODO: Print subprocess output to Unreal console
	ret_code = subprocess.call(command)

	if ret_code == "0":
		print("Requirements installed successfully.")
		return True
	print("Error installing requirements...")
	return False
