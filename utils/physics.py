import utils.maths as maths


def calculate_smooth_follow(current_x, target_x, vel_x, speed, friction, speed_multiplier):
    # Smoothly pull the paddle toward the target while preserving inertia.
    diff = target_x - current_x

    if abs(diff) > 2:
        vel_x += diff * speed_multiplier

    if vel_x > speed: vel_x = speed
    if vel_x < -speed: vel_x = -speed

    vel_x = maths.apply_friction(vel_x, friction)

    return current_x + vel_x, vel_x


def calculate_bounce_speed(object, area, speed_x, speed_y):
    # Flip the velocity component that points into the boundary that was hit.
    if object.rect.left < area.left or object.rect.right > area.right:
        speed_x = -speed_x

    if object.rect.top < area.top or object.rect.bottom > area.bottom:
        speed_y = -speed_y

    return speed_x, speed_y
