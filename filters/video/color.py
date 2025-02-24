class ColorBalance:  # 定义颜色平衡类，用于调整视频颜色的平衡
    # 定义参数范围，用于限制颜色平衡的参数值
    PARAM_RANGES = {  
        # 红色通道范围，取值范围为-1.0到1.0
        'rs': (-1.0, 1.0),  
        # 绿色通道范围，取值范围为-1.0到1.0
        'gs': (-1.0, 1.0),  
        # 蓝色通道范围，取值范围为-1.0到1.0
        'bs': (-1.0, 1.0)  
    }

    # 验证参数的方法，用于检查颜色平衡参数是否有效
    def validate(self, params: dict):  
        # 遍历参数，检查每个参数的值
        for param, value in params.items():  
            # 如果参数在定义的范围内
            if param in self.PARAM_RANGES:  
                try:
                    # 转换参数值为浮点数
                    val = float(value)  
                    # 检查值是否在范围内
                    if not (self.PARAM_RANGES[param][0] <= val <= self.PARAM_RANGES[param][1]):  
                        # 抛出值错误
                        raise ValueError  
                except (ValueError, TypeError):  # 捕获值错误或类型错误
                    # 抛出FFmpeg错误
                    raise FFmpegError(  
                        # 错误代码
                        code="COLOR_RANGE_ERR",  
                        # 错误信息
                        message=f"{param}参数值{value}超出允许范围",  
                        # 错误建议
                        suggestion=f"取值范围: {self.PARAM_RANGES[param]}",  
                        # 错误等级
                        level=ErrorLevel.CRITICAL  
                    )

    # 生成颜色平衡命令的方法
    def generate(self, params: dict) -> str:  
        # 将参数转换为字符串
        param_str = ":".join([f"{k}={v}" for k,v in params.items()])  
        # 返回颜色平衡命令
        return f"colorbalance={param_str}"  