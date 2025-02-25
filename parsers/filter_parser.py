from typing import Dict, List, Optional, Union
from parsers.lexer.filter_lexer import FilterLexer, FilterTokenType
from core.error_types import FFmpegError, ErrorLevel
from parsers.semantic_analyzer import SemanticAnalyzer
from parsers.parser_models import ParsedCommand, Stream, FilterNode, FilterChain

class FilterParser:
    def __init__(self):
        self.current_pos = 0
        self.text = ""

    def parse(self, text):
        """解析滤镜链文本"""
        try:
            self.text = text
            self.current_pos = 0
            
            streams = []
            filter_chains = []
            
            # 解析流标签和滤镜
            while self.current_pos < len(text):
                # 解析输入流标签
                input_streams = []
                while self.peek() == '[':
                    stream = self._parse_stream_label()
                    input_streams.append(stream["id"])
                    streams.append(Stream(**stream))

                # 解析滤镜名称和参数
                filter_name, params = self._parse_filter()
                
                # 解析输出流标签
                output_stream = None
                if self.peek() == '[':
                    output_stream = self._parse_stream_label()
                    streams.append(Stream(**output_stream))

                # 添加到滤镜链
                filter_chains.append(FilterChain(
                    inputs=input_streams,
                    output=output_stream["id"] if output_stream else None,
                    filters=[{"name": filter_name, "params": params}]
                ))

                # 跳过分隔符
                if self.peek() == ';':
                    self.current_pos += 1

            return ParsedCommand(streams=streams, filter_chains=filter_chains)

        except Exception as e:
            if not isinstance(e, FFmpegError):
                raise FFmpegError(
                    message=str(e),
                    error_type="PARSER_ERROR",
                    suggestion="请检查滤镜链语法是否正确"
                )
            raise

    def _parse_stream_label(self):
        """解析流标签 [label]"""
        if self.text[self.current_pos] != '[':
            raise FFmpegError(
                message="括号不匹配",
                error_type="PARSER_ERROR",
                suggestion="检查是否有未闭合的括号"
            )
        
        self.current_pos += 1
        label = ''
        
        while self.current_pos < len(self.text) and self.text[self.current_pos] != ']':
            label += self.text[self.current_pos]
            self.current_pos += 1
            
        if self.current_pos >= len(self.text) or self.text[self.current_pos] != ']':
            raise FFmpegError(
                message="括号不匹配",
                error_type="PARSER_ERROR",
                suggestion="检查是否有未闭合的括号"
            )
            
        self.current_pos += 1
        return {"id": label, "type": "video" if ":v" in label else "audio"}

    def _parse_filter(self):
        """解析滤镜名称和参数"""
        # 跳过空白字符
        while self.current_pos < len(self.text) and self.text[self.current_pos].isspace():
            self.current_pos += 1

        name = ''
        # 解析滤镜名称
        while (self.current_pos < len(self.text) and 
               (self.text[self.current_pos].isalnum() or self.text[self.current_pos] == '_')):
            name += self.text[self.current_pos]
            self.current_pos += 1
            
        if not name:
            # 检查是否在流标签后面
            if self.current_pos > 0 and self.text[self.current_pos - 1] == ']':
                name = 'scale'  # 默认滤镜
            else:
                raise FFmpegError(
                    message="缺少滤镜名称",
                    error_type="PARSER_ERROR",
                    suggestion="请指定有效的滤镜名称"
                )
            
        # 解析参数
        params = {}
        if self.peek() == '=':
            self.current_pos += 1
            if name == 'format':
                # 特殊处理 format 滤镜
                params = self._parse_format_params()
            else:
                params = self._parse_parameters()
        elif name == 'scale':
            # 为scale滤镜添加默认参数
            params = {"width": "iw", "height": "ih"}
        
        return name, params

    def _parse_format_params(self):
        """特殊处理 format 滤镜的参数"""
        params = {}
        value = ''
        
        # 跳过空白字符
        while self.current_pos < len(self.text) and self.text[self.current_pos].isspace():
            self.current_pos += 1
        
        # 收集到下一个分隔符前的所有字符
        while (self.current_pos < len(self.text) and 
               self.text[self.current_pos] not in '[];,'):
            value += self.text[self.current_pos]
            self.current_pos += 1
        
        if value:
            params['pix_fmt'] = value.strip()
        
        return params

    def _parse_parameters(self):
        """解析滤镜参数"""
        params = {}
        while self.current_pos < len(self.text):
            # 跳过空白字符
            while self.current_pos < len(self.text) and self.text[self.current_pos].isspace():
                self.current_pos += 1
            
            # 获取参数名或值
            value = ''
            while (self.current_pos < len(self.text) and 
                   self.text[self.current_pos] not in '[];,: \t\n'):
                value += self.text[self.current_pos]
                self.current_pos += 1
            
            if not value:
                break
            
            # 处理 scale=1280:720 这样的简写格式
            if value.isdigit():
                if len(params) == 0:
                    params["width"] = value
                else:
                    params["height"] = value
                # 跳过冒号
                if self.peek() == ':':
                    self.current_pos += 1
                continue
            
            # 处理常规 key=value 格式
            if self.peek() == '=':
                self.current_pos += 1
                param_name = value
                param_value = ''
                while (self.current_pos < len(self.text) and 
                       self.text[self.current_pos] not in '[];,'):
                    param_value += self.text[self.current_pos]
                    self.current_pos += 1
                params[param_name] = param_value.strip()
            
            # 跳过分隔符
            if self.peek() == ',':
                self.current_pos += 1
            
        return params

    def peek(self):
        """查看下一个字符"""
        return self.text[self.current_pos] if self.current_pos < len(self.text) else None

    def _parse_complex_label(self, tokens):
        """解析复合流标签（如 [0:v]overlay[x]）"""
        self._label_stack.append([])
        while tokens:
            token_type, value = tokens[0]
            if token_type == FilterTokenType.RBRACKET and len(self._label_stack) == 1:
                break
            # ... 解析逻辑
        return ''.join(self._label_stack.pop())

    def _parse_params(self, tokens: list) -> Dict[str, str]:
        """解析参数（如 scale=width=640:height=360）"""
        params = {}
        param_str = ""
        
        # 收集所有参数相关token（包括表达式、数字、字符串、冒号和等号）
        while tokens:
            token_type, value = tokens[0]
            if token_type in (
                FilterTokenType.EXPRESSION,
                FilterTokenType.NUMBER,
                FilterTokenType.STRING,
                FilterTokenType.COLON,
                FilterTokenType.EQUAL  # 关键修复：包含等号
            ):
                param_str += value
                tokens.pop(0)
            else:
                break
        
        # 分割参数对
        param_pairs = param_str.split(":")
        for pair in param_pairs:
            if "=" in pair:
                key_value_pairs = pair.split("=")
                key = key_value_pairs[0].strip()
                value = "=".join(key_value_pairs[1:]).strip()  # 处理多个等号的情况
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
