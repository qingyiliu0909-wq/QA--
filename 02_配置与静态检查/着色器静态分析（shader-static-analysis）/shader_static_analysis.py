from __future__ import annotations
from typing import List
from antlr4 import *

from analyzer_manager import AnalyzerManager
from config import output_csv, code_file

import time

class CompileInputChunk:
    def __init__(self, file_name: str, text: str, context: str | None = None):
        self.file_name = file_name
        self.text = text
        self.context = context


class ChunkLoader:
    def load_compile_input_chunks(self, file_name: str) -> list[CompileInputChunk]:
        with open(file_name, "r", encoding="utf-8") as file:
            text = file.read()
        chunks = []
        lines = text.split("\n")
        i = 0
        file_name = ""
        text = ""
        code_push = False
        while i < len(lines):
            if lines[i].startswith("======================="):
                file_name = lines[i + 1]
                i += 2
            elif lines[i].startswith("```hlsl") or lines[i].startswith("``` hlsl"):
                code_push = True
                i += 1

            elif code_push and not lines[i].startswith("```"):
                text += lines[i] + "\n"
                i += 1
            elif code_push and lines[i].startswith("```"):
                code_push = False
                chunks.append(CompileInputChunk(file_name, text))
                text = ""
                i += 1
            else:
                i += 1
        return chunks

    def load_compile_input_chunk_from_input_text_file(
        self,
        file_name: str,
    ) -> list[CompileInputChunk]:
        with open(file_name, "r", encoding="utf-8") as file:
            text = file.read()
        chunks = []
        chunks.append(CompileInputChunk("default", text))
        return chunks


class PreProcessor:
    def __init__(self) -> None:
        self.__pre_process_macros = {"FLATTEN", "DEFINE_SKYATMLIGHTDIRECTION"}

    def _remove_pre_process_line(self, text: str, pre_process_macros: List[str]):
        lines = text.split("\n")
        for i in range(len(lines)):
            for macro in pre_process_macros:
                if macro in lines[i]:
                    lines[i] = ""
        return "\n".join(lines)

    def pre_process_HLSL(self, text: str):
        return self._remove_pre_process_line(text, self.__pre_process_macros)    


def main():
    chunks = ChunkLoader().load_compile_input_chunks(code_file)
    # chunks = load_compile_input_chunk_from_input_text_file("input.txt")
    output_csv_info = {}
    for chunk in chunks:
        code = PreProcessor().pre_process_HLSL(chunk.text)
        AnalyzerManager().analyze(chunk.file_name, code, output_csv_info)
    with open(output_csv, "w", encoding="utf-8") as csv_file:
        csv_file.write("Asset,Expression,ErrorLog \n")
        for file_name, error_msg_dict in output_csv_info.items():
            for expression_name, error_msg_list in error_msg_dict.items():
                for error_msg in error_msg_list:
                    csv_file.write('{},{},\"{}\"\n'.format(file_name, expression_name, error_msg))
    
if __name__ == "__main__":
    time_begin = time.time()
    main()
    time_end = time.time()
    print("Total time consume: {}".format(time_end - time_begin))