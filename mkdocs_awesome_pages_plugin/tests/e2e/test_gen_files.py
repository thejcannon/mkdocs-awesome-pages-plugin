import tempfile
from pathlib import Path

import yaml
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File

from .base import E2ETestCase


class GeneratedFiles(BasePlugin):
    def on_pre_build(self, *args, **kwargs):
        self.src_dir = tempfile.TemporaryDirectory()

    def on_post_build(self, *args, **kwargs):
        self.src_dir.cleanup()



    def on_files(self, files, config):
        docs_dir = Path(self.src_dir.name)
        section_dir = docs_dir / "section"
        section_dir.mkdir()
        (section_dir / "2.md").touch()
        (section_dir / "3.md").touch()
        subsection_dir = section_dir / "sub"
        subsection_dir.mkdir()
        (subsection_dir / "a.md").touch()
        (section_dir / ".pages").write_text(yaml.dump({"arrange": ["3.md", "sub", "..."]}))

        def write_files(path):
            for entry in path.iterdir():
                if entry.is_file():
                    files.append(
                        File(
                            f"{path.relative_to(docs_dir)}/{entry.name}",
                            src_dir=self.src_dir.name,
                            dest_dir=config["site_dir"],
                            use_directory_urls=config["use_directory_urls"],
                        )
                    )
                else:
                    write_files(path / entry.name)

        write_files(section_dir)
        return files

    @staticmethod
    def _write_files(path, files, config):
        for file in path.iterdir():
            if file.is_file():
                files.append(
                    File(
                        f"section/{file.name}",
                        src_dir=self.src_dir.name,
                        dest_dir=config["site_dir"],
                        use_directory_urls=config["use_directory_urls"],
                    )
                )


class TestGeneratedFiles(E2ETestCase):
    PLUGINS = [GeneratedFiles]

    def test_mixed(self):
        """See https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin/issues/78."""
        navigation = self.mkdocs(
            self.config,
            [
                (
                    "section",
                    ["1.md"],
                )
            ],
        )
        self.assertEqual(
            navigation,
            [
                (
                    "Section",
                    [("3", "/section/3"), ("1", "/section/1"), ("2", "/section/2")],
                )
            ],
        )

    def test_all_virtual(self):
        """See https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin/issues/78."""
        navigation = self.mkdocs(
            self.config,
            [],
        )
        self.assertEqual(
            navigation,
            [
                (
                    "Section",
                    [("3", "/section/3"), ("2", "/section/2")],
                )
            ],
        )

