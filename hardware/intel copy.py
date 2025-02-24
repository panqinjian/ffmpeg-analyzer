class IntelQSVAccelerator:  # 定义Intel QSV加速器类
    """
    Intel QSV加速器类，用于优化FFmpeg滤镜为Intel QSV实现。
    """
    SUPPORTED_FILTERS = {  # 支持的滤镜
        """
        支持的滤镜字典，键为滤镜名称，值为字典包含实现、参数和需要的参数。
        """
        'scale': {  # 缩放滤镜
            """
            缩放滤镜，用于改变视频尺寸。
            """
            'impl': 'scale_qsv',  # Intel QSV实现的缩放滤镜
            'params': ['w', 'h'],  # 参数：宽度和高度
            'requires': ['hwaccel', 'hwaccel_device']  # 需要的参数：硬件加速和硬件加速设备
        },
        'overlay': {  # 覆叠滤镜
            """
            覆叠滤镜，用于叠加两个视频流。
            """
            'impl': 'overlay_qsv',  # Intel QSV实现的覆盖滤镜
            'params': ['x', 'y'],  # 参数：x和y坐标
            'requires': ['main_hwctx', 'overlay_hwctx']  # 需要的参数：主硬件上下文和覆盖硬件上下文
        }
    }

    def __init__(self):  # 初始化方法
        """
        初始化方法，检查驱动和检测设备。
        """
        self._check_driver()  # 检查驱动
        self._devices = self._detect_devices()  # 检测设备

    def _check_driver(self):  # 检查驱动方法
        """
        检查Intel媒体驱动是否安装。
        """
        try:
            result = subprocess.run(
                ["vainfo"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if "iHD" not in result.stdout:
                raise FFmpegError(
                    code="INTEL_DRIVER_MISMATCH",
                    message="未检测到Intel iHD驱动",
                    suggestion="安装 intel-media-va-driver-non-free",
                    level=ErrorLevel.CRITICAL
                )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise FFmpegError(
                code="INTEL_DRIVER_MISSING",
                message="Intel媒体驱动不可用",
                suggestion="安装: sudo apt install intel-media-va-driver",
                level=ErrorLevel.CRITICAL
            ) from e

    def _detect_devices(self) -> list:  # 检测设备方法
        """
        检测可用QSV设备。
        """
        try:
            result = subprocess.run(
                ["ls /dev/dri/renderD*"],
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                text=True
            )
            return result.stdout.strip().split()
        except subprocess.CalledProcessError:
            return []

    def optimize_filter(self, filter_name: str, params: dict) -> str:  # 优化滤镜的方法
        """
        优化滤镜为QSV实现。
        :param filter_name: 原始滤镜名称
        :param params: 滤镜参数
        :return: 优化后的滤镜字符串或None
        """
        # 检查滤镜名称是否为支持的滤镜
        if filter_name == "scale":  # 如果滤镜名称为缩放
            return self._optimize_scale(params)  # 调用优化缩放的方法
        return None  # 如果不支持的滤镜，返回None

    def _optimize_scale(self, params: dict) -> str:  # 优化缩放滤镜的方法
        """
        优化缩放滤镜为QSV实现。
        :param params: 缩放滤镜参数
        :return: 优化后的缩放滤镜字符串
        """
        # 生成优化后的缩放滤镜字符串
        return f"qsv_scale=width={params['width']}:height={params['height']}"  # 返回优化后的缩放命令