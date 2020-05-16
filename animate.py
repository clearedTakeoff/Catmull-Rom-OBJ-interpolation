import math

# File formated as vertices followed by vt, followed by faces (repeating 3 times)
# vt and faces don't change so only extract them once to write in output file
static_parts = []


def read_obj(file, extract_statics=False):
    f = open(file)
    vertices = []
    current_vertices = []
    static = []
    for line in f:
        if line.startswith("v "):
            if len(static) > 0:
                static_parts.append(static)
                static = []
            current_vertices.append([float(i) for i in line.split(" ")[1:]])
        elif line.startswith("vt") or line.startswith("f") or line.startswith("g"):
            if len(current_vertices) > 0:
                vertices.append(current_vertices)
                current_vertices = []
            if extract_statics is True:
                static.append(line)
    if extract_statics is True:
        static_parts.append(static)
    f.close()
    return vertices


def catmull_rom(frame1, frame2, frame3, frame4, counter, steps=10):
    parts = []
    for i in range(len(frame1)):  # Number of groups
        parts.append([])
        for j in range(steps):  # Number of steps
            parts[i].append([])
    for group in range(len(frame1)):
        for i in range(len(frame1[group])):
            control_1 = frame1[group][i]
            control_2 = frame4[group][i]
            point_1 = frame2[group][i]
            point_2 = frame3[group][i]
            # Tangents
            t1x = (point_2[0] - control_1[0]) * 0.5
            t1y = (point_2[1] - control_1[1]) * 0.5
            t1z = (point_2[2] - control_1[2]) * 0.5

            t2x = (control_2[0] - point_1[0]) * 0.5
            t2y = (control_2[1] - point_1[1]) * 0.5
            t2z = (control_2[2] - point_1[2]) * 0.5

            for time in range(steps):
                t = time / steps
                t2 = t * t
                t3 = t2 * t
                f1 = 2 * t3 - 3 * t2 + 1
                f2 = -2 * t3 + 3 * t2
                f3 = t3 - 2 * t2 + t
                f4 = t3 - t2
                new_x = f1 * point_1[0] + f2 * point_2[0] + f3 * t1x + f4 * t2x
                new_y = f1 * point_1[1] + f2 * point_2[1] + f3 * t1y + f4 * t2y
                new_z = f1 * point_1[2] + f2 * point_2[2] + f3 * t1z + f4 * t2z
                parts[group][time].append((new_x, new_y, new_z))

    for t in range(steps):
        f = open("output/int_frame" + "%03d" % counter + ".obj", "w")
        counter += 1
        for group in range(len(parts)):
            for line in parts[group][t]:
                f.write("v " + str(line[0]) + " " + str(line[1]) + " " + str(line[2]) + "\n")
            for line in static_parts[group]:
                f.write(line)
        f.close()
    return counter


def read_input(file):
    f = open(file, "r")
    frames = []
    duration = []
    for line in f:
        parameters = line.split(" ")
        frames.append(parameters[0])  # Obj file name
        duration.append(int(parameters[1]))
    for i in range(len(duration) - 1):
        duration[i] = duration[i + 1] - duration[i]

    frames.insert(0, frames[-1])
    frames.append(frames[1])
    return frames, duration


def interpolate_sequence(frames, duration):
    global static_parts
    file_ind = 1
    FPS = 30
    for i in range(1, len(frames) - 2):
        frame1 = read_obj("input/" + frames[i - 1], True)  # Control "point"
        frame2 = read_obj("input/" + frames[i])  # From "point"
        frame3 = read_obj("input/" + frames[i + 1])  # To "point"
        frame4 = read_obj("input/" + frames[i + 2])  # Control "point" 2
        frames_no = math.ceil((FPS * duration[i - 1]) / 1000)
        file_ind = catmull_rom(frame1, frame2, frame3, frame4, file_ind, steps=frames_no)
        static_parts = []


if __name__ == "__main__":
    f, d = read_input("input/input_00.txt")
    # f, d = read_input("input/input_03.txt")
    # f, d = read_input("input/input_03.txt")
    # f, d = read_input("input/input_03.txt")
    interpolate_sequence(f, d)
    #frame1 = read_obj("input/frame_01.obj", True)
    #frame2 = read_obj("input/frame_02.obj")
    #frame3 = read_obj("input/frame_03.obj")
    #frame4 = read_obj("input/frame_04.obj")
    #print(frame1)
    #catmull_rom(frame1, frame2, frame3, frame4, 60)
