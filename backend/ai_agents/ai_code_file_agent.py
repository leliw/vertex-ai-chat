import os
from pathlib import Path
from typing import Any

from .ai_agent import AIAgent


class AICodeFileAgent(AIAgent):
    """Agent przeznaczony do obsługi plików zawierających kod"""

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
    def _read_files_to_markdown(cls, files: list[Path] = None, dir: Path = None) -> str:
        """Odczytuje fliki i zwraca sformatowany markdown.
        Nazwa pliku jest jako nagłówek 2, a treść jako kod"""

        if files is None and dir:
            # Jak podano katalog i nie ma plików,
            # to bierę wszyskie pliki z katalogu
            files = []
            skip_root_len = len(str(dir)) + 1
            for root, _, filenames in os.walk(dir):
                sub_dir = Path(root[skip_root_len:])
                for filename in filenames:
                    files.append(sub_dir.joinpath(filename))

        ret = ""
        for f in files:
            if dir:
                full_path = dir.joinpath(f)
            else:
                full_path = f
            if full_path.exists():
                ret += f"\n## {f}\n\n"
                lang = cls._decode_language(full_path.suffix[1:])
                with open(full_path, "r", encoding="utf8") as i:
                    ret += f"```{lang}\n{i.read()}\n```\n"
        return ret

    @classmethod
    def _decode_language(cls, file_ext: str) -> str:
        if (file_ext == 'py'):
            return 'python'
        elif (file_ext == 'ts'):
            return 'Typescript'
        else:
            return file_ext

    @classmethod
    def _extract_code_files(cls, markdown_text: str) -> list[tuple[Path, str]]:
        """
        Funkcja wyciąga nagłówki i kod z pliku Markdown, zachowując kolejność.

        Args:
            markdown_file (str): Ścieżka do pliku Markdown.

        Returns:
            list: Lista krotek, gdzie każda krotka zawiera nagłówek i listę fragmentów kodu pod nim.
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
        for file, body in files:
            if output_dir:
                full_path = output_dir.joinpath(file)
            else:
                full_path = file
            os.makedirs(full_path.parent, exist_ok=True)
            with open(full_path, "w", encoding="utf8") as f:
                f.write(body)

    def run(
        self, prompt: str, input_files: list[Path] = None, input_dir: Path = None
    ) -> str:
        if input_files or input_dir:
            prompt += "\n"
            prompt += self._read_files_to_markdown(dir=input_dir, files=input_files)
        result = super().run(prompt)
        return result

    def run_and_save_files(
        self,
        prompt: str,
        input_files: list[Path] = None,
        input_dir: Path = None,
        output_dir: Path = None,
    ) -> str:
        result = self.run(prompt, input_files, input_dir)
        output_files = self._extract_code_files(result)
        self._save_output_files(output_files, output_dir)
        return result
