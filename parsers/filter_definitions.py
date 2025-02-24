from enum import Enum

class FilterParamType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOL = "bool"
    EXPR = "expr"

# 定义支持的 FFmpeg 滤镜及其参数
FILTER_DEFINITIONS = {
    "scale": {
        "description": "缩放视频尺寸",
        "inputs": 1,
        "outputs": 1,
        "parameters": {
            "width": {"type": FilterParamType.EXPR, "required": True},
            "height": {"type": FilterParamType.EXPR, "required": True}
        }
    },
    "rotate": {
        "description": "旋转视频",
        "inputs": 1,
        "outputs": 1,
        "parameters": {
            "angle": {"type": FilterParamType.EXPR, "required": True}
        }
    },
    "format": {
        "description": "设置像素格式",
        "inputs": 1,
        "outputs": 1,
        "parameters": {
            "pix_fmts": {"type": FilterParamType.STRING, "required": True}
        }
    },
    "colorbalance": {
        "description": "调整颜色平衡",
        "inputs": 1,
        "outputs": 1,
        "parameters": {
            "rs": {"type": FilterParamType.NUMBER, "required": False},
            "gs": {"type": FilterParamType.NUMBER, "required": False},
            "bs": {"type": FilterParamType.NUMBER, "required": False}
        }
    },
    # 其他滤镜...
}
