"""AI Agent for generating code files."""

import logging
import os
from pathlib import Path
from typing import Any


from .ai_agent import AIAgent

type StrPath = str | Path


class AICodeFileAgent(AIAgent):
    """AI Agent for generating code files."""

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        model_name: str,
        system_instruction: str,
        generation_config: dict[str, Any] = None,
        safety_settings: dict = None,
    ) -> None:
        super().__init__(
            model_name,
            system_instruction
            + "\nPrzed każdym kodem podawaj proponowaną ścieżkę i nazwę pliku dla tego kodu jako nagłowek 2 markdown.",
            generation_config,
            safety_settings,
        )

    @classmethod
    def _read_files_to_markdown(
        cls, files: list[StrPath] = None, root_dir: Path = None
    ) -> str:
        """Read files and return them as markdown code blocks."""
        ret = ""
        for path, body in cls._read_files(files, root_dir):
            ret += f"\n## {str(path)}\n\n"
            lang = cls._decode_language(path.suffix[1:])
            ret += f"```{lang}\n{body}\n```\n"
        return ret

    @classmethod
    def _read_files(
        cls, files: list[StrPath] = None, root_dir: Path = None
    ) -> list[tuple[Path, str]]:
        """Read files and return them as a list of tuples (path, body)."""
        ret = []
        for f in files:
            if not isinstance(f, Path) and root_dir is None:
                f = Path(f)
            full_path = root_dir.joinpath(f) if root_dir else f
            if full_path.is_file():
                with open(full_path, "r", encoding="utf8") as b:
                    path = full_path.relative_to(root_dir) if root_dir else full_path
                    ret.append((path, b.read()))
            elif full_path.is_dir():
                sub = cls._read_files(
                    files=list(full_path.iterdir()), root_dir=root_dir
                )
                ret.extend(sub)
            else:
                cls._logger.error(f"File {full_path} not found")
                raise FileNotFoundError(f"File {full_path} not found")
        return ret

    @classmethod
    def _decode_language(cls, file_ext: str) -> str:
        """Decode file extension to language name."""
        if file_ext == "py":
            return "python"
        elif file_ext == "js":
            return "JavaScript"
        elif file_ext == "ts":
            return "TypeScript"
        else:
            return file_ext

    @classmethod
    def _extract_code_files(cls, markdown_text: str) -> list[tuple[Path, str]]:
        """Extract code files from markdown text.

        Args:
            markdown_text: Markdown text with code blocks.
        Returns:
            List of tuples (path, code).
        """
        headers_and_code = []
        current_header = None
        current_code_block = None

        for line in markdown_text.splitlines():
            if current_code_block is None and line.startswith("#"):
                # Nowy nagłówek
                if current_header:
                    headers_and_code.append(
                        (Path(current_header), current_code_block[0])
                    )
                current_header = line.split(" ", 1)[1]
                current_code_block = None
            elif line.startswith("```"):
                if current_code_block is None:
                    # Początek bloku
                    current_code_block = ""
                else:
                    # koniec bloku
                    headers_and_code.append((Path(current_header), current_code_block))
                    current_header = None
                    current_code_block = None
            elif current_code_block is not None:
                current_code_block += line
                current_code_block += "\n"

        # Dodaj ostatni nagłówek i kod do listy
        if current_header and current_code_block:
            headers_and_code.append((Path(current_header), current_code_block[0]))

        return headers_and_code

    @classmethod
    def _save_output_files(
        cls, files: tuple[Path, str], output_dir: Path = None
    ) -> None:
        """Save output files to the output directory.

        Args:
            files: List of tuples (path, code).
            output_dir: Output directory.
        """
        for file, body in files:
            if output_dir:
                full_path = output_dir.joinpath(file)
            else:
                full_path = file
            os.makedirs(full_path.parent, exist_ok=True)
            with open(full_path, "w", encoding="utf8") as f:
                f.write(body)

    def run(
        self, prompt: str, input_files: list[StrPath] = None, root_dir: Path = None
    ) -> str:
        """Run the model with the given prompt and return the response.

        Args:
            prompt: Prompt for the model.
            input_files: List of files to include in the prompt.
            root_dir: Root directory for the input files.
        Returns:
            Response from the model.
        """
        if input_files or root_dir:
            prompt += "\n"
            prompt += self._read_files_to_markdown(root_dir=root_dir, files=input_files)
        self._logger.debug(f"Prompt: \n{prompt}")
        result = super().run(prompt)
        self._logger.debug(f"Result: \n{result}")
        return result

    def run_and_save_files(
        self,
        prompt: str,
        input_files: list[StrPath] = None,
        root_dir: Path = None,
        output_dir: Path = None,
    ) -> str:
        """Run the model with the given prompt and save received files
        to the output directory.

        Args:
            prompt: Prompt for the model.
            input_files: List of files to include in the prompt.
            root_dir: Root directory for the input files.
            output_dir: Output directory for the files.
        Returns:
            Response from the model.
        """
        result = self.run(prompt, input_files, root_dir)
        output_files = self._extract_code_files(result)
        self._save_output_files(output_files, output_dir)
        return result
