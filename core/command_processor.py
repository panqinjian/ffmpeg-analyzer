import re
import shlex
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union
import os
import sys
import importlib

class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
from error_types import FFmpegError, ErrorLevel 

class FFmpegCommandProcessor:
    def __init__(self, enable_hw_accel: bool = True):
        self.semantic_analyzer = SemanticAnalyzer()
        self.accel_manager = AccelerationManager() if enable_hw_accel else None
        self.temp_dir = Path("/tmp/ffmpeg_proc")
        self.temp_dir.mkdir(exist_ok=True)

    def process_command(self, raw_command: str) -> Dict:
        """完整处理流程"""
        try:
            parsed = self._parse(raw_command)
            self.semantic_analyzer.validate(parsed)
            if self.accel_manager:
                parsed = self.accel_manager.optimize(parsed)
            cmd_str = self._generate_cmd(parsed)
            return self._execute(cmd_str)
        except FFmpegError as e:
            return self._format_error(e)

    def _parse(self, command: str) -> Dict:
        """深度解析命令结构"""
        parsed = {"inputs": [], "filters": [], "outputs": []}
        tokens = iter(shlex.split(command))
        
        while (token := next(tokens, None)) is not None:
            if token == "-i":
                parsed["inputs"].append({"path": next(tokens)})
            elif token == "-filter_complex":
                parsed["filters"] = self._parse_filter_complex(next(tokens))
            elif token.startswith(("-c:", "-c:v", "-c:a")):
                self._parse_codec(token, parsed)
            elif token == "-map":
                parsed["outputs"][-1]["map"] = next(tokens)
            else:
                self._parse_global(token, parsed)

        return parsed

    def _parse_filter_complex(self, filter_str: str) -> List:
        """解析滤镜链语法"""
        chains = []
        current = {"inputs": [], "filters": [], "output": None}
        
        for part in filter_str.split(';'):
            part = part.strip()
            if not part:
                continue
            
            # 提取输入输出标签
            inputs = re.findall(r'\[([^\]]+)\]', part)
            output_match = re.search(r'\[([^\]]+)\]$', part)
            
            current["inputs"].extend(inputs)
            current["filters"].extend(
                [f.strip() for f in part.split(']')[-1].split(',') if f.strip()]
            )
            if output_match:
                current["output"] = output_match.group(1)
                chains.append(current)
                current = {"inputs": [], "filters": [], "output": None}

        return chains

    def _generate_cmd(self, parsed: Dict) -> str:
        """生成可执行命令"""
        cmd = ["ffmpeg -y"]
        
        # 全局参数
        if threads := parsed.get("threads"):
            cmd.append(f"-threads {threads}")
        if hwaccel := parsed.get("hwaccel"):
            cmd.append(f"-hwaccel {hwaccel}")

        # 输入文件
        for inp in parsed["inputs"]:
            cmd.append(f"-i {shlex.quote(inp['path'])}")

        # 滤镜链
        if filters := parsed.get("filters"):
            cmd.append(f'-filter_complex "{self._build_filters(filters)}"')

        # 输出参数
        for out in parsed["outputs"]:
            if map_spec := out.get("map"):
                cmd.append(f"-map {map_spec}")
            if codec := out.get("codec"):
                cmd.append(f"-c:{codec['type']} {codec['name']}")
            cmd.append(shlex.quote(out["path"]))

        return " ".join(cmd)

    def _build_filters(self, chains: List) -> str:
        """构建滤镜链字符串"""
        filter_chain = []
        for c in chains:
            # 构建输入标签部分
            input_labels = "".join(f"[{label}]" for label in c['inputs'])
            
            # 构建滤镜部分
            filters = ",".join(c['filters'])
            
            # 构建输出标签部分（修正后的代码）
            output_label = f"[{c['output']}]" if c['output'] else ""
            
            filter_chain.append(f"{input_labels}{filters}{output_label}")
        return ";".join(filter_chain)

    def _execute(self, command: str) -> Dict:
        """执行FFmpeg命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            return {"status": "success", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            raise FFmpegError(
                code="EXECUTION_FAILED",
                message=f"执行失败: {e.output}",
                suggestion="检查输入文件和参数",
                level=ErrorLevel.CRITICAL
            ) from e

    def _format_error(self, error: FFmpegError) -> Dict:
        return {
            "status": "error",
            "code": error.code,
            "message": error.message,
            "suggestion": error.suggestion
        }