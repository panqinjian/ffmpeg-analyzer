# 项目结构及文件作用 ---这是一个使用deepseek r1生成并且调试的项目(Cascade Base也参与调试，由于穷，没有pro的调试，囧)

ffmpeg-analyzer/
├── core/
│   ├── __init__.py               # 核心模块初始化
│   ├── command_processor.py       # FFmpeg命令处理器，负责解析和执行FFmpeg命令
│   └── error_types.py             # 定义错误类型和错误等级
├── parsers/
│   ├── lexer/
│   │   ├── filter_lexer.py       # 词法分析器，用于解析滤镜链
│   │   └── global_lexer.py        # 全局词法分析器
│   ├── grammar/
│   │   ├── filter_grammar.lark    # 滤镜语法定义
│   │   └── command_grammar.lark    # FFmpeg命令语法定义
│   └── semantic_analyzer.py       # 语义分析器，负责验证FFmpeg命令的语义
├── filters/
│   ├── video/
│   │   ├── scaling.py             # 缩放滤镜类，处理视频缩放
│   │   └── color.py               # 颜色平衡滤镜类
│   ├── audio/
│   │   └── mixing.py              # 音频混合器类，处理音频流的混合
│   └── filter_registry.py          # 滤镜注册表，管理滤镜的规格和注册
├── hardware/
│   ├── __init__.py                # 硬件加速模块初始化
│   ├── nvidia.py                  # NVIDIA CUDA加速器类，处理CUDA相关的加速
│   └── intel.py                   # Intel QSV加速器类，处理Intel QSV相关的加速
├── ui/
│   ├── comfyui/
│   │   ├── __init__.py            # UI模块初始化
│   │   ├── nodes.py               # FFmpeg处理节点类，处理视频和音频流
│   │   └── widgets.py             # UI组件，提供GPU选项的配置
└── test/
    ├── unit/
    │   ├── test_hardware.py       # 硬件加速模块的单元测试
    │   ├── test_parser.py         # 解析器模块的单元测试
    └── integration/
        └── test_comfy_integration.py # ComfyUI集成的集成测试

# 使用说明
- 将以上内容复制到 README.md 文件中，以便其他开发者能够快速了解项目结构和各个文件的功能.
- 本项目基于Lark语法分析器进行开发.
- 项目结构基于Python的标准库.
- 项目使用了PyYAML作为配置文件格式.
- 项目使用了PyQt5作为UI框架.

关键功能说明
组件	功能亮点
widgets.py	提供图形化GPU参数配置界面，支持显存限制设置
nvidia.py	实现CUDA滤镜转换，自动检测NVIDIA驱动状态
intel.py	完整QSV加速支持，验证iHD驱动可用性
test_parser.py	覆盖词法分析和语义验证核心路径测试
test_comfy_integration	端到端集成测试，验证完整处理流程
