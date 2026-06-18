import math
import random
import pygame
from src.constants import WIDTH, HEIGHT, COLOR_WHITE, COLOR_BULLET

class WeaponProfile:
    def __init__(self, name, damage, radius, speed_mult, cost, desc, special_type="normal"):
        self.name = name
        self.damage = damage       
        self.radius = radius       
        self.speed_mult = speed_mult
        self.cost = cost
        self.desc = desc
        self.special_type = special_type  

CHARACTER_WEAPONS = {
    'Knight': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Missile Táctico", damage=46, radius=38, speed_mult=1.05, cost=35, desc="Misil perforador azul."),
        WeaponProfile("Double Shot", damage=25, radius=24, speed_mult=1.0, cost=65, desc="Lanza 2 misiles de impacto continuo.", special_type="double"),
        WeaponProfile("Shield Strike", damage=50, radius=32, speed_mult=1.18, cost=75, desc="Impacto cinético lineal rápido."),
        WeaponProfile("Holy Bomb", damage=68, radius=58, speed_mult=0.9, cost=130, desc="Explosión bendita masiva.")
    ],
    'Mage': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Fireball Plasma", damage=52, radius=52, speed_mult=0.95, cost=50, desc="Onda ígnea expansiva."),
        WeaponProfile("Thunder Strike", damage=55, radius=36, speed_mult=1.1, cost=80, desc="Rayo electromagnético vertical.", special_type="thunder"),
        WeaponProfile("Magic Arrow", damage=38, radius=20, speed_mult=1.45, cost=45, desc="Saeta de plasma veloz."),
        WeaponProfile("Meteor Inbound", damage=76, radius=65, speed_mult=0.85, cost=140, desc="Meteoro denso de alta destrucción.")
    ],
    'Dragon': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Poison Shot", damage=44, radius=34, speed_mult=1.1, cost=40, desc="Plasma ácido corrosivo."),
        WeaponProfile("Flame Breath", damage=48, radius=46, speed_mult=1.0, cost=55, desc="Fuego místico molecular."),
        WeaponProfile("Dragon Fang", damage=56, radius=38, speed_mult=1.22, cost=85, desc="Perforador colmillar pesado."),
        WeaponProfile("Earthquake", damage=62, radius=68, speed_mult=0.88, cost=120, desc="Onda sismológica destructora.")
    ],
    'Heavy': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Atomic Bomb", damage=92, radius=92, speed_mult=0.7, cost=200, desc="Ojiva de destrucción masiva."),
        WeaponProfile("Big Missile", damage=58, radius=48, speed_mult=0.92, cost=70, desc="Fragmentación pesada."),
        WeaponProfile("Machine Gun", damage=18, radius=20, speed_mult=1.28, cost=60, desc="Ráfaga continua de 3 disparos.", special_type="machinegun"),
        WeaponProfile("Bunker Buster", damage=48, radius=42, speed_mult=1.12, cost=90, desc="Taladra antes de estallar.", special_type="buster")
    ]
}

