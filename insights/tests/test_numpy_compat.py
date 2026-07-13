from pathlib import Path
import tomllib
import unittest


class TestNumpyCompat(unittest.TestCase):
	def test_numpy_dependency_is_capped_before_x86_v2_wheels(self):
		pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
		project_config = tomllib.loads(pyproject_path.read_text())
		dependencies = project_config["project"]["dependencies"]

		numpy_dependencies = [dependency for dependency in dependencies if dependency.startswith("numpy")]

		self.assertTrue(numpy_dependencies)
		self.assertTrue(any("<2.4.0" in dependency for dependency in numpy_dependencies))


if __name__ == "__main__":
	unittest.main()
