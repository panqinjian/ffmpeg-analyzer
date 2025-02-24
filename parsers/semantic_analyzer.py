from collections import defaultdict
from core.error_types import FFmpegError, ErrorLevel
from filters.filter_registry import FilterRegistry, get_filter_spec
from .filter_definitions import FILTER_DEFINITIONS
from .parser_models import ParsedCommand


class SemanticAnalyzer:
    def __init__(self):
        self.filter_definitions = FILTER_DEFINITIONS
        self.defined_labels = set()  # 已定义的流标签
        self.used_labels = set()     # 已使用的流标签

    def validate(self, parsed_command: ParsedCommand) -> list:
        warnings = []
        self._check_filter_parameters(parsed_command, warnings)
        self._check_stream_labels(parsed_command, warnings)
        return warnings

    def _check_filter_parameters(self, parsed_command: ParsedCommand, warnings: list):
        for filter_node in parsed_command.get_filters():
            if filter_node.name not in self.filter_definitions:
                warnings.append({
                    "type": "UNKNOWN_FILTER",
                    "message": f"未知滤镜: {filter_node.name}",
                    "suggestion": "检查名称或更新滤镜库"
                })
                continue

            # 检查必填参数
            definition = self.filter_definitions[filter_node.name]
            required_params = [k for k, v in definition["parameters"].items() if v.get("required")]
            for param in required_params:
                if param not in filter_node.params:
                    warnings.append({
                        "type": "MISSING_PARAM",
                        "message": f"滤镜 `{filter_node.name}` 缺少必要参数: {param}",
                        "suggestion": f"添加参数 `{param}=...`"
                    })

    def _check_stream_labels(self, parsed_command: ParsedCommand, warnings: list):
        # 收集所有定义和使用的流标签
        for chain in parsed_command.filter_chains:
            for node in chain:
                # 记录输出流定义
                for output in node.outputs:
                    self.defined_labels.add(output.label)
                # 记录输入流使用
                for input_stream in node.inputs:
                    self.used_labels.add(input_stream.label)

        # 检查未定义的流
        for label in self.used_labels:
            if label not in self.defined_labels:
                warnings.append({
                    "type": "UNDEFINED_STREAM",
                    "message": f"流标签 `{label}` 未定义",
                    "suggestion": "在使用前通过 `[label]` 定义流"
                })

        # 检查未使用的流
        for label in self.defined_labels:
            if label not in self.used_labels:
                warnings.append({
                    "type": "UNUSED_STREAM",
                    "message": f"流标签 `{label}` 定义后未使用",
                    "suggestion": "清理未使用的流标签"
                })