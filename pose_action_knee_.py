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

knee_y_history = []


def process_frame(frame):
    # 推論を実行
    results = model(frame)

    annotated_frame = results[0].plot()

    # 姿勢分析結果のキーポイントを取得する
    # keypoints = results[0].keypoints.xy  # 座標
    # confs = results[0].keypoints.conf  # 信頼度

    # for keypoint in keypoints:
    # for idx, point in enumerate(keypoint):
    # x, y = int(point[0]), int(point[1])

    keypoints = results[0].keypoints.xy[0]  # 1人目のキーポイント
    confs = results[0].keypoints.conf[0]   # 1人目の信頼度

    left_knee_y = keypoints[13][1]
    knee_y_history.append(left_knee_y)
    print(knee_y_history)

    for idx, (point, score) in enumerate(zip(keypoints, confs)):
        x, y = int(point[0]), int(point[1])
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

    # 左手挙げ判定
    left_shoulder = keypoints[5]
    left_elbow = keypoints[7]
    left_wrist = keypoints[9]

    if left_wrist[1] < left_elbow[1] < left_shoulder[1]:
        left_raised = True

    # 右手挙げ判定
    right_shoulder = keypoints[6]
    right_elbow = keypoints[8]
    right_wrist = keypoints[10]

    if right_wrist[1] < right_elbow[1] < right_shoulder[1]:
        right_raised = True

    # 膝のY座標の履歴リストが10個を超えたら
    if len(knee_y_history) > 10:
        # 一番古いデータ（先頭の要素）を削除して、リストのサイズを保つ
        knee_y_history.pop(0)

    # 時間軸を基いて判定
    # 膝が上がった動作かどうかを判定するフラグ（初期状態はFalse）
    knee_raised_motion = False

    # 履歴データが2件以上あるかをチェック（なければ動作判定できない）
    if len(knee_y_history) >= 2:
        # 2フレーム前の膝のY座標と最新のY座標の差分を計算
        delta_y = knee_y_history[-2] - knee_y_history[-1]  # 前 - 今

        # 差分が20pxを超えていれば「膝が上がった」と判定
        if delta_y > 20:
            knee_raised_motion = True
            print("膝が上がった")

    '''
    if len(knee_y_history) >= 5:
        delta_fast = knee_y_history[-2] - knee_y_history[-1]
        delta_slow = knee_y_history[-5] - knee_y_history[-1]

    if delta_fast > 15 or delta_slow > 20:
        print("✅ 膝が上がった！")
    '''

    # 判定に応じた表示
    if left_raised and right_raised:
        cv2.putText(
            annotated_frame,
            "Both Hands Raised",
            (50, 150),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.5,
            color=(0, 128, 255),
            thickness=4,
            lineType=cv2.LINE_AA,
        )
    elif left_raised:
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
    elif knee_raised_motion:
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
