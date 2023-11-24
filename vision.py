import cv2 as cv
import numpy as np


class Vision:

    def check_collision(self, rect1, rect2):
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)


    def process1(self,squares):
        combined_squares = []
        for square in squares:
            # Assuming square is a tuple (x, y, w, h)
            x, y, w, h = square
            combined = False

            for i, existing_square in enumerate(combined_squares):
                if self.check_collision(square, existing_square):
                    # Combine squares
                    x = min(x, existing_square[0])
                    y = min(y, existing_square[1])
                    w = max(x + w, existing_square[0] + existing_square[2]) - x
                    h = max(y + h, existing_square[1] + existing_square[3]) - y

                    # Update the combined square in the list
                    combined_squares[i] = (x, y, w, h)
                    combined = True
                    break

            if not combined:
                combined_squares.append((x, y, w, h))

        # Add single squares that are not colliding within 32 pixels
        for square in squares:
            alone = True

            for existing_square in combined_squares:
                if self.check_collision(square, existing_square):
                    alone = False
                    break

            if alone:
                combined_squares.append(tuple(square))

        return combined_squares