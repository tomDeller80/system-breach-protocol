import pygame as pg

class PhysicsEngine:

    def __init__(self, friction = 0.7, glitch = 1.0):
        # Keep the current physics tuning in one place so effects can modify it temporarily.
        self.glitch_factor = glitch
        self.global_friction = friction

        # Track the temporary glitch state independently from the base settings.
        self.glitch_active = False
        self.glitch_start_time = 0
        self.glitch_duration = 1000  # Glitch lasts for 1000 milliseconds (1 second)

    def activate_glitch(self):
        # Start the glitch timer when a hardened block breaks.
        self.glitch_active = True
        self.glitch_start_time =  pg.time.get_ticks()


    def update_environment(self, current_time):
        # Restore normal physics when the temporary effect expires.
        if self.glitch_active:
            if current_time - self.glitch_start_time > self.glitch_duration:
                self.glitch_active = False
                self.glitch_start_time = 0

        if self.glitch_active:
            # While glitched, movement is slower and the paddle follow is heavier.
            self.glitch_factor = 0.5
            self.global_friction = 0.35
        else:
            self.glitch_factor = 1.0
            self.global_friction = 0.75


    def handle_collisions(
            self, game, paddle, balls,
            bricks, all_sprites, modules,
            explosion, explosions, powerups, debris
    ):
        # Resolve every active ball against the paddle, bricks, and spawned modules.
        for ball in balls:
            if ball.rect.colliderect(paddle): ball.struck()

            # Handle ball-to-brick impacts and trigger the correct destruction path.
            hit_bricks = pg.sprite.spritecollide(ball, bricks, False)

            for brick in hit_bricks:

                brick.struck()

                if self.get_side_hit(ball, brick) == 'vertical':
                    ball.speed[1] = -ball.speed[1]
                else:
                    ball.speed[0] = -ball.speed[0]

                if brick.hits <= 0:
                   # Special blocks spawn effects, normal blocks disappear immediately.
                   if brick.type in ['powerup', 'volatile', 'hardened']:

                       if brick.type == 'powerup':

                           position = brick.rect.center
                           brick.kill()

                           exploding_brick = explosion(
                               game, 'powerup',
                               position
                           )
                           all_sprites.add(exploding_brick)
                           explosions.add(exploding_brick)

                       elif brick.type == 'volatile':

                           position = brick.rect.center


                           exploding_brick = explosion(
                               game, 'volatile',
                               position
                           )

                           all_sprites.add(exploding_brick)
                           explosions.add(exploding_brick)

                           self.detonate_volatile_block(game, brick, debris)
                           brick.kill()


                       elif brick.type == 'hardened':

                           position = brick.rect.center

                           exploding_brick = explosion(
                               game, 'hardened',
                               position
                           )
                           all_sprites.add(exploding_brick)
                           explosions.add(exploding_brick)

                           self.detonate_volatile_block(game, brick, debris, (200,200))
                           brick.kill()

                   else:
                      brick.kill()

        # Collectable modules are picked up by the paddle when they overlap.
        for module in modules:
            if module.state == 'spawn' and paddle.rect.colliderect(module.rect):
                if len(powerups) < 3:
                    module.play_sfx()
                    powerups.append(module.type)

                module.kill()


    def get_side_hit(self, ball, brick):
        # Compare the overlap depth on each axis to infer which surface was struck.
        overlap_x = min(ball.rect.right, brick.rect.right) - max(ball.rect.left, brick.rect.left)
        overlap_y = min(ball.rect.bottom, brick.rect.bottom) - max(ball.rect.top, brick.rect.top)

        if overlap_x < overlap_y:
            return "horizontal"
        else:
            return "vertical"



    def detonate_volatile_block(self, game, volatile_brick, debris, radius=(250,250)):
        # Build an area-of-effect rectangle around the destroyed special block.
        blast_radius = volatile_brick.rect.inflate(radius)

        struck_special_bricks = set()

        # Destroy surrounding normal blocks and queue secondary effects for special ones.
        for brick in list(game.bricks):

            # Prevent the same block from being processed twice in one blast.
            if brick == volatile_brick or brick in struck_special_bricks:
                continue

            if brick != volatile_brick and blast_radius.colliderect(brick.rect):

                if brick.type in ['powerup', 'volatile', 'hardened']:
                    struck_special_bricks.add(brick)
                else:
                    glowing_debris = debris(game, brick.rect, brick.image)
                    game.all_sprites.add(glowing_debris)
                    game.debris.add(glowing_debris)
                    brick.kill()
