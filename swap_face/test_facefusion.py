import subprocess
import time
import psutil
import GPUtil

def get_gpu_usage():
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].load * 100  # GPU utilization percentage
        return None
    except:
        return None

def monitor_gpu(duration):
    start_time = time.time()
    max_usage = 0
    while time.time() - start_time < duration:
        usage = get_gpu_usage()
        if usage is not None:
            max_usage = max(max_usage, usage)
        time.sleep(0.1)  # Check every 0.1 seconds
    return max_usage

print('Running FaceFusion command...')
source_image = 'swap_face/test_media/elon.jpg'
target_image = 'swap_face/test_media/zuck.jpg'
target_video = 'swap_face/test_media/uploaded_video.mp4'
output_image = 'swap_face/test_media/output_image.jpg'
output_video = 'swap_face/test_media/output_video.mp4'

command = f'python swap_face/facefusion/run.py -s {source_image} -t {target_image} -o {output_image} --headless'

# Start GPU monitoring in a separate process
gpu_monitor = subprocess.Popen(['python', '-c', f"import time; from __main__ import monitor_gpu; print(monitor_gpu({60}))"], stdout=subprocess.PIPE)

start_time = time.time()
image_result = subprocess.run(f'bash -c "{command}"', shell=True, capture_output=True, text=True)
end_time = time.time()

# Wait for GPU monitoring to finish
gpu_usage, _ = gpu_monitor.communicate()

print(f'FaceFusion command completed in {end_time - start_time:.2f} seconds')
print(f'Subprocess stdout: {image_result.stdout}')
print(f'Subprocess stderr: {image_result.stderr}')
print(f'Max GPU Usage: {float(gpu_usage.strip()):.2f}%')

# CPU usage
cpu_percent = psutil.cpu_percent(interval=1)
print(f'CPU Usage: {cpu_percent}%')

# Memory usage
memory = psutil.virtual_memory()
print(f'Memory Usage: {memory.percent}%')

# Uncomment these lines if you want to run the video test as well
# video_command = command.replace(target_image, target_video).replace(output_image, output_video)
# video_result = subprocess.run(f'bash -c "{video_command}"', shell=True, capture_output=True, text=True)
# print(f'Video FaceFusion command completed in {video_result.returncode} seconds')
# print(f'Video Subprocess stdout: {video_result.stdout}')
# print(f'Video Subprocess stderr: {video_result.stderr}')