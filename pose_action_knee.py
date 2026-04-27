import cv2
from ultralytics import YOLO

# カメラ入力
video_path = 0
capture = cv2.VideoCapture(video_path)

# キーポイント名（17部位）
KEYPOINTS_NAMES = [
    "nose", "eye(L)", "eye(R)", "ear(L)", "ear(R)",
    "shoulder(L)", "shoulder(R)", "elbow(L)", "elbow(R)",
    "wrist(L)", "wrist(R)", "hip(L)", "hip(R)",
    "knee(L)", "knee(R)", "ankle(L)", "ankle(R)",
]

# YOLOv8 Poseモデルをロード
model = YOLO("yolov8n-pose.pt")

# 左膝のY座標履歴（時間軸用）
knee_y_history = []

# 関数
def process_frame(frame):
    global knee_y_history

    # YOLOv8 推論
    results = model(frame)
    annotated_frame = results[0].plot()

    # キーポイントが存在しない場合はスキップ
    if results[0].keypoints is None or len(results[0].keypoints.xy) == 0:
        print("⚠️ 人物が検出されませんでした")
        return annotated_frame

    keypoints = results[0].keypoints.xy[0]
    confs = results[0].keypoints.conf[0]

    # キーポイントの描画とログ表示
    for idx, (point, score) in enumerate(zip(keypoints, confs)):
        if score < 0.5:
            continue
        x, y = int(point[0]), int(point[1])
        cv2.rectangle(annotated_frame, (x, y), (x + 3, y + 3),
                      (255, 0, 255), cv2.FILLED)
        cv2.putText(annotated_frame, KEYPOINTS_NAMES[idx], (x + 5, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        print(
            f"Keypoint {KEYPOINTS_NAMES[idx]}: x={x}, y={y}, conf={score:.2f}")

    # 左膝のY座標の履歴に追加
    left_knee_y = keypoints[13][1]
    knee_y_history.append(left_knee_y)

    # 履歴は最大10フレームに制限
    if len(knee_y_history) > 10:
        knee_y_history.pop(0)

    # 時間軸に基づく「膝が上がる」動作の検出
    knee_raised_motion = False
    if len(knee_y_history) >= 5:
        delta_y = knee_y_history[-5] - knee_y_history[-1]  # 昔 - 今
        if delta_y > 20:  # Y座標が20px以上上がっていれば「膝を上げた」
            knee_raised_motion = True
            print("✅ 左膝が上がる動作を検出しました")

    # 結果表示
    if knee_raised_motion:
        cv2.putText(annotated_frame,
                    "Left Knee Raised (Motion)",
                    (50, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.3,
                    (255, 128, 0),
                    3,
                    cv2.LINE_AA)

    print("------------------------------------------------------")
    return annotated_frame


# メインループ
while capture.isOpened():
    success, frame = capture.read()
    if not success:
        break

    annotated_frame = process_frame(frame)
    cv2.imshow("YOLOv8 Human Pose Estimation", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

capture.release()
cv2.destroyAllWindows()
