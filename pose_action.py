import cv2
from ultralytics import YOLO

video_path = 0
capture = cv2.VideoCapture(video_path)

KEYPOINTS_NAMES = [
    "nose",  # 0 鼻
    "eye(L)",  # 1 左目
    "eye(R)",  # 2 右目
    "ear(L)",  # 3 左耳
    "ear(R)",  # 4 右耳
    "shoulder(L)",  # 5 左肩
    "shoulder(R)",  # 6 右肩
    "elbow(L)",  # 7 左肘
    "elbow(R)",  # 8 右肘
    "wrist(L)",  # 9 左手首
    "wrist(R)",  # 10 右手首
    "hip(L)",  # 11 左腰
    "hip(R)",  # 12 右腰
    "knee(L)",  # 13 左膝
    "knee(R)",  # 14 右膝
    "ankle(L)",  # 15 左足首
    "ankle(R)",  # 16 右足首
]

# モデルの読み込み
model = YOLO("yolov8n-pose.pt")


def process_frame(frame):
    # 推論を実行
    results = model(frame)

    annotated_frame = results[0].plot()
    if results[0].keypoints is None or len(results[0].keypoints.xy) == 0:
        print("人物が検出されませんでした")
        return annotated_frame
    # 姿勢分析結果のキーポイントを取得する
    # keypoints = results[0].keypoints.xy  # 座標
    # confs = results[0].keypoints.conf  # 信頼度

    # for keypoint in keypoints:
    # for idx, point in enumerate(keypoint):
    # x, y = int(point[0]), int(point[1])
    
    # 姿勢分析結果のキーポイントを取得する
    keypoints = results[0].keypoints.xy[0]  # 1人目のキーポイント
    confs = results[0].keypoints.conf[0]   # 1人目の信頼度
    
    for idx, (point, score) in enumerate(zip(keypoints, confs)):
        x, y = int(point[0]), int(point[1])
        # score = confs[idx]
        if score < 0.5:
            continue

        print(
            f"Keypoint Name={KEYPOINTS_NAMES[idx]}, X={x}, Y={y}, Score={score:.4f}")

        # 紫の四角を描画
        cv2.rectangle(
            annotated_frame,
            (x, y),
            (x + 3, y + 3),
            (255, 0, 255),
            cv2.FILLED,
            cv2.LINE_AA,
        )

        # キーポイントの部位名称を描画
        cv2.putText(
            annotated_frame,
            KEYPOINTS_NAMES[idx],
            (x + 5, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 255),
            1,
            cv2.LINE_AA,
        )

        # 手挙げ判定フラグ
        left_raised = False
        right_raised = False

        # 左手を挙げる検出
        left_shoulder = keypoints[5]  # 左肩
        left_elbow = keypoints[7]  # 左肘
        left_wrist = keypoints[9]  # 左手首

        if left_wrist[1] < left_elbow[1] and left_elbow[1] < left_shoulder[1]:
            left_raised = True
        # 右手を挙げる検出
        right_shoulder = keypoints[6]
        right_elbow = keypoints[8]
        right_wrist = keypoints[10]

        if right_wrist[1] < right_elbow[1] < right_shoulder[1]:
            right_raised = True
            
        if left_raised:
            cv2.putText(
                annotated_frame,
                "Left Hand Raised",
                (50, 50),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.3,
                color=(0, 255, 0),
                thickness=3,
                lineType=cv2.LINE_AA,
            )
        elif right_raised:
            cv2.putText(
                annotated_frame,
                "Right Hand Raised",
                (50, 100),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.3,
                color=(0, 255, 255),
                thickness=3,
                lineType=cv2.LINE_AA,
            )

    print("------------------------------------------------------")
    return annotated_frame


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
