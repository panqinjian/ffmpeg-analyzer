from collections import defaultdict
from core.error_types import FFmpegError, ErrorType
from filters.filter_registry import FilterRegistry, get_filter_spec
from parsers.filter_definitions import FILTER_DEFINITIONS
from parsers.parser_models import ParsedCommand, ParseResult, Stream, FilterChain
from parsers.some_parser import SomeParser, SomeParserConfig
from core.ffmpeg_query import FFmpegQuery
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SemanticAnalyzerConfig(SomeParserConfig):
    """语义分析器配置"""
    check_types: bool = True
    resolve_references: bool = True
    validate_values: bool = True

class SemanticAnalyzer(SomeParser):
    """FFmpeg命令语义分析器"""
    
    def __init__(self, config: Optional[SemanticAnalyzerConfig] = None):
        super().__init__(config or SemanticAnalyzerConfig())
        self.config: SemanticAnalyzerConfig = self.config  # 类型提示
        self.filter_definitions = FILTER_DEFINITIONS
        self.defined_labels = set()  # 已定义的流标签
        self.used_labels = set()     # 已使用的流标签
        self.parser = SomeParser()  # 确保初始化 parser 属性
        self.defined_streams = set()
        self.used_streams = set()
        self.output_streams = set()   # 作为输出的流标签
        self.ffmpeg_query = FFmpegQuery()  # 添加 FFmpeg 查询支持

    def _do_parse(self, text: str) -> Dict:
        """实现语义分析逻辑"""
        # 这里添加具体的语义分析实现
        result = {}
        
        # 示例实现
        if self.config.check_types:
            self._check_types(text)
        
        if self.config.resolve_references:
            self._resolve_references(text)
            
        if self.config.validate_values:
            self._validate_values(text)
            
        return result
    
    def _check_types(self, text: str) -> None:
        """检查类型"""
        pass
    
    def _resolve_references(self, text: str) -> None:
        """解析引用"""
        pass
    
    def _validate_values(self, text: str) -> None:
        """验证值"""
        pass

    def validate(self, command):
        """验证命令的语义正确性"""
        if isinstance(command, ParsedCommand):
            command = command.to_dict()
        elif not isinstance(command, dict):
            raise FFmpegError("无效的命令格式", "命令必须是字典格式或ParsedCommand对象")

        # 重置状态
        self.defined_streams.clear()
        self.used_streams.clear()
        self.output_streams.clear()

        # 收集所有初始流
        for stream in command["streams"]:
            stream_id = stream["id"]
            if ":v" in stream_id or ":a" in stream_id:  # 输入流标签
                self.defined_streams.add(stream_id)

        # 验证滤镜链
        for chain in command["filter_chains"]:
            # 验证输入流
            for input_stream in chain["inputs"]:
                if input_stream not in self.defined_streams:
                    raise FFmpegError(
                        f"未定义的输入流: {input_stream}",
                        error_type="SEMANTIC_ERROR",
                        suggestion="请先定义输入流再使用"
                    )
                self.used_streams.add(input_stream)

            # 验证输出流
            output = chain["output"]
            if output in self.output_streams:
                raise FFmpegError(
                    f"重复的输出标签: {output}",
                    error_type="SEMANTIC_ERROR",
                    suggestion="输出标签不能重复使用"
                )
            
            # 将输出流添加到已定义和输出集合中
            self.defined_streams.add(output)
            self.output_streams.add(output)

            # 验证滤镜参数
            for filter_def in chain["filters"]:
                try:
                    # 直接使用 FFmpegQuery 的验证方法
                    self.ffmpeg_query.validate_filter_params(
                        filter_def["name"], 
                        filter_def["params"]
                    )
                except FFmpegError:
                    # 直接重新抛出错误
                    raise

        return True

    def _validate_filter_params(self, filter_def):
        """验证滤镜参数"""
        name = filter_def["name"]
        params = filter_def["params"]

        try:
            # 使用 FFmpeg 查询验证参数
            self.ffmpeg_query.validate_filter_params(name, params)
        except FFmpegError as e:
            if e.error_type == "UNKNOWN_FILTER":
                # 对于未知滤镜，使用内置验证规则
                if name == "scale":
                    if "width" in params and not self._is_valid_dimension(params["width"]):
                        raise FFmpegError(
                            "无效的参数: width",
                            error_type="SEMANTIC_ERROR",
                            suggestion="宽度必须是数字或有效的表达式"
                        )
                    if "height" in params and not self._is_valid_dimension(params["height"]):
                        raise FFmpegError(
                            "无效的参数: height",
                            error_type="SEMANTIC_ERROR",
                            suggestion="高度必须是数字或有效的表达式"
                        )
            else:
                raise

    def _is_valid_dimension(self, value):
        """验证尺寸参数是否有效"""
        if value.isdigit():
            return True
        # 支持的表达式：iw/2, ih*1.5 等
        valid_expressions = {"iw", "ih", "in_w", "in_h", "out_w", "out_h"}
        operators = {"+", "-", "*", "/"}
        parts = ''.join(c if c not in operators else ' ' + c + ' ' for c in value).split()
        return all(p in valid_expressions or p.replace(".", "").isdigit() or p in operators for p in parts)

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

    def _build_stream_graph(self, parsed_command: ParsedCommand):
        """构建流标签依赖图"""
        graph = defaultdict(list)
        defined = set()
        
        for chain in parsed_command.filter_chains:
            for node in chain:
                # 记录定义
                for out_stream in node.outputs:
                    defined.add(out_stream.label)
                # 记录依赖
                for in_stream in node.inputs:
                    graph[in_stream.label].append(node.name)
        
        # 确保 '0:v' 被视为已定义的标签
        defined.add("0:v")
        
        return graph, defined

    
    def _check_stream_labels(self, parsed_command: ParsedCommand) -> None:
        for chain in parsed_command.filter_chains:
            if not chain:
                raise FFmpegError('Empty filter chain detected')
            
            # Check for valid stream labels
            if '[' in chain or ']' in chain:
                try:
                    self.parser._parse_stream_label(chain)
                except FFmpegError as e:
                    raise FFmpegError(f'Invalid stream label in filter chain: {chain}') from e

        defined = set()
        used = set()

        # 添加 FFmpeg 隐式输入流 (如 0:v, 1:a 等)
        implicit_streams = {"0:v", "0:a", "1:v", "1:a"}  # 根据实际情况扩展
        defined.update(implicit_streams)

        # 收集显式定义的流
        for chain in parsed_command.filter_chains:
            for node in chain:
                for output in node.outputs:
                    defined.add(output.label)

        # 验证使用的流
        for chain in parsed_command.filter_chains:
            for node in chain:
                for input_stream in node.inputs:
                    used.add(input_stream.label)
                    if input_stream.label not in defined:
                        raise FFmpegError(
                            code="UNDEFINED_STREAM",
                            message=f"未定义输入流: {input_stream.label}",
                            suggestion="请确保输入流在使用前已定义",
                            level=ErrorType.CRITICAL
                        )

        # 检查未闭合标签
        for label in parsed_command.inputs:
            if not label.startswith("["):
                raise FFmpegError(
                    code="INVALID_INPUT",
                    message=f"输入流格式错误: {label}",
                    suggestion="格式应为 [type:label]",
                    level=ErrorType.CRITICAL
                )

    def _detect_cycles(self, graph):
        """使用拓扑排序检测循环依赖"""
        in_degree = {u: 0 for u in graph}
        
        # 初始化所有节点的入度
        for u in graph:
            for v in graph[u]:
                if v not in in_degree:
                    in_degree[v] = 0  # 确保所有节点都在 in_degree 中

                in_degree[v] += 1
        
        queue = [u for u in in_degree if in_degree[u] == 0]
        while queue:
            u = queue.pop(0)
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        
        if any(in_degree[u] > 0 for u in in_degree):
            raise FFmpegError(
                code="CIRCULAR_DEPENDENCY",
                message="检测到流标签循环依赖",
                level=ErrorType.CRITICAL
            )

    def analyze(self, input_str):
        """分析滤镜字符串的语义"""
        try:
            # 提取流标识符
            stream_matches = re.findall(r'\[(\d+:[va])\]', input_str)
            for stream in stream_matches:
                if stream.startswith('1:'):  # 检查是否使用了未定义的流
                    raise FFmpegError(
                        f"使用了未定义的流: {stream}",
                        error_type="SEMANTIC_ERROR",
                        suggestion="请确保所有使用的流都已正确定义"
                    )
            return True
        except Exception as e:
            if not isinstance(e, FFmpegError):
                raise FFmpegError(str(e), error_type="SEMANTIC_ERROR")
            raise

# 确保导出类
__all__ = ['SemanticAnalyzer', 'SemanticAnalyzerConfig']