from core import Storage, PhysicsEngine
import utils.physics as Physics
import utils.maths as MathUtils
from random import choice
import pygame as pg


# Sprite definitions for the ball, paddle, bricks, effects, and falling modules.

class Paddle(pg.sprite.Sprite):

    def __init__(self, game):
        super().__init__()

        # game logic
        self.game = game

        # sprite parameters
        self.friction = 0.7
        self.vel_x = 0
        self.speed = 20
        self.is_buffered = False

        # game area
        self.screen = pg.display.get_surface()
        self.area = self.screen.get_rect()
        self.area_width, self.area_height = self.area.size

        # image
        self.original_image, self.rect = Storage.load_image(filename="assets/sprites/paddle_plasma.png")
        self.image = self.original_image.copy()

        # sprite size
        self.base_width = self.rect.width
        self.buffer_width = int(self.base_width * 1.5)
        self.current_width = self.base_width
        self.target_width = self.base_width

        # position
        self.rect.x = (self.area_width / 2) - (self.rect.width / 2)
        self.rect.y = 600

        # Time
        self.buffer_expiry_time = pg.time.get_ticks()


    def activate_buffer(self, time=10000):
        self.is_buffered = True
        self.game.audio_manager.play_sfx('activate')
        self.buffer_expiry_time = pg.time.get_ticks() + time
        self.target_width = self.buffer_width

    def deactivate_buffer(self):
        self.is_buffered = False
        self.target_width = self.base_width

    def update(self):

        if self.is_buffered:
            now = pg.time.get_ticks()
            if now > self.buffer_expiry_time:
                self.deactivate_buffer()

        if self.current_width != self.target_width:

            diff = self.target_width - self.current_width
            if abs(diff) < 5:
                self.current_width = self.target_width
            else:
                self.current_width += 5 if diff > 0 else -5

            new_height = self.original_image.get_height()
            self.image = pg.transform.scale(self.original_image, (int(self.current_width), new_height))

            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

        mouse_x, _ = pg.mouse.get_pos()
        target_x = mouse_x - (self.rect.width / 2)

        scaled_max_speed = self.speed * self.game.physics.glitch_factor

        self.rect.x, self.vel_x = Physics.calculate_smooth_follow(
            self.rect.x,
            target_x,
            self.vel_x,
            scaled_max_speed,
            self.game.physics.global_friction,
            speed_multiplier=self.game.physics.glitch_factor
        )

        if self.rect.left < self.game.active_area.left:
            self.rect.left = self.game.active_area.left
            self.vel_x = 0
        elif self.rect.right > self.game.active_area.right:
            self.rect.right = self.game.active_area.right
            self.vel_x = 0


    def reset(self):
        # position
        self.rect.x = (self.area_width / 2) - (self.rect.width / 2)
        self.rect.y = 600


