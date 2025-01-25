from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # Or "yolov8s.pt" for better accuracy
model.train(data="config.yaml", epochs=100)
