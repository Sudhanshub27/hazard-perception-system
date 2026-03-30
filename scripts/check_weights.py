import os
import hashlib

def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

mw_path = 'model/weights/best.onnx'
rw_path = 'runs/bdd100k_yolo26/weights/best.onnx'

print(f'model/weights/best.onnx  : {os.path.getsize(mw_path):,} bytes  | md5: {md5(mw_path)}')
print(f'training run best.onnx   : {os.path.getsize(rw_path):,} bytes  | md5: {md5(rw_path)}')

# Also check the .pt files
pt_path = 'model/weights/best.pt'
rpt_path = 'runs/bdd100k_yolo26/weights/best.pt'
print(f'model/weights/best.pt    : {os.path.getsize(pt_path):,} bytes  | md5: {md5(pt_path)}')
print(f'training run best.pt     : {os.path.getsize(rpt_path):,} bytes  | md5: {md5(rpt_path)}')
