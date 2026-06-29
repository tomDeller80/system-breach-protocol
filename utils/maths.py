import math

def apply_friction(velocity, friction_coef):
    return velocity * friction_coef


def calculate_redirected_velocity(current_vx, current_vy, influence_v, influence_factor, max_vx, target_speed):

    new_vx = current_vx + (influence_v * influence_factor)

    if abs(new_vx) > max_vx:
        new_vx = math.copysign(max_vx, new_vx)

    if abs(new_vx) < 0.5:
        new_vx = 1.5 if influence_v >= 0 else -1.5

    new_vy = -abs(current_vy)
    return set_magnitude(new_vx, new_vy, target_speed)


def set_magnitude(vx, vy, target_magnitude):

    current_magnitude = math.sqrt(vx ** 2 + vy ** 2)

    if current_magnitude == 0:
        return 0, 0

    ratio = target_magnitude / current_magnitude
    return vx * ratio, vy * ratio