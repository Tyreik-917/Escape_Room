import pygame
import time

class Player:
    def __init__(self, x, y, screen_width, screen_height, sprite_size=128, initial_scale=1.0):
        """
        Initialize the player object.
        - x,y: center world/screen position
        - screen_width/height: for movement boundaries
        - sprite_size: base size used for scaling frames initially
        - initial_scale: initial scale multiplier (1.0 = original)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # store logical sprite size (base size before scale)
        self.base_sprite_size = sprite_size
        self.current_scale = float(initial_scale)

        # Collision box for movement and interaction (size will be updated after frames are created)
        self.rect = pygame.Rect(0, 0, sprite_size, sprite_size)
        self.rect.center = (x, y)

        # Movement speed in pixels per frame
        self.speed = 5

        # ---------------------------
        # ANIMATION SETUP (load originals)
        # ---------------------------
        # Load original (unscaled) frames and keep them so we can rescale cleanly
        self._original_frames = [
            pygame.image.load("Main/idle.png").convert_alpha(),
            pygame.image.load("Main/walk_1.png").convert_alpha(),
            pygame.image.load("Main/walk_2.png").convert_alpha()
        ]

        # Create the active frames (scaled)
        self.frames = []
        self._rescale_frames(self.current_scale)

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
        try:
            self.footstep = pygame.mixer.Sound("Main/footstep.mp3")
            self.footstep.set_volume(0.3)
        except Exception:
            self.footstep = None

    # ---------------------------------------------------------
    # INTERNAL: rescale frames (used by constructor and resize)
    # ---------------------------------------------------------
    def _rescale_frames(self, scale):
        """
        Rescale original frames by given scale multiplier and update
        the current frames list and collision rect while preserving center.
        """
        # Keep center so we can restore after changing rect
        old_center = self.rect.center

        new_w = int(self.base_sprite_size * scale)
        new_h = int(self.base_sprite_size * scale)

        if new_w <= 0: new_w = 1
        if new_h <= 0: new_h = 1

        self.frames = [
            pygame.transform.scale(frame, (new_w, new_h))
            for frame in self._original_frames
        ]

        # Update rect to match new frame size, preserve center
        self.rect = self.frames[0].get_rect(center=old_center)

    # ---------------------------------------------------------
    # Public API: resize at runtime (Method 3)
    # ---------------------------------------------------------
    def resize(self, scale):
        """
        Resize the player's visible sprite and collision rect.
        - scale: float multiplier (e.g. 0.75 for 75% size)
        """
        if scale <= 0:
            raise ValueError("scale must be > 0")

        self.current_scale = float(scale)
        self._rescale_frames(self.current_scale)

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
        # ---------------------------
        top_limit = 200  # Custom camera/scene limit

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top < top_limit:
            self.rect.top = top_limit
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height

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
            if self.footstep and not pygame.mixer.get_busy():
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
                getattr(item, "is_active", True)
                and item.is_near(self.rect)
                and getattr(item, "interactable", True)
                and getattr(item, "reinteractable", True)
            ):
                # Some items only allow interaction under certain conditions
                if getattr(item, "can_interact_now", False):
                    item.interact()
                    self.last_interact = now
                    break

