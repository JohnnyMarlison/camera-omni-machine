def my_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def math_block(x, y):
    vec_a = 320 - x 
    vec_b = 480 - y
    vec_a = my_map(vec_a, -320, 320, -255, 255)
    vec_b = my_map(vec_b, -240, 240, -255, 255)
    return '{} {}'.format(str(vec_a), str(vec_b))