class Ball(pg.sprite.Sprite):

    def __init__(self, game, paddle, is_additional=False):
        super().__init__()

        # sprite
        self.state = 'inactive'
        self.visible = True

        # core position
        self.x = 0.0
        self.y = 0.0

        # game logic
        self.game = game

        # associated sprites
        self.paddle = paddle

        # additional ball
        self.is_additional = is_additional

        # sprite speed
        self.speed = [6, 6]
        self.base_speed = 8.5
        self.is_speed_boost = False

        # game area
        self.screen = pg.display.get_surface()
        self.area = self.screen.get_rect()
        self.area_width, self.area_height = self.area.size

        # animation
        self.frames = self.generate_frames()
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 100
        self.index = 0

        # image / rect
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect()

        # position
        self.rect.x = (self.area_width / 2) - (self.rect.width / 2)
        self.rect.y = 560

        # Time
        self.boost_expiry_time = pg.time.get_ticks()


    def generate_frames(self):

        frames = []

        # ball frames
        for index in range(10):
            frame, _ = Storage.load_image(
                filename=f"assets/animation/ball/ball_f{(index + 1)}.png"
            )
            frames.append(frame)

        return frames


    def animate(self):
        # Cycle the idle ball animation while it waits on the paddle.
        now = pg.time.get_ticks()

        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.index += 1

            if self.index < len(self.frames):
                self.image = self.frames[self.index]
            else:
                self.index = 0;


    def play_sfx(self, title):
        self.game.audio_manager.play_sfx(f'{title}')


    def reset(self, hide=False):
        self.disable()
        self.base_speed = 8.5

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.rect.centerx = self.paddle.rect.centerx
        self.rect.bottom = self.paddle.rect.top

        if hide:
            self.visible = False
            self.index = 0
            self.image = self.frames[self.index]
        else:
            self.visible = True

    def enable(self):
        self.state = 'active'
        self.index = 5
        self.image = self.frames[self.index]

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.speed[0], self.speed[1] = MathUtils.calculate_redirected_velocity(
            current_vx=0, # x-speed
            current_vy=6, # y-speed
            influence_v=self.paddle.vel_x,
            influence_factor=0.6,
            max_vx=6,
            target_speed=self.base_speed
        )

    def disable(self):
        self.state = 'inactive'


    def activate_speed_boost(self, multiplier=1.5, time=10000):

        self.is_speed_boost = True
        self.base_speed *= multiplier

        self.boost_expiry_time = pg.time.get_ticks() + time

        self.speed[0], self.speed[1] = MathUtils.set_magnitude(
            self.speed[0],
            self.speed[1],
            self.base_speed
        )

    def deactivate_speed_boost(self):

        self.is_speed_boost = False
        self.base_speed = 8.5

        self.speed[0], self.speed[1] = MathUtils.set_magnitude(
            self.speed[0],
            self.speed[1],
            self.base_speed
        )

    def struck(self):

        self.play_sfx('hit-paddle')

        self.speed[0], self.speed[1] = MathUtils.calculate_redirected_velocity(
            current_vx=self.speed[0],
            current_vy=self.speed[1],
            influence_v=self.paddle.vel_x,
            influence_factor=0.6,
            max_vx=7,
            target_speed=self.base_speed
        )

        # prevent double collision
        self.rect.bottom = self.paddle.rect.top

    def update(self):
        # Keep the ball attached to the paddle until the player launches it.
        if self.state == 'inactive':
            self.rect.centerx = self.paddle.rect.centerx
            self.x = float(self.rect.x)
            self.y = float(self.rect.y)
            if self.visible:
                self.animate()
            return

        if self.is_speed_boost:
            now = pg.time.get_ticks()
            if now > self.boost_expiry_time:
                self.deactivate_speed_boost()

        # Move float values smoothly by the glitched step fraction
        self.x += self.speed[0] * self.game.physics.glitch_factor
        self.y += self.speed[1] * self.game.physics.glitch_factor

        # Sync the Pygame display Rect to the float positions
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Check for bounces BEFORE clamping or freezing the rect position
        new_vx, new_vy = Physics.calculate_bounce_speed(
            self, self.game.active_area, self.speed[0], self.speed[1])


        # If a bounce occurred, update the vector and re-sync the float tracking
        if new_vx != self.speed[0] or new_vy != self.speed[1]:
            self.speed[0], self.speed[1] = new_vx, new_vy

        if new_vx != self.speed[0] or new_vy != self.speed[1]:
            self.speed[0], self.speed[1] = new_vx, new_vy

            # Instantly reflect the position out of the boundary so it doesn't double-trigger
            if self.rect.left < self.game.active_area.left:
                self.rect.left = self.game.active_area.left
            elif self.rect.right > self.game.active_area.right:
                self.rect.right = self.game.active_area.right

            if self.rect.top < self.game.active_area.top:
                self.rect.top = self.game.active_area.top

            # Re-sync float values to the safely pushed rect position
            self.x = float(self.rect.x)
            self.y = float(self.rect.y)

        # Final fallback safety clamp
        self.rect.clamp_ip(self.game.active_area)

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # Check if ball hit the bottom of the screen
        if self.rect.bottom >= self.game.active_area.bottom:

            if self.is_additional:
                self.kill()

                # Make primary ball visible if no clones are left
                active_clones = [b for b in self.game.balls if b.is_additional and b.state == 'active']
                if not active_clones:
                    self.game.ball.visible = True

            else:
                active_balls = [b for b in self.game.balls if b.is_additional]
                if not active_balls:
                    self.play_sfx('denied')
                    self.game.lose_life()
                    self.reset(hide=False)
                else:
                    self.reset(hide=True)


