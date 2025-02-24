from collections import defaultdict
import os
import sys



class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["error_types.py", "filter_registry.py"])
from filters.video import *
from core.error_types import FFmpegError, ErrorLevel
from filter_registry import FilterRegistry, get_filter_spec
from filters.video import *


class SemanticAnalyzer:
    def __init__(self):
        self.defined_labels = set()
        self.used_labels = set()
        self.warnings = []
        self._filter_param_cache = defaultdict(dict)

    def validate(self, parsed_command):
        self._check_stream_labels(parsed_command)
        self._check_filter_parameters(parsed_command)
        self._check_output_mappings(parsed_command)

    def get_warnings(self):
        return self.warnings

    def _check_stream_labels(self, parsed_command):
        # 第一阶段：收集所有输出标签
        for chain in parsed_command.get("filter_chains", []):
            if output_label := chain.get("output"):
                if output_label in self.defined_labels:
                    raise FFmpegError(
                        code="DUP_LABEL",
                        message=f"重复定义的输出标签: [{output_label}]",
                        suggestion="确保每个输出标签唯一",
                        level=ErrorLevel.CRITICAL
                    )
                self.defined_labels.add(output_label)

        # 第二阶段：验证输入标签
        for chain in parsed_command.get("filter_chains", []):
            for input_label in chain.get("inputs", []):
                if input_label not in self.defined_labels:
                    if input_label in ["0:v", "0:a", "1:v", "1:a"]:
                        self.warnings.append(f"隐式输入流标签: {input_label}")
                        self.defined_labels.add(input_label)
                        continue
                    raise FFmpegError(
                        code="UNDEF_LABEL",
                        message=f"未定义的输入流标签: [{input_label}]",
                        suggestion="检查前置滤镜链的输出标签定义",
                        level=ErrorLevel.CRITICAL
                    )

    def _check_filter_parameters(self, parsed_command):
        for chain in parsed_command.get("filter_chains", []):
            for filter_str in chain.get("filters", []):
                name, params = self._parse_filter_string(filter_str)
                result = self._validate_filter(name, params)
                if result:
                    self.warnings.append(result)

    def _parse_filter_string(self, filter_str: str) -> tuple:
        if "=" not in filter_str:
            return filter_str, {}
        
        name_part, param_part = filter_str.split("=", 1)
        params = {}
        
        for pair in param_part.split(":"):
            if "=" not in pair:
                # 处理简单参数，将其视为默认参数
                params["default"] = pair.strip()
                continue
            key, value = pair.split("=", 1)
            params[key.strip()] = value.strip()
        
        return name_part.strip(), params

    def _validate_filter(self, name: str, params: dict):
        print(f"检查滤镜: {name}, 参数: {params}")
        spec = get_filter_spec(name)
        if not spec:
            raise FFmpegError(
                code="UNKNOWN_FILTER",
                message=f"未知滤镜: {name}",
                suggestion="检查滤镜名称拼写",
                level=ErrorLevel.CRITICAL
            )

        # 验证必要参数
        missing_params = [p for p in spec.required_params if p not in params]
        if missing_params:
            return {
                'error': 'MISSING_PARAMS',
                'message': f"{name} 滤镜缺少必要参数: {', '.join(missing_params)}"
            }

        # 验证参数范围
        for param, value in params.items():
            if param in spec.param_ranges:
                min_val, max_val = spec.param_ranges[param]
                try:
                    num_val = float(value)
                    if not (min_val <= num_val <= max_val):
                        raise FFmpegError(
                            code="PARAM_RANGE",
                            message=f"参数 {param}={value} 超出允许范围",
                            suggestion=f"有效范围: {min_val} ~ {max_val}",
                            level=ErrorLevel.WARNING
                        )
                except ValueError:
                    pass

    def _check_output_mappings(self, parsed_command):
        for output in parsed_command.get("outputs", []):
            if "map" not in output:
                self.warnings.append("输出未指定流映射，使用默认流")
            elif output["map"] not in self.defined_labels:
                raise FFmpegError(
                    code="OUTPUT_MAP_ERR",
                    message=f"未定义的输出映射: {output['map']}",
                    suggestion="确保滤镜链生成对应的输出标签",
                    level=ErrorLevel.CRITICAL
                )