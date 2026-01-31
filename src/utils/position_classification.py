
def point_in_polygon(point, polygon):
    """
    Ray casting algorithm
    point: (x, y)
    polygon: [(x1, y1), (x2, y2), ...]
    return: True nếu point nằm trong polygon
    """
    x, y = point
    inside = False
    n = len(polygon)

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        if ((y1 > y) != (y2 > y)):
            x_intersect = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1
            if x < x_intersect:
                inside = not inside

    return inside

def bbox_in_zone(bbox, polygon):
    """
    bbox: (x1, y1, x2, y2)
    polygon: list of (x, y)
    """
    x1, y1, x2, y2 = bbox

    # tâm bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    
    return point_in_polygon((cx, cy), polygon)

if __name__ == "__main__":
    # Ví dụ kiểm thử
    polygon = [(457.2777777777776,542.2222222222222), (617.2777777777776,1784.4444444444446), (1077.2777777777776,1713.3333333333335), 
               (1072.8333333333333,460.0), (761.722222222222,511.1111111111111)]
    bbox_inside = (723, 802, 956, 1002)
    bbox_outside = (250, 250, 300, 300)

    print(bbox_in_zone(bbox_inside, polygon))   # Kết quả mong đợi: True
    print(bbox_in_zone(bbox_outside, polygon))  # Kết quả mong đợi: False