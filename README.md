# FlowASR
FlowASR是一个实现实时语音转文本（ASR）功能的项目，利用VAD、WebSocket和Whisper服务，提供无缝的语音转文字转换。

## 功能特点
实时语音识别：通过将VAD、WebSocket和Whisper服务结合，实现实时的语音转文本功能。
高效准确：FlowASR利用最新的语音识别技术，提供高准确性的文本转录。
无缝集成：支持与其他应用程序和服务的无缝集成，方便快速部署和使用。
## 快速开始
环境要求
Python 3.7+
安装相关依赖：pip install -r requirements.txt
使用示例
配置WebSocket和Whisper服务的相关参数。
运行main.py文件启动FlowASR服务。
向服务发送音频流进行实时语音识别。
python

#### 示例代码

#### 配置WebSocket和Whisper服务参数
whisper_url = "https://whisper-service.com"

#### 启动FlowASR服务
pytho server.py



## 联系我们
如有任何疑问或建议，请通过项目的Issue页面与我们联系。或者 加q：2637332218





### 算法介绍
该算法的数学原理基于信号处理中的均方根（RMS）能量计算和动态调整公式。

均方根（RMS）能量计算：

均方根能量是一种测量信号能量级别的方法，它通过计算信号的均方根值来表示信号的能量。
对于音频信号而言，均方根能量计算通常涉及以下步骤：
将音频信号划分为短时窗口，例如每个窗口包含一定数量的音频采样。
对于每个窗口，计算其所有采样的平方和。
将该和除以窗口长度，并取平方根，得到均方根能量值。
动态调整公式：


该公式用于根据当前音频能量和先前的能量阈值来动态调整阈值。
公式中的 damping 是一个衰减因子，它根据音频帧的长度和调整阻尼系数 connection.dynamic_energy_adjustment_damping 的值进行计算。
target_energy 是根据当前音频帧的能量和动态能量比例 connection.dynamic_energy_ratio 计算得到的目标能量阈值。
动态调整公式根据当前阈值和目标能量阈值，以及衰减因子来更新阈值。在更新过程中，当前阈值经过衰减后与目标能量阈值的加权平均得到新的阈值。
通过使用均方根能量计算和动态调整公式，该算法可以根据实时音频的能量级别来动态调整阈值，以适应不同的音频输入情况。这样可以提高系统对于不同音频信号的适应性和鲁棒性。


该算法的数学原理基于信号处理中的均方根（RMS）能量计算和动态调整公式。

均方根（RMS）能量计算：

均方根能量是一种测量信号能量级别的方法，它通过计算信号的均方根值来表示信号的能量。
对于音频信号而言，均方根能量计算通常涉及以下步骤：
将音频信号划分为短时窗口，例如每个窗口包含一定数量的音频采样。
对于每个窗口，计算其所有采样的平方和。
将该和除以窗口长度，并取平方根，得到均方根能量值。
动态调整公式：

该公式用于根据当前音频能量和先前的能量阈值来动态调整阈值。
公式中的 damping 是一个衰减因子，它根据音频帧的长度和调整阻尼系数 connection.dynamic_energy_adjustment_damping 的值进行计算。
target_energy 是根据当前音频帧的能量和动态能量比例 connection.dynamic_energy_ratio 计算得到的目标能量阈值。
动态调整公式根据当前阈值和目标能量阈值，以及衰减因子来更新阈值。在更新过程中，当前阈值经过衰减后与目标能量阈值的加权平均得到新的阈值。
通过使用均方根能量计算和动态调整公式，该算法可以根据实时音频的能量级别来动态调整阈值，以适应不同的音频输入情况。这样可以提高系统对于不同音频信号的适应性和鲁棒性。


假设 frame 是一个长度为 100 的音频帧。
假设 rms 的初始值为 50。
假设 connection.dynamic_energy_threshold 为 True，表示启用了动态能量阈值。
假设 connection.dynamic_energy_adjustment_damping 的值为 0.9。
假设 connection.dynamic_energy_ratio 的值为 0.8。
假设 connection.energy_threshold 的初始值为 100。

现在我们将使用这些数值来解释算法的执行步骤：

从 frames_queue 中获取最早的音频帧 frame，假设为长度为 100 的音频帧。

使用 audioop.rms(frame, 2) 函数计算音频帧的均方根（RMS）能量。假设计算结果为 rms = 50。

由于 connection.dynamic_energy_threshold 为真，启用了动态能量阈值。

计算 damping，它是 connection.dynamic_energy_adjustment_damping 的值的 (len(frame) / 8000) 次方。假设 len(frame) = 100，则 damping = 0.9 ^ (100 / 8000)。 大概为 0.999

计算 target_energy，它是当前音频帧的 RMS 能量乘以 connection.dynamic_energy_ratio。假设 target_energy = rms * connection.dynamic_energy_ratio = 50 * 0.8 = 40。

根据动态调整公式，更新 connection.energy_threshold。公式为：
connection.energy_threshold = connection.energy_threshold * damping + target_energy * (1 - damping)` 假设 `connection.energy_threshold` 的初始值为 100，代入数值进行计算： 

connection.energy_threshold = connection.energy_threshold * damping + target_energy * (1 - damping)
                           = 100 * 0.999828 + 40 * (1 - 0.999828)
                           ≈ 99.9828 + 0.0712
                           ≈ 100.054



## 贡献
欢迎对FlowASR项目进行贡献！如果你发现了bug、有改进建议或想要添加新功能，请提交Issue或Pull Request。

## 许可证
该项目基于MIT许可证。请查阅LICENSE文件了解更多详情。