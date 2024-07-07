import subprocess

print('Running FaceFusion command...')
source_image = 'swap_face/data/tmp/image_data.png'
target_image = 'swap_face/data/tmp/uploaded_image.png'
target_video = 'swap_face/data/tmp/uploaded_video.mp4'
output_image = 'swap_face/data/tmp/output_image.png'
output_video = 'swap_face/data/tmp/output_video.mp4'
command = f'source .venv/bin/activate && python swap_face/facefusion/run.py -s {source_image} -t {target_image} -o {output_image} --headless'
image_result = subprocess.run(f'bash -c "{command}"', shell=True, capture_output=True, text=True)
print(f'FaceFusion command completed in {image_result.returncode} seconds')
print(f'Subprocess stdout: {image_result.stdout}')
print(f'Subprocess stderr: {image_result.stderr}')
video_result = subprocess.run(f'bash -c "{command.replace(target_image, target_video).replace(output_image, output_video)}"', shell=True, capture_output=True, text=True)
print(f'FaceFusion command completed in {video_result.returncode} seconds')
print(f'Subprocess stdout: {video_result.stdout}')
print(f'Subprocess stderr: {video_result.stderr}')
print('FaceFusion command completed')