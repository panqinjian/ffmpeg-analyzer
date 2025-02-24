# main.py
from loader import init_plugins
import os

if __name__ == "__main__":
    os.environ['DEBUG_MODE'] = 'True'
    os.environ['DEBUG_path'] = 'D:\\AI\\Comfyui_Nvidia\\'
    init_plugins()
    from lexer.filter_lexer import FilterLexer
    # 验证模块是否加载成功
    
    lexer = FilterLexer(
            "ffmpeg.exe -y -hwaccel cuda -threads 16 "
            "-i D:\\AI\\Comfyui_Nvidia\\input\\video\\2.mp4 "
            "-i D:\\AI\\Comfyui_Nvidia\\input\\video\\b.mp4 "
            "-filter_complex "
            "[1:v]scale=iw*1.0:ih*1.0,rotate=0.0*PI/180, "
            "colorbalance=rs=0:gs=0:bs=0,gblur=sigma=0.0,eq=brightness=0.0:contrast=1.0,format=rgba, "
            "colorchannelmixer=aa=1.0[v2];"
            "[0:v]scale=iw/2:ih/2[base1]; "
            "[v2]scale=iw/2:ih/2[base2]; "
            "[base1][base2]hstack[outv];"
            "[1:a]volume=1.0[a1]; "
            "[0:a][a1]amix=inputs=2[aout]; "
            "-map [outv] -map [aout] "
            "-c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k "
            "D:\\AI\\Comfyui_Nvidia\\output\\AdvancedVideoMix_2_9.mp4"
        )
    tokens = lexer.tokenize()
    print(tokens)
