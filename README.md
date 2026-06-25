# DeskPerson - 桌面AI伴侣项目

基于 [Mate-Engine](https://github.com/shinyflvre/Mate-Engine) 的桌面AI伴侣项目，支持VRM模型加载、GPT-SoVITS语音克隆、实时交互声音播放等功能。

## ⚖️ 许可证和版权声明

### 原项目许可证

本项目是基于 [Mate-Engine](https://github.com/shinyflvre/Mate-Engine) 的**衍生作品**。

**原项目采用混合许可证：**
- **GNU AGPL v3** (GNU通用公共许可证第3版，带额外条款)
- **MateProv2 License** (Mate系统专有二级许可证)

**使用本项目前，请仔细阅读并遵守上述两类许可证的完整条款。**

### 本项目的许可证

本项目作为Mate-Engine的衍生作品，遵循 **GNU AGPL v3** 许可证。

详见：[LICENSE](LICENSE) 文件。

### 版权声明

- **原项目 (Mate-Engine) 版权**：© shinyflvre
- **本项目版权**：© 2026 Qfish-417
- **默认Avatar版权**：默认内置角色的所有权利归 [Yorshka Shop](https://yorshkasencho.booth.pm/) 所有。**禁止在自行构建的分发包中重新分发该模型**。
- **内置AI模型版权**：集成的 `QWEN 2.5 1.5b LLM` 模型采用 `Apache License Version 2.0` 协议。

## ✨ 功能特性

- **VRM模型支持**: 支持加载和显示VRM格式的3D角色模型
- **语音克隆(TTS)**: 基于GPT-SoVITS和OmniVoice的高质量语音合成
- **实时交互**: 鼠标点击检测和游戏窗口状态监控
- **多音频播放**: Windows PlaySoundW API实现无窗口音频播放
- **监控集成**: 自动监控AI回复并生成语音

## 📁 项目结构

```
deskperson/
├── scripts/                    # Python脚本
│   ├── omnivoice_tts_server.py      # OmniVoice TTS服务器
│   ├── gpt_sovits_tts_server.py    # GPT-SoVITS TTS服务器
│   ├── interaction_sound_player_v6.py  # 交互声音播放器
│   └── tts_monitor_gpt_sovits.py   # TTS监控脚本
├── docs/                       # 文档
├── 一键启动.bat                # 一键启动脚本
├── start_omnivoice_tts_server.bat  # OmniVoice启动脚本
├── .gitignore                 # Git忽略文件
├── LICENSE                    # GNU AGPL v3 许可证
└── README.md                 # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- PyTorch (CUDA推荐)
- FastAPI
- sounddevice (可选，用于音频播放)
- Windows系统 (交互声音播放器需要)

### 安装依赖

```bash
pip install torch fastapi uvicorn soundfile numpy requests sounddevice
```

### 配置

1. **下载模型文件**
   - GPT-SoVITS模型: 从[官方仓库](https://github.com/RVC-Boss/GPT-SoVITS)下载
   - OmniVoice模型: 从[官方仓库](https://github.com/xxx)下载

2. **准备参考音频**
   - 将参考音频文件放在 `ref_audio/` 目录
   - 修改脚本中的 `REF_AUDIO_PATH` 和 `REF_TEXT`

3. **修改配置**
   - 编辑各脚本中的路径配置
   - 设置游戏窗口标题 `GAME_WINDOW_TITLE`

### 启动服务

#### 方式1: 一键启动 (Windows)

双击运行 `一键启动.bat`，会自动启动所有服务。

#### 方式2: 手动启动

1. **启动OmniVoice TTS服务器**:
   ```bash
   python scripts/omnivoice_tts_server.py
   ```

2. **启动GPT-SoVITS TTS服务器**:
   ```bash
   cd /d D:\voice\GPT-SoVITS-windows\GPT-SoVITS\
   python api_v2.py -c GPT_SoVITS/configs/tts_infer.yaml
   ```

3. **启动交互声音播放器**:
   ```bash
   python scripts/interaction_sound_player_v6.py
   ```

4. **启动TTS监控** (可选):
   ```bash
   python scripts/tts_monitor_gpt_sovits.py
   ```

## 📝 使用说明

### TTS服务器API

#### OmniVoice TTS服务器 (端口8083)

**请求**:
```bash
POST http://127.0.0.1:8083/tts
Content-Type: application/json

{
  "text": "你好，我是芙宁娜",
  "language": "zh",
  "speed": 1.0
}
```

**响应**: WAV音频数据

#### GPT-SoVITS TTS服务器 (端口9880)

**请求**:
```bash
GET http://127.0.0.1:9880/tts?text=你好&text_lang=zh&ref_audio_path=ref.mp3&prompt_text=参考文本
```

**响应**: WAV音频数据

### 交互声音播放器

- 自动检测游戏窗口(`MateEngineX`)是否在前台
- 检测鼠标点击并播放随机音频
- 使用Windows PlaySoundW API，无窗口弹出

## ⚠️ 使用规则和合规要求

### 必须遵守的规则

1. **模型使用要求**：
   - 仅可使用符合VRM 0.x/1.x规范的自定义模型
   - **禁止使用未授权的第三方版权模型**
   - 内置默认模型不得二次分发

2. **开发要求**：
   - 若分发修改后的版本，需遵守 **GNU AGPL v3** 的强制要求
   - 必须公开修改后的源代码
   - 必须保留原许可证声明
   - 不得移除原作者版权信息

3. **模特来源声明**：
   - 本项目使用的 **芙宁娜模型** 来源于：[aplaybox](https://www.aplaybox.com/details/model/Z5pE6HJacOlc)
   - 请遵守该模型的原创作者和使用条款

4. **商业使用**：
   - 商业分发需额外确认 `MateProv2 License` 的商业使用条款
   - 公益/个人非商业分发需保留完整许可证和版权声明

### 免责声明

- 本项目仅供学习研究使用
- 请遵守相关法律法规和模型许可证要求
- 使用第三方模型时，请确保已获得合法授权
- 因不当使用造成的任何问题，本项目不承担任何责任

## 🔧 配置参数

### interaction_sound_player_v6.py

```python
AUDIO_FILES = [
    r"D:\voice\game_tts_sample1.mp3",
    r"D:\voice\game_tts_sample2.mp3",
]
GAME_WINDOW_TITLE = "MateEngineX"
CLICK_COOLDOWN = 0.3  # 点击冷却时间(秒)
POLL_INTERVAL = 0.05    # 轮询间隔(秒)
```

### omnivoice_tts_server.py

```python
MODEL_DIR = r"D:\voice\omnivoice"
REF_AUDIO_PATH = r"path\to\ref_audio.mp3"
REF_TEXT = "参考音频的文本内容"
DEVICE = "cuda"  # 或 "cpu"
```

## 📦 模型文件

由于模型文件较大，请从以下渠道下载：

- **GPT-SoVITS**: [https://github.com/RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
- **OmniVoice**: [官方发布页](https://example.com) (请替换为实际链接)
- **芙宁娜VRM模型**: [aplaybox - 芙宁娜](https://www.aplaybox.com/details/model/Z5pE6HJacOlc)

下载后将模型文件放在以下目录：
```
D:/voice/models/           # GPT-SoVITS模型
D:/voice/omnivoice/       # OmniVoice模型
D:/Mate-Engine/           # VRM模型文件
```

## 🐛 常见问题

### 1. TTS服务器启动失败

- 检查模型路径是否正确
- 检查CUDA是否可用
- 查看日志输出

### 2. 交互声音播放器无响应

- 确认游戏窗口标题是否正确
- 检查音频文件是否存在
- 以管理员权限运行

### 3. 音频播放有延迟

- 调整 `CLICK_COOLDOWN` 参数
- 使用更快的TTS模型
- 启用GPU加速

## 📄 许可证

本项目采用 **GNU AGPL v3** 许可证。

详见：[LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Mate-Engine](https://github.com/shinyflvre/Mate-Engine) - 原项目 (© shinyflvre)
- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) - TTS引擎
- [OmniVoice](https://github.com/xxx) - TTS引擎
- [aplaybox - 芙宁娜模型](https://www.aplaybox.com/details/model/Z5pE6HJacOlc) - VRM模型来源

## 📧 联系方式

如有问题或建议，请提交Issue或联系：[your-email@example.com]

---

**注意**: 
- 本项目是 [Mate-Engine](https://github.com/shinyflvre/Mate-Engine) 的衍生作品
- 使用本项目前，请仔细阅读并遵守 **GNU AGPL v3** 和 **MateProv2 License**
- 请确保使用的所有模型均已获得合法授权