class Tank:
    def __init__(self, x, mobile_type, name):
        self.x = float(x)
        self.y = 0.0
        self.mobile_type = mobile_type
        self.name = name
        self.width = 42
        self.height = 24
        
        self.max_health = 135 if mobile_type == 'Heavy' else 100
        self.health = self.max_health
        self.shield = 0
        self.gold = 300
        self.next_damage_mult = 1.0
        
        self.base_angle = 0.0
        self.angle = 45.0 if x < WIDTH/2 else 135.0
        
        self.power = 0.0
        self.speed = 1.5 if mobile_type == 'Heavy' else (2.4 if mobile_type == 'Knight' else 2.0)
        self.wheel_rotation = 0.0
        self.recoil_offset = 0.0
        
        self.vy = 0.0
        self.is_moving = False
        self.last_anim_tick = 0
        self.anim_toggle = False  
        self.muzzle_flash_frames = 0
        
        if mobile_type == 'Knight': self.color = (41, 128, 185)
        elif mobile_type == 'Mage': self.color = (192, 41, 43)
        elif mobile_type == 'Dragon': self.color = (39, 174, 96)
        else: self.color = (211, 84, 0)

    def take_damage(self, amount):
        """Método núcleo desacoplado guiado por TDD para asegurar mitigación perimetral."""
        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
                amount = 0
            else:
                amount -= self.shield
                self.shield = 0
                
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def calculate_terrain_slope(self, terrain):
        ix = max(0, min(int(self.x), WIDTH - 1))
        if self.y < float(terrain.heights[ix]):
            return 0.0
            
        x_left = max(0, min(int(self.x - 14), WIDTH - 1))
        x_right = max(0, min(int(self.x + 14), WIDTH - 1))
        
        y_left = terrain.heights[x_left]
        y_right = terrain.heights[x_right]
        
        dx = x_right - x_left
        dy = y_right - y_left
        
        if dx == 0: return 0.0
        return max(-35.0, min(math.degrees(math.atan2(-dy, dx)), 35.0))

    def update_position(self, terrain):
        ix = max(0, min(int(self.x), WIDTH - 1))
        ground_y = float(terrain.heights[ix])
        
        if self.y < ground_y:
            self.vy += 0.38  
            self.y += self.vy
            if self.y >= ground_y:
                self.y = ground_y
                self.vy = 0.0
        else:
            self.y = ground_y
            self.vy = 0.0
            
        target_slope = self.calculate_terrain_slope(terrain)
        self.base_angle += (target_slope - self.base_angle) * 0.15

        if self.recoil_offset > 0: self.recoil_offset -= 0.6
        if self.muzzle_flash_frames > 0: self.muzzle_flash_frames -= 1

    def move(self, direction, terrain):
        self.x += direction * self.speed
        self.wheel_rotation += direction * 0.3
        self.is_moving = True
        
        now = pygame.time.get_ticks()
        if now - self.last_anim_tick > 120:
            self.anim_toggle = not self.anim_toggle
            self.last_anim_tick = now

        half_w = self.width / 2
        if self.x < half_w: self.x = half_w
        elif self.x > WIDTH - half_w: self.x = WIDTH - half_w
        self.update_position(terrain)

    def rotate_point_helper(self, cx, cy, px, py, angle_deg):
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        dx = px - cx
        dy = py - cy
        return (int(cx + dx * cos_a - dy * sin_a), int(cy + dx * sin_a + dy * cos_a))

    def draw(self, surface, is_active, asset_mgr):
        tx, ty = int(self.x), int(self.y)
        rad_recoil = math.radians(self.base_angle + self.angle)
        draw_x = tx - int(math.cos(rad_recoil) * self.recoil_offset)
        draw_y = ty + int(math.sin(rad_recoil) * self.recoil_offset)

        pivot_x, pivot_y = draw_x, draw_y - 12
        abs_angle = self.base_angle + self.angle
        abs_rad = math.radians(abs_angle)
        barrel_len = 24
        bx = pivot_x + math.cos(abs_rad) * barrel_len
        by = pivot_y - math.sin(abs_rad) * barrel_len

        if asset_mgr.use_sprites:
            orig_cannon = asset_mgr.sprites[self.mobile_type]['cannon']
            rotated_cannon = pygame.transform.rotate(orig_cannon, abs_angle)
            rot_rect = rotated_cannon.get_rect()
            rot_rect.center = (pivot_x + math.cos(abs_rad) * 12, pivot_y - math.sin(abs_rad) * 12)
            surface.blit(rotated_cannon, rot_rect.topleft)
        else:
            pygame.draw.line(surface, (236, 240, 241), (pivot_x, pivot_y), (int(bx), int(by)), 4)

        if asset_mgr.use_sprites:
            frame_sprite = asset_mgr.sprites[self.mobile_type]['idle'] if not self.is_moving else (asset_mgr.sprites[self.mobile_type]['move1'] if self.anim_toggle else asset_mgr.sprites[self.mobile_type]['move2'])
            rotated_body = pygame.transform.rotate(frame_sprite, self.base_angle)
            body_rect = rotated_body.get_rect(center=(draw_x, draw_y - 10))
            surface.blit(rotated_body, body_rect.topleft)
        else:
            cx, cy = draw_x, draw_y - 10
            p1 = self.rotate_point_helper(cx, cy, draw_x - 18, draw_y - 16, self.base_angle)
            p2 = self.rotate_point_helper(cx, cy, draw_x + 18, draw_y - 16, self.base_angle)
            p3 = self.rotate_point_helper(cx, cy, draw_x + 18, draw_y - 6, self.base_angle)
            p4 = self.rotate_point_helper(cx, cy, draw_x - 18, draw_y - 6, self.base_angle)
            pygame.draw.polygon(surface, self.color, [p1, p2, p3, p4])
            for wx in [-14, -5, 5, 14]:
                w_cx, w_cy = self.rotate_point_helper(cx, cy, draw_x + wx, draw_y - 4, self.base_angle)
                pygame.draw.circle(surface, (44, 62, 80), (w_cx, w_cy), 5)

        if self.muzzle_flash_frames > 0:
            if asset_mgr.use_sprites and asset_mgr.sprites['muzzle_flash']:
                rotated_mf = pygame.transform.rotate(asset_mgr.sprites['muzzle_flash'], abs_angle)
                surface.blit(rotated_mf, rotated_mf.get_rect(center=(int(bx), int(by))).topleft)
            else:
                pygame.draw.circle(surface, (254, 202, 87), (int(bx), int(by)), 9)

        bar_w, bx_pos, by_pos = 46, draw_x - 23, draw_y - 42
        pygame.draw.rect(surface, (50, 50, 50), (bx_pos, by_pos, bar_w, 5))
        pygame.draw.rect(surface, (46, 204, 113), (bx_pos, by_pos, int(bar_w * (self.health / self.max_health)), 5))
        if self.shield > 0:
            pygame.draw.rect(surface, (52, 152, 219), (bx_pos, by_pos + 6, int(bar_w * (self.shield / 50.0)), 3))

        font_tag = pygame.font.SysFont("Arial", 11, bold=True)
        txt_name = font_tag.render(self.name, True, COLOR_WHITE)
        surface.blit(txt_name, (draw_x - txt_name.get_width() // 2, by_pos - 15))

class Projectile:
    def __init__(self, x, y, angle, power, wind_x, weapon_profile, owner):
        self.x, self.y = float(x), float(y)
        self.profile, self.owner = weapon_profile, owner
        rad = math.radians(angle)
        velocity_scalar = power * 0.25 * weapon_profile.speed_mult
        self.vx = velocity_scalar * math.cos(rad)
        self.vy = -velocity_scalar * math.sin(rad)
        self.gravity, self.wind_factor, self.wind_x = 0.22, 0.045, wind_x

    def update(self):
        self.vx += self.wind_x * self.wind_factor
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        color = (235, 94, 40) if self.profile.special_type == "thunder" else COLOR_BULLET
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 6 if self.profile.radius > 60 else 3)

class Particle:
    def __init__(self, x, y, color, vx=None, vy=None):
        self.x, self.y = float(x), float(y)
        if vx is None:
            angle, speed = random.uniform(0, 2 * math.pi), random.uniform(2.0, 6.5)
            self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        else:
            self.vx, self.vy = vx, vy
        self.color, self.radius, self.alpha, self.decay = color, random.uniform(3, 6), 255, random.uniform(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.alpha -= self.decay

    def draw(self, surface):
        if self.alpha > 0 and self.radius > 0:
            ratio = max(0.0, min(1.0, self.alpha / 255.0))
            c = (int(self.color[0] * ratio), int(self.color[1] * ratio), int(self.color[2] * ratio))
            pygame.draw.circle(surface, c, (int(self.x), int(self.y)), int(self.radius))

class ExplosionAnimation:
    def __init__(self, x, y, max_radius):
        self.x, self.y, self.max_radius = float(x), float(y), float(max_radius)
        self.current_radius, self.duration_frames, self.current_frame, self.is_finished = 0.0, 40, 0, False

    def update(self):
        self.current_frame += 1
        self.current_radius = self.max_radius * (self.current_frame / self.duration_frames)
        if self.current_frame >= self.duration_frames: self.is_finished = True

    def draw(self, surface):
        ratio = self.current_frame / self.duration_frames
        if ratio >= 1.0: return
        if ratio < 0.25:
            r, g, b = 235 + 20 * (ratio/0.25), 94 + 126 * (ratio/0.25), 40 + 10 * (ratio/0.25)
        elif ratio < 0.65:
            f = (ratio - 0.25) / 0.40
            r, g, b = 255, 220 - 190 * f, 50 - 40 * f
        else:
            f = (ratio - 0.65) / 0.35
            r, g, b = 230 * (1.0 - f), 30 * (1.0 - f), 10 * (1.0 - f)
        if self.current_radius > 2:
            pygame.draw.circle(surface, (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b)))), (int(self.x), int(self.y)), int(self.current_radius))