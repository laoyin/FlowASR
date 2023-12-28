import audioop
import asyncio
import aiohttp
import uuid
import wave
import json
from collections import deque
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketState
from fastapi.websockets import WebSocketDisconnect
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

# WebSocket 连接对象的字典，用于存储每个连接的状态和参数
connections = {}

# 线程池用于处理音频帧的 VAD
executor = ThreadPoolExecutor(max_workers=10)

# 处理音频帧的 VAD
async def process_vad_frames_async(frames, connection, websocket):
    print(process_vad_frames_async)
    result = await asr_from_audio_stream(frames)
    #j_re = json.loads(result)
    print(result)
    await websocket.send_text(json.dumps({"code": 30005, "msg": result.get("zn_text")}))
    print("tmd", "开始asr啦 send end")


async def send_file_2_asr(filepath):
    print("send_file_2_asr")
    async with aiohttp.ClientSession() as session:
        url = "https://your whisper user"
        form_data = aiohttp.FormData()
        form_data.add_field('secret', 'your_asr_code')
        form_data.add_field('audio_file', open(filepath, 'rb'), filename=filepath)

        async with session.post(url,data=form_data) as response:
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])
            html = await response.text()
            print("Body:", html, "...")
            return html


def save_as_file(client_data):
    print("save_as_file")
    tmp_wav_name = "./audo_tmp/" +str(uuid.uuid1()) + ".wav"
    tmp_wave = wave.open(tmp_wav_name, "wb")
    tmp_wave.setnchannels(1)
    tmp_wave.setsampwidth(2)
    tmp_wave.setframerate(8000)
    tmp_wave.writeframes(client_data)
    tmp_wave.close()
    return tmp_wav_name

async def asr_from_audio_stream(audio_data):
    print("asr_from_audio_stream")
    audio_data = b"".join(audio_data)
    tmp_wav_name = save_as_file(audio_data)
    asr_text = await send_file_2_asr(tmp_wav_name)
    print(asr_text)
    asr_text = json.loads(asr_text)
    if asr_text:
        asr_text["file_name"] = tmp_wav_name
    return asr_text

# WebSocket 连接对象
class Connection:
    def __init__(self):
        # 定义 VAD 参数
        self.initial_energy_threshold = 1000
        self.pause_threshold = 0.5  # 静音持续时间阈值，单位为秒
        self.non_speaking_duration = 1.0  # 非语音缓冲区的最大持续时间，单位为秒

        # 初始化能量阈值和动态调整参数
        self.energy_threshold = self.initial_energy_threshold
        self.dynamic_energy_threshold = True
        self.dynamic_energy_adjustment_damping = 0.1
        self.dynamic_energy_ratio = 1.5

        self.start_asr = False
        self.asr_task = None
        # 音频帧队列
        self.frames_queue = deque()

# WebSocket 接收音频数据并进行 VAD 处理
@app.websocket("/audio")
async def audio(websocket: WebSocket):
    await websocket.accept()

    # 创建当前 WebSocket 连接对象
    connection = Connection()
    connections[websocket] = connection

    try:
        while websocket.client_state != WebSocketState.DISCONNECTED:
            data = await websocket.receive_bytes()

            # print("coming data", data)
            # 将接收到的二进制数据添加到帧队列中
            connection.frames_queue.append(data)

            if not connection.start_asr:
                # 在线程池中异步处理 VAD
                connection.asr_task = asyncio.create_task(process_vad(connection.frames_queue, connection, websocket))
                connection.start_asr = True
            await asyncio.sleep(0.002)

    except WebSocketDisconnect:
        # 当 WebSocket 连接断开时抛出异常
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket连接异常: {e}")

    finally:
        # 清理连接对象
        try:
            print("cancel task")
            task = connection.asr_task
            if task:
                print("awiat cancel", task)
                task.cancel()
        except Exception as e:
            print("cancel error")
            print(e)

        del connections[websocket]

# 异步处理 VAD
async def process_vad(frames_queue, connection, websocket):
    # 判断是否开始进行 VAD
    while True:
        await asyncio.sleep(0.02)
        if len(frames_queue) > 0:
            frame = frames_queue.popleft()
            rms = audioop.rms(frame, 2)  # 假设音频帧采样宽度为 2

            # 动态调整能量阈值
            if connection.dynamic_energy_threshold:
                damping = connection.dynamic_energy_adjustment_damping ** (len(frame) / 8000)  # 根据实际情况调整
                target_energy = rms * connection.dynamic_energy_ratio
                connection.energy_threshold = connection.energy_threshold * damping + target_energy * (1 - damping)

            # 判断是否开始说话
            if rms > connection.energy_threshold:
                # 检测到说话开始
                print("检测到说话开始")

                # 继续从帧队列中获取音频数据，直到达到静音持续时间阈值
                pause_count = 0
                speaking_frames = [frame]  # 存储说话期间的音频帧

                print(connection.pause_threshold * 8000 / len(frame))
                while pause_count < connection.pause_threshold * 8000 / len(frame):  # 8000 是音频采样率，根据实际情况调整
                    await asyncio.sleep(0.01)
                    if len(frames_queue) > 0:
                        frame = frames_queue.popleft()
                        print("开始计算")
                        # await websocket.send(json.dumps({"code": 30005, "msg": "开始计算"}))
                        rms = audioop.rms(frame, 2)
                        if connection.dynamic_energy_threshold:
                            damping = connection.dynamic_energy_adjustment_damping ** (len(frame) / 8000)  # 根据实际情况调整
                            target_energy = rms * connection.dynamic_energy_ratio
                            connection.energy_threshold = connection.energy_threshold * damping + target_energy * (1 - damping)

                        if rms > connection.energy_threshold:
                            # 重置静音计数器
                            print("重置静音计数器")
                            pause_count = 0
                        else:
                            pause_count += 1

                        speaking_frames.append(frame)

                print("tmd", "开始asr啦 send begin")
                #await websocket.send_text(json.dumps({"code": 30005, "msg": "开始处理啦"}))
                # 在线程池中异步处理音频帧的 VAD
                #await asyncio.get_event_loop().run_in_executor(executor, process_vad_frames_async, speaking_frames, connection, websocket)
                asyncio.create_task(process_vad_frames_async(speaking_frames, connection, websocket))
        else:
            await asyncio.sleep(0.01)



# 启动 FastAPI 应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
