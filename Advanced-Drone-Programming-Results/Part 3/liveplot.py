# liveplot.py
from collections import deque
import numpy as np
import cv2

class LivePlot:
    def __init__(self, width=600, height=200, yLimit=(-100, 100), char="X"):
        self.w, self.h = int(width), int(height)
        self.ymin, self.ymax = float(yLimit[0]), float(yLimit[1])
        self.char = char
        self.data = deque(maxlen=self.w - 60)

    def update(self, value: float):
        """Append a value and return an image of the plot."""
        self.data.append(float(value))
        img = np.full((self.h, self.w, 3), 255, np.uint8)

        # plot area
        x0, y0, x1, y1 = 50, 20, self.w - 10, self.h - 20
        cv2.rectangle(img, (x0, y0), (x1, y1), (0, 0, 0), 2)

        # zero line
        if self.ymin < 0 < self.ymax:
            y_zero = int(np.interp(0, [self.ymin, self.ymax], [y1, y0]))
            cv2.line(img, (x0, y_zero), (x1, y_zero), (200, 200, 200), 1)

        # labels
        val = self.data[-1] if self.data else 0.0
        cv2.putText(img, f"{self.char}: {val:.1f}", (x0 + 10, y0 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(img, f"{self.ymax:.0f}", (10, y0 + 5),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 1)
        cv2.putText(img, f"{self.ymin:.0f}", (10, y1),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 1)

        # draw line
        if len(self.data) > 1:
            ys = np.interp(self.data, [self.ymin, self.ymax], [y1, y0]).astype(int)
            xs = np.arange(len(ys)) + x0
            pts = np.column_stack([xs, ys])
            for a, b in zip(pts[:-1], pts[1:]):
                cv2.line(img, tuple(a), tuple(b), (0, 0, 255), 1)

        return img
