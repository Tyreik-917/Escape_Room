import pygame
import time

# Screen dimensions (used for movement boundaries)
width, height = 1920, 1080
center_x, center_y = width // 2, height // 2


class Player:
    def __init__(self, x, y, sprite_size=128):
        """
        Initialize the player object:
        - Sets up position
        - Loads animations
        - Configures movement and interaction
        """
        # Collision box for movement and interaction
        self.rect = pygame.Rect(0, 0, sprite_size, sprite_size)
        self.rect.center = (x, y)

        # Movement speed in pixels per frame
        self.speed = 5

        # ---------------------------
        # ANIMATION SETUP
        # ---------------------------
        # Load idle and walking frames
        self.frames = [
            pygame.image.load("Main/idle.png"),
            pygame.image.load("Main/walk_1.png"),
            pygame.image.load("Main/walk_2.png")
        ]

        # Resize frames to match sprite size
        self.frames = [
            pygame.transform.scale(f, (sprite_size, sprite_size))
            for f in self.frames
        ]

        # Animation state tracking
        self.frame_index = 0
        self.animation_speed = 0.15  # How fast animation cycles
        self.moving = False           # True only when WASD pressed
        self.facing_right = True      # Flip horizontally when moving left

        # ---------------------------
        # INTERACTION SYSTEM
        # ---------------------------
        self.last_interact = 0          # Time last interaction occurred
        self.interact_cooldown = 0.5    # Prevent accidental spam E-presses

        # ---------------------------
        # FOOTSTEP SOUND
        # ---------------------------
        self.footstep = pygame.mixer.Sound("Main/footstep.mp3")
        self.footstep.set_volume(0.3)

    # ---------------------------------------------------------
    # HANDLE MOVEMENT INPUT (WASD)
    # ---------------------------------------------------------
    def handle_input(self, keys):
        """
        Moves the player based on WASD input.
        Returns the old rect for collision rollback.
        """
        old = self.rect.copy()
        self.moving = False

        # Move up
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.moving = True

        # Move down
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            self.moving = True

        # Move left
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.moving = True
            self.facing_right = False

        # Move right
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.moving = True
            self.facing_right = True

        # ---------------------------
        # MOVEMENT BOUNDARIES
        # Prevent player from leaving screen or going too far up
        # ---------------------------
        top_limit = 200  # Custom camera/scene limit

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.top < top_limit:
            self.rect.top = top_limit
        if self.rect.bottom > height:
            self.rect.bottom = height

        return old  # Used to revert if colliding with walls

    # ---------------------------------------------------------
    # ANIMATION UPDATE
    # ---------------------------------------------------------
    def animate(self):
        """
        Returns the correct animation frame based on movement.
        Also plays footstep sounds when walking.
        """
        # Walking animation cycle
        if self.moving:
            self.frame_index += self.animation_speed

            # Play footstep sound only when not already playing
            if not pygame.mixer.get_busy():
                self.footstep.play()

        else:
            # Reset to idle frame
            self.frame_index = 0

        # Loop animation
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        frame = self.frames[int(self.frame_index)]

        # Flip sprite horizontally when facing left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        return frame

    # ---------------------------------------------------------
    # INTERACTION WITH ITEMS (E KEY)
    # ---------------------------------------------------------
    def try_interact(self, items):
        """
        Attempts to interact with any nearby interactable item.
        - Checks cooldown
        - Checks distance
        - Checks if the item can currently be interacted with
        """
        now = time.time()

        # Prevent spamming E by using cooldown
        if now - self.last_interact < self.interact_cooldown:
            return

        # Loop through all interactable items in the level
        for item in items:
            if (
                item.is_active
                and item.is_near(self.rect)
                and item.interactable
                and item.reinteractable
            ):
                # Some items only allow interaction under certain conditions
                if getattr(item, "can_interact_now", False):
                    item.interact()
                    self.last_interact = now
                    break
