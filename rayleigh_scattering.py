import pygame, sys, math, random

pygame.init()
# Full screen mode and get dimensions.
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
clock = pygame.time.Clock()

# Define colors.
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
YELLOW     = (255, 255, 0)
RED        = (255, 0, 0)
BLUE       = (0, 0, 255)
LIGHT_BLUE = (0, 169, 211)
GREY       = (128, 128, 128)
BROWN      = (139, 69, 19)
DARK_BLUE  = (0, 0, 139)

# Set up a font for on-screen text.
font = pygame.font.SysFont("Arial", 24)

# Sun: Middle of left edge (offset by its radius)
sun_radius = 50
sun = (sun_radius, height // 2)

# Define the inner blue circle parameters (our "earth")
# Its center is at the center of the right two-thirds
blue_center = (2 * width // 3, height // 2)
blue_radius = 200

# Define the outer blue circle (design circle) with a larger radius
outer_blue_radius = int(blue_radius * 2)

# Atom parameters: 200 atoms (radius 10) randomly placed in the annulus between
# the inner blue circle and the outer blue circle
atom_radius = 10
atoms = []
while len(atoms) < 200:
    x = random.randint(blue_center[0] - outer_blue_radius, blue_center[0] + outer_blue_radius)
    y = random.randint(blue_center[1] - outer_blue_radius, blue_center[1] + outer_blue_radius)
    dist_sq = (x - blue_center[0])**2 + (y - blue_center[1])**2
    if dist_sq >= blue_radius**2 and dist_sq <= outer_blue_radius**2:
        atoms.append((x, y))

def clamp_endpoint(start, angle, length, max_x):
    """
    Compute endpoint from 'start' at 'angle' with given 'length',
    clamping it so that x does not exceed max_x.
    """
    end_x = start[0] + length * math.cos(angle)
    end_y = start[1] + length * math.sin(angle)
    if end_x > max_x and math.cos(angle) > 0:
        t = (max_x - start[0]) / math.cos(angle)
        if t < length:
            end_x = max_x
            end_y = start[1] + t * math.sin(angle)
    return (end_x, end_y)

# Maximum allowed generation for scattering.
MAX_GENERATION = 2

class RaySegment:
    def __init__(self, start, angle, color, scatter_allowed, speed, generation=0):
        self.start = start                  # Starting point (x, y)
        self.angle = angle                  # Direction (radians)
        self.color = color                  # Color of this segment
        self.scatter_allowed = scatter_allowed  # Can this segment spawn scatter?
        self.speed = speed                  # Speed (pixels per frame)
        self.length = 0                     # Current length of the segment
        self.collided = False               # Has it collided with an atom?
        self.terminated = False             # Should it stop extending?
        self.scatter_spawned = False        # Has scattering been spawned already?
        self.collision_point = None         # Collision point if collided
        self.generation = generation        # Generation number
        self.age = 0                        # Age (in frames) after termination
        self.hit_earth = False              # Set to True if it hits the inner blue circle

    def get_endpoint(self):
        """Return the current endpoint (clamped at the right edge)."""
        endpoint = (self.start[0] + self.length * math.cos(self.angle),
                    self.start[1] + self.length * math.sin(self.angle))
        if endpoint[0] > width:
            endpoint = clamp_endpoint(self.start, self.angle, self.length, width)
        return endpoint

    def update(self, atoms):
        if self.terminated:
            self.age += 1
            return

        # Increase length.
        new_length = self.length + self.speed
        new_endpoint = (self.start[0] + new_length * math.cos(self.angle),
                        self.start[1] + new_length * math.sin(self.angle))
        # Clamp at the right edge.
        if new_endpoint[0] > width:
            new_endpoint = clamp_endpoint(self.start, self.angle, new_length, width)
            new_length = math.hypot(new_endpoint[0] - self.start[0],
                                    new_endpoint[1] - self.start[1])
            self.terminated = True

        # Check intersection with the inner blue circle.
        dx = math.cos(self.angle)
        dy = math.sin(self.angle)
        ox, oy = self.start
        cx, cy = blue_center
        a = 1  # since dx^2 + dy^2 = 1
        b = 2 * (dx * (ox - cx) + dy * (oy - cy))
        c = (ox - cx)**2 + (oy - cy)**2 - blue_radius**2
        discriminant = b * b - 4 * a * c
        if discriminant >= 0:
            sqrt_disc = math.sqrt(discriminant)
            t_candidate = (-b - sqrt_disc) / 2
            if t_candidate <= self.length:
                t_candidate = (-b + sqrt_disc) / 2
            if t_candidate > self.length and t_candidate < new_length:
                new_length = t_candidate
                self.hit_earth = True
                self.terminated = True

        self.length = new_length

        # Check collision with atoms (only if scattering is allowed and not hit earth).
        if not self.terminated and (not self.collided) and self.scatter_allowed:
            for atom in atoms:
                dx_atom = new_endpoint[0] - atom[0]
                dy_atom = new_endpoint[1] - atom[1]
                if math.hypot(dx_atom, dy_atom) <= atom_radius:
                    self.collided = True
                    self.collision_point = atom
                    self.length = math.hypot(atom[0] - self.start[0], atom[1] - self.start[1])
                    self.terminated = True
                    break

    def draw(self, surface):
        endpoint = self.get_endpoint()
        pygame.draw.line(surface, self.color, self.start, endpoint, 2)

def spawn_scatter(segment):
    """
    Spawn new ray segments from the collision point of the given segment.
    - WHITE segments spawn one RED (non-scattering) and several BLUE segments.
    - BLUE segments spawn BLUE segments.
    - RED segments do not spawn further segments.
    Only spawn if generation is below MAX_GENERATION.
    Spawned segments start slightly offset to avoid immediate re-collision.
    """
    new_segments = []
    cp = segment.collision_point
    base_angle = segment.angle
    scatter_offsets = [-0.5, -0.35, -0.2, -0.05, 0.05, 0.2, 0.35, 0.5]
    offset_distance = 5  # Offset in pixels.

    if segment.generation >= MAX_GENERATION:
        return new_segments

    if segment.color == WHITE:
        new_start = (cp[0] + offset_distance * math.cos(base_angle),
                     cp[1] + offset_distance * math.sin(base_angle))
        new_segments.append(RaySegment(new_start, base_angle, RED, False, segment.speed, segment.generation + 1))
        for offset in scatter_offsets:
            angle = base_angle + offset
            new_start = (cp[0] + offset_distance * math.cos(angle),
                         cp[1] + offset_distance * math.sin(angle))
            new_segments.append(RaySegment(new_start, angle, BLUE, True, segment.speed, segment.generation + 1))
    elif segment.color == BLUE:
        for offset in scatter_offsets:
            angle = base_angle + offset
            new_start = (cp[0] + offset_distance * math.cos(angle),
                         cp[1] + offset_distance * math.sin(angle))
            new_segments.append(RaySegment(new_start, angle, BLUE, True, segment.speed, segment.generation + 1))
    return new_segments

# List to hold active ray segments.
active_segments = []
# Initially, create 30 white rays from the sun with random angles.
for _ in range(30):
    angle = random.uniform(-math.pi/8, math.pi/8)
    active_segments.append(RaySegment(sun, angle, WHITE, True, 5))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)

    # Draw the sun.
    pygame.draw.circle(screen, YELLOW, sun, sun_radius)

    # Draw the atoms.
    for atom in atoms:
        pygame.draw.circle(screen, GREY, atom, atom_radius)

    # Draw the inner blue circle (filled with light blue) that stops rays.
    pygame.draw.circle(screen, LIGHT_BLUE, blue_center, blue_radius, 0)

    # Draw eight dark blue radial lines to cut the inner circle into 8 equal segments,
    # and label each segment from a to h.
    labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for i in range(8):
        angle_boundary = i * (2 * math.pi / 8)
        end_x = blue_center[0] + blue_radius * math.cos(angle_boundary)
        end_y = blue_center[1] + blue_radius * math.sin(angle_boundary)
        pygame.draw.line(screen, DARK_BLUE, blue_center, (end_x, end_y), 2)
        # Label is placed at the midpoint of the wedge.
        mid_angle = angle_boundary + (math.pi / 8)
        label_radius = blue_radius * 0.5
        label_x = blue_center[0] + label_radius * math.cos(mid_angle)
        label_y = blue_center[1] + label_radius * math.sin(mid_angle)
        text_surface = font.render(labels[i], True, DARK_BLUE)
        text_rect = text_surface.get_rect(center=(label_x, label_y))
        screen.blit(text_surface, text_rect)

    # Draw the outer blue circle (design) with the larger radius.
    pygame.draw.circle(screen, BLUE, blue_center, outer_blue_radius, 4)

    # Draw the brown line along the right edge.
    pygame.draw.line(screen, BROWN, (width - 2, 0), (width - 2, height), 4)

    new_segments = []
    # Update and draw all active segments.
    for seg in active_segments:
        seg.update(atoms)
        seg.draw(screen)
        if seg.collided and (not seg.scatter_spawned) and seg.scatter_allowed:
            spawned = spawn_scatter(seg)
            new_segments.extend(spawned)
            seg.scatter_spawned = True

    active_segments.extend(new_segments)

    # Compute counts per wedge (for rays that hit the inner blue circle).
    # Each wedge covers an angular span of pi/4 (45°).
    wedge_counts = [{'white': 0, 'red': 0, 'blue': 0} for _ in range(8)]
    for seg in active_segments:
        if seg.hit_earth:
            ep = seg.get_endpoint()  # Endpoint on the inner blue circle.
            dx = ep[0] - blue_center[0]
            dy = ep[1] - blue_center[1]
            hit_angle = math.atan2(dy, dx)
            if hit_angle < 0:
                hit_angle += 2 * math.pi
            wedge_index = int(hit_angle // (math.pi / 4)) % 8
            if seg.color == WHITE:
                wedge_counts[wedge_index]['white'] += 1
            elif seg.color == RED:
                wedge_counts[wedge_index]['red'] += 1
            elif seg.color == BLUE:
                wedge_counts[wedge_index]['blue'] += 1

    # Display the counts for each wedge near the outer boundary of the inner circle.
    for i in range(8):
        mid_angle = i * (math.pi / 4) + (math.pi / 8)
        # Position the count text slightly outside the inner circle.
        count_radius = blue_radius + 30
        text_x = blue_center[0] + count_radius * math.cos(mid_angle)
        text_y = blue_center[1] + count_radius * math.sin(mid_angle)
        counts = wedge_counts[i]
        count_str = f"W:{counts['white']} R:{counts['red']} B:{counts['blue']}"
        count_surface = font.render(count_str, True, WHITE)
        count_rect = count_surface.get_rect(center=(text_x, text_y))
        screen.blit(count_surface, count_rect)

    pygame.display.flip()
    clock.tick(60)
