from comfy.ui import widgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QSlider, QLabel

class GPUOptionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # CUDA启用选项
        self.cuda_checkbox = QCheckBox("启用NVIDIA CUDA加速")
        layout.addWidget(self.cuda_checkbox)
        
        # 显存限制滑块
        self.mem_label = QLabel("GPU显存限制 (MB):")
        layout.addWidget(self.mem_label)
        
        self.mem_slider = QSlider()
        self.mem_slider.setOrientation(1)  # 水平方向
        self.mem_slider.setRange(128, 16384)
        self.mem_slider.setValue(4096)
        layout.addWidget(self.mem_slider)
        
        # Intel QSV选项
        self.qsv_checkbox = QCheckBox("启用Intel QSV加速")
        layout.addWidget(self.qsv_checkbox)
        
        self.setLayout(layout)

    def get_options(self):
        return {
            "enable_cuda": self.cuda_checkbox.isChecked(),
            "gpu_mem_limit": self.mem_slider.value(),
            "enable_qsv": self.qsv_checkbox.isChecked()
        }