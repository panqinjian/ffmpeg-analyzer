from typing import Dict, List, Optional, Union
from lexer.filter_lexer import FilterLexer, FilterTokenType
from core.error_types import FFmpegError, ErrorLevel
from parsers.semantic_analyzer import SemanticAnalyzer
from parsers.parser_models import ParsedCommand, Stream

class FilterParser:
    def __init__(self):
        self.current_streams = []  # 用于追踪当前流的上下文

    def parse(self, text: str) -> ParsedCommand:
        lexer = FilterLexer(text)
        tokens = lexer.tokenize()
        parsed_command = ParsedCommand(
            inputs=[],
            outputs=[],
            global_options={},
            filter_chains=[]
        )
        current_chain = []
        current_label = None

        while tokens:
            token_type, value = tokens.pop(0)

            # 处理流标签定义（如 [0:v]）
            if token_type == FilterTokenType.LBRACKET:
                label = self._parse_stream_label(tokens)
                current_label = label

            # 处理滤镜链分隔符（;）
            elif token_type == FilterTokenType.SEMICOLON:
                if current_chain:
                    parsed_command.filter_chains.append(current_chain)
                    current_chain = []

            # 处理滤镜表达式（如 scale=iw/2:ih/2）
            elif token_type == FilterTokenType.EXPRESSION:
                if "=" in value:
                    name, param_str = value.split("=", 1)
                    params = self._parse_params(tokens)
                    filter_node = FilterNode(
                        name=name,
                        params=params,
                        inputs=self._get_inputs(),  # 根据上下文获取输入流
                        outputs=[Stream(type="v", label=current_label)] if current_label else []
                    )
                    current_chain.append(filter_node)
                    current_label = None  # 重置标签

        return parsed_command

    def _parse_stream_label(self, tokens: list) -> str:
        """解析流标签（如 [0:v] -> 0:v）"""
        label_tokens = []
        while tokens and tokens[0][0] != FilterTokenType.RBRACKET:
            _, value = tokens.pop(0)
            label_tokens.append(value)
        tokens.pop(0)  # 移除右括号 ]
        return "".join(label_tokens)

    def _parse_params(self, tokens: list) -> Dict[str, str]:
        """解析参数（如 scale=iw/2:ih/2）"""
        params = {}
        param_str = ""
        while tokens:
            token_type, value = tokens[0]
            if token_type in (FilterTokenType.EXPRESSION, FilterTokenType.NUMBER, FilterTokenType.STRING, FilterTokenType.COLON):
                param_str += value
                tokens.pop(0)
            else:
                break
        param_list = param_str.split(":")
        for param in param_list:
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value
        return params

    def _get_inputs(self) -> List[Stream]:
        """根据上下文推断输入流（简化逻辑，实际需更复杂处理）"""
        # 示例：假设当前输入流为上一个滤镜的输出流
        return [Stream(type="v", label=self.current_streams[-1])] if self.current_streams else []

    def validate(self, parsed_command: ParsedCommand):
        for filter_chain in parsed_command.filter_chains:
            for node in filter_chain:
                if not self._is_valid_stream(node.inputs):
                    raise FFmpegError(
                        code="INVALID_STREAM",
                        message="无效的输入流标签",
                        suggestion="请检查输入流标签是否正确",
                        level=ErrorLevel.CRITICAL
                    )
                if not self._is_valid_stream(node.outputs):
                    raise FFmpegError(
                        code="INVALID_STREAM",
                        message="无效的输出流标签",
                        suggestion="请检查输出流标签是否正确",
                        level=ErrorLevel.CRITICAL
                    )

    def _is_valid_stream(self, streams: List[Stream]) -> bool:
        # TODO: 实现流标签有效性检查逻辑
        pass
