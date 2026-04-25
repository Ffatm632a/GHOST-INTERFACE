
import cv2

def start_capture():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("HATA: Webcam açılamadı!")
        return

    print("Webcam açıldı. Çıkmak için 'q' tuşuna bas.")

    while True:
        success, frame = cap.read()

        if not success:
            print("HATA: Kare okunamadı.")
            break

        frame = cv2.flip(frame, 1)
        cv2.imshow("Ghost Interface - Kamera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Webcam kapatıldı.")


if __name__ == "__main__":
    start_capture()