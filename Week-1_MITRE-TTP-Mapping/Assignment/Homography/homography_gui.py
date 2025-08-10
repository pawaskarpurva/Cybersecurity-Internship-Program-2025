import cv2
import numpy as np
from tkinter import Tk, Label, Button, filedialog, messagebox
from PIL import Image, ImageTk

class HomographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Homography Detector (Cybersecurity)")
        self.root.geometry("400x250")
        self.trusted_path = ""
        self.suspect_path = ""

        Label(root, text="Homography Detection Tool").pack(pady=10)

        Button(root, text="Upload Trusted Image", command=self.load_trusted).pack(pady=5)
        Button(root, text="Upload Suspicious Image", command=self.load_suspect).pack(pady=5)
        Button(root, text="Detect Spoof", command=self.detect).pack(pady=20)

    def load_trusted(self):
        self.trusted_path = filedialog.askopenfilename()
        messagebox.showinfo("Trusted Image", f"Selected:\n{self.trusted_path}")

    def load_suspect(self):
        self.suspect_path = filedialog.askopenfilename()
        messagebox.showinfo("Suspicious Image", f"Selected:\n{self.suspect_path}")

    def detect(self):
        if not self.trusted_path or not self.suspect_path:
            messagebox.showerror("Error", "Please select both images.")
            return

        img1 = cv2.imread(self.trusted_path, 0)
        img2 = cv2.imread(self.suspect_path, 0)

        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) < 15:
            messagebox.showwarning("Result", "⚠️ Warning: Possible spoof detected!")
        else:
            messagebox.showinfo("Result", "✅ Trusted and suspicious images are visually similar.")

        match_img = cv2.drawMatches(img1, kp1, img2, kp2, matches[:20], None, flags=2)
        cv2.imshow("Matched Features", match_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Run GUI
if __name__ == "__main__":
    root = Tk()
    app = HomographyApp(root)
    root.mainloop()
