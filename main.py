import cv2
from camera_handler import PlateDetection

def main():
    plate_detection = PlateDetection()
    cap = cv2.VideoCapture(0)

    print("Plaka tespiti başlatıldı. Çıkmak için 'q' tuşuna basın.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kare alınamadı, çıkılıyor.")
            break

        plates = plate_detection.process_frame(frame)
        for plate in plates:
            plate_detection.handle_plate(plate)

        cv2.imshow("Plaka Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