class DataBlock(pg.sprite.Sprite):

    def __init__(self, game, type, position, hits, large_block):

        super().__init__()

        self.game = game
        self.type = type
        self.hits = hits
        self.current_hits = 0
        self.large_block = large_block

        # frames
        self.frames = []
        self.base_frame_rate = 60
        self.current_frame_rate = self.base_frame_rate
        self.index = 0

        # image / rect
        self.image, self.rect = Storage.load_image(filename=f"assets/sprites/{self.type}.png")

        # location
        self.rect.x = position[0]
        self.rect.y = position[1]

        self.generate_frames()
        self.last_update = pg.time.get_ticks()

    def generate_frames(self):
        # Preload the hit animation frames for special brick variants.
        if self.type == 'hardened':
            for i in range(1, 17):
                self.frames.append(
                    Storage.load_image(filename=f"assets/animation/{self.type}/{self.type}_h{i}.png")[0]
                )
        elif self.type == 'powerup':
            for i in range(1, 11):
                self.frames.append(
                    Storage.load_image(filename=f"assets/animation/{self.type}/{self.type}_h{i}.png")[0]
                )
        elif self.type == 'volatile':
            for i in range(1, 11):
                self.frames.append(
                    Storage.load_image(filename=f"assets/animation/{self.type}/{self.type}_h{i}.png")[0]
                )


    def struck(self):
        # Record the hit, play the audio cue, and award points on the final hit.
        self.game.audio_manager.play_sfx('hit-block')
        self.hits -= 1
        self.current_hits += 1

        if self.hits <= 0:
            points = self.game.scoreboard.points[self.type]
            self.game.update_score(points)

    def update(self):
        # Only animated blocks need per-frame hit-state updates.
        if self.type not in ['volatile', 'hardened', 'powerup']:
            return

        if self.current_hits > 0:

            # Speed up the damage animation as the block gets closer to breaking.
            expected_frame_rate = self.base_frame_rate - (20 * self.current_hits)

            if self.current_frame_rate < expected_frame_rate:
                self.current_frame_rate = expected_frame_rate

            now = pg.time.get_ticks()

            if now - self.last_update > self.current_frame_rate:
                self.last_update = now
                self.index += 1

                # Loop the effect animation until the block is removed.
                if self.index == (len(self.frames) - 1):
                    self.index = 0

                # Swap the visible frame for the current damage step.
                if len(self.frames) > 0:
                    self.image = self.frames[self.index]
                else:
                  print(self.type)






