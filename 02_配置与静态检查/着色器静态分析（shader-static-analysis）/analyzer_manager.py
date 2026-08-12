from typing import List, Dict
from singleton import Singleton

# StrEnum add in python 3.11
from enum import StrEnum

from analyzer import Analyzer
from loop_analyzer import LoopAnalyzer
from struct_analyzer import StructAnalyzer
from function_analyzer import FunctionAnalyzer

from config import logger
import traceback

class AnalyzerType(StrEnum):
    LOOPANALYZER = "LoopAnalyzer"
    STRUCTANALYZER = "StructAnalyzer"
    FUNCTIONANALYZER = "FunctionAnalyzer"

black_list: List[AnalyzerType] = []
analyzer_list: List[AnalyzerType] = [
    AnalyzerType.LOOPANALYZER, 
    AnalyzerType.STRUCTANALYZER,
    AnalyzerType.FUNCTIONANALYZER
    ]

class AnalyzerManager(metaclass = Singleton):
    def __init__(self) -> None:
        self.__analyzers: List[Analyzer] = list()
        for analyzer in analyzer_list:
            if analyzer not in black_list:
                self.__analyzers.append(globals()[analyzer]())
    
    def analyze(self, file_name: str, code: str, output_csv: Dict):
        self.__init_code_map(code)
        for analyzer in self.__analyzers:
            try:
                analyzer.analyze(file_name, output_csv)
            except Exception as e:
                logger.error("An error occurred")
                logger.error("file: %s", file_name)
                logger.error("traceback: %s", str(traceback.format_exc()))

    def __init_code_map(self, code: str):
        Analyzer.reset_code_map()
        Analyzer.init_code_map(code)