class Explosion(pg.sprite.Sprite):

    def __init__(self, game, type, center):

        super().__init__()

        # params
        self.game = game
        self.type = type
        self.center = center

        self.collectable = choice(['multi', 'speed', 'health', 'buffer'])

        # animation
        self.frames = self.generate_frames()
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 60
        self.index = 0

        # image / rect
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=self.center)

        # play explosion
        self.play_sfx()


    def generate_frames(self):
        # Load the full explosion or transformation animation for the brick type.
        frames = []

        if self.type == 'powerup':

            # explosion frames
            for index in range(28):
                frame, _ = Storage.load_image(
                    filename=f"assets/animation/powerup/{self.type}_e{(index + 1)}.png"
                )
                frames.append(frame)

            # stabilize frames
            for index in range(13):
                frame, _ = Storage.load_image(
                    filename=f"assets/animation/{self.collectable}/{self.collectable}_s{(index + 1)}.png"
                )
                frames.append(frame)

        elif self.type == 'volatile':
            for index in range(22):
                frame, _ = Storage.load_image(filename=f"assets/animation/volatile/volatile_e{(index + 1)}.png")
                frames.append(frame)

        elif self.type == 'hardened':
            for index in range(20):
                frame, _ = Storage.load_image(filename=f"assets/animation/hardened/hardened_e{(index + 1)}.png")
                frames.append(frame)


        return frames

    def play_sfx(self):
        # Match the sound effect to the kind of impact being shown.
        if self.type == 'volatile':
            self.game.audio_manager.play_sfx('explosion')
        elif self.type == 'hardened':
            self.game.audio_manager.play_sfx('plasma')
        else:
            self.game.audio_manager.play_sfx('explosion')

    def spawn_collectable(self):
        # Powerup blocks turn into falling collectables when their animation ends.
        powerup = PowerUp(self.game, self.collectable, center=self.center, state='spawn')
        self.game.all_sprites.add(powerup)
        self.game.modules.add(powerup)
        self.kill()

    def activate_glitch(self):
        # Hardened blocks end by triggering the temporary glitch effect.
        self.game.physics.activate_glitch()
        self.game.audio_manager.play_sfx('glitch')
        self.kill()

    def update(self):
        # Step through the explosion frames and resolve the follow-up action at the end.
        now = pg.time.get_ticks()

        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.index += 1

            if self.index < len(self.frames):
                self.image = self.frames[self.index]
            else:
                if self.type == 'powerup':
                    self.spawn_collectable()
                elif self.type == 'hardened':
                    self.activate_glitch()
                else:
                    self.kill()


class PowerUp(pg.sprite.Sprite):

    def __init__(self, game, type, center, state):

        super().__init__()

        self.game = game
        self.type = type
        self.center = center
        self.state = state

        # sprite parameters
        self.speed = [0, 5]

        # game area
        self.screen = pg.display.get_surface()

        # animation
        self.frames = self.generate_frames()
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 60
        self.index = 0

        # image / rect
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=self.center)

    def generate_frames(self):
        # Preload the falling animation for the collected module type.
        frames = []

        # falling frames
        for index in range(12):
            frame, _ = Storage.load_image(
                filename=f"assets/animation/{self.type}/{self.type}_p{(index + 1)}.png"
            )
            frames.append(frame)

        return frames

    def play_sfx(self):
        # Use a single pickup sound for every module type.
        self.game.audio_manager.play_sfx('powerup')

    def update(self):
        # Advance the animation and let the module fall until it leaves the playfield.
        now = pg.time.get_ticks()

        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.index += 1

            if self.index < len(self.frames):
                self.image = self.frames[self.index]
            else:
                self.index = 0;

        if self.rect.bottom > self.game.active_area.bottom:
            self.kill()
            return

        self.rect.y += self.speed[1]


class Debris(pg.sprite.Sprite):
    def __init__(self, game, rect, original_surface):
        super().__init__()
        # Debris is a tinted copy of the destroyed brick that fades out over time.
        self.game = game

        self.image = original_surface.copy().convert_alpha()
        self.rect = rect.copy()

        tint_surf = pg.Surface(self.image.get_size(), pg.SRCALPHA)
        tint_surf.fill((255, 0, 128, 220))  # Saturated electric magenta

        pg.draw.rect(tint_surf, (255, 255, 255, 255), tint_surf.get_rect(), 3)

        self.image.blit(tint_surf, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        # 3. Slow down the clock
        self.alpha = 255.0
        self.fade_speed = 2.5

    def update(self):
        # Fade the debris until it is no longer visible.
        self.alpha -= self.fade_speed

        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(int(self.alpha), pg.RLEACCEL)
