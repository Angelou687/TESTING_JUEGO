import pygame
import math
import random
import sys
import array
import os

from src.constants import *
from src.terrain import Terrain
from src.entities import Tank, Projectile, Particle, ExplosionAnimation, CHARACTER_WEAPONS

class AssetManager:
    def __init__(self):
        self.use_sprites = True
        self.sprites = {}
        self.load_all_assets()

    def safe_load(self, path, scale_dims=None):
        if not os.path.exists(path):
            self.use_sprites = False
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale_dims: img = pygame.transform.scale(img, scale_dims)
            return img
        except pygame.error:
            self.use_sprites = False
            return None

    def load_all_assets(self):
        mobiles = ['Knight', 'Mage', 'Dragon', 'Heavy']
        self.sprites['muzzle_flash'] = self.safe_load("assets/muzzle_flash.png", (20, 20))
        for mob in mobiles:
            m_lower = mob.lower()
            self.sprites[mob] = {
                'idle':   self.safe_load(f"assets/{m_lower}_idle.png", (42, 24)),
                'move1':  self.safe_load(f"assets/{m_lower}_move1.png", (42, 24)),
                'move2':  self.safe_load(f"assets/{m_lower}_move2.png", (42, 24)),
                'cannon': self.safe_load(f"assets/{m_lower}_cannon.png", (26, 8))
            }
            if not all(self.sprites[mob].values()): self.use_sprites = False

class SoundGenerator:
    @staticmethod
    def init_mixer():
        try: pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except Exception: pass

    @staticmethod
    def create_shoot_sound():
        sample_rate, duration = 22050, 0.12
        num_samples = int(duration * sample_rate)
        buf = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            t = i / sample_rate
            val = math.sin(2 * math.pi * (480.0 - (t / duration) * 300.0) * t)
            buf[i] = int(val * 11000 * (1.0 - t/duration))
        try: return pygame.mixer.Sound(buffer=buf)
        except Exception: return None

    @staticmethod
    def create_explosion_sound():
        sample_rate, duration = 22050, 0.35
        num_samples = int(duration * sample_rate)
        buf = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            buf[i] = int(random.uniform(-1.0, 1.0) * (1.0 - (i / sample_rate) / duration) ** 2.5 * 13000)
        try: return pygame.mixer.Sound(buffer=buf)
        except Exception: return None

class Game:
    STATE_MENU = 0
    STATE_CHARACTER_SELECT = 1
    STATE_PLAYING = 2
    STATE_GAME_OVER = 3

    SUBSTATE_AIMING = 0
    SUBSTATE_CHARGING = 1
    SUBSTATE_SHOP = 2
    SUBSTATE_FIRING = 3
    SUBSTATE_EXPLODING = 4

    def __init__(self):
        pygame.init()
        SoundGenerator.init_mixer()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption("Gunbound Core Ultimate V6 - QA Edition")
        self.clock = pygame.time.Clock()
        self.asset_mgr = AssetManager()
        self.is_paused = False  

        self.font_sm = pygame.font.SysFont("monospace", 14)
        self.font_main = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)

        self.snd_shoot = SoundGenerator.create_shoot_sound()
        self.snd_explosion = SoundGenerator.create_explosion_sound()
        self.state = Game.STATE_MENU
        self.mobiles_pool = ['Knight', 'Mage', 'Dragon', 'Heavy']
        self.p1_sel_idx, self.p2_sel_idx, self.selection_phase = 0, 1, 1 
        self.particles, self.projectiles_queue, self.current_explosion = [], [], None
        self.current_weapon_idx = {0: 0, 1: 0} 
        self.reset_game()

    def reset_game(self):
        self.terrain = Terrain(WIDTH, HEIGHT)
        self.particles.clear()
        self.projectiles_queue.clear()
        self.current_explosion = None
        p1_t = self.mobiles_pool[self.p1_sel_idx] if hasattr(self, 'p1_sel_idx') else 'Knight'
        p2_t = self.mobiles_pool[self.p2_sel_idx] if hasattr(self, 'p2_sel_idx') else 'Mage'
        self.player1, self.player2 = Tank(WIDTH * 0.18, p1_t, "Player 1"), Tank(WIDTH * 0.82, p2_t, "Player 2")
        self.player1.update_position(self.terrain)
        self.player2.update_position(self.terrain)
        self.tanks = [self.player1, self.player2]
        self.current_turn, self.substate, self.turn_timer = 0, Game.SUBSTATE_AIMING, 30.0
        self.randomize_wind()

    def randomize_wind(self): self.wind_x = random.uniform(-6.0, 6.0)
    def get_current_player(self): return self.tanks[self.current_turn]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.state == Game.STATE_MENU and event.key == pygame.K_SPACE:
                    self.state = Game.STATE_CHARACTER_SELECT
                    self.selection_phase = 1
                elif self.state == Game.STATE_CHARACTER_SELECT:
                    if self.selection_phase == 1:
                        if event.key == pygame.K_LEFT: self.p1_sel_idx = (self.p1_sel_idx - 1) % 4
                        elif event.key == pygame.K_RIGHT: self.p1_sel_idx = (self.p1_sel_idx + 1) % 4
                        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]: self.selection_phase = 2
                    elif self.selection_phase == 2:
                        if event.key == pygame.K_LEFT: self.p2_sel_idx = (self.p2_sel_idx - 1) % 4
                        elif event.key == pygame.K_RIGHT: self.p2_sel_idx = (self.p2_sel_idx + 1) % 4
                        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                            self.reset_game()
                            self.state = Game.STATE_PLAYING
                elif self.state == Game.STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.state = Game.STATE_CHARACTER_SELECT
                        self.selection_phase = 1
                    elif event.key == pygame.K_ESCAPE: self.state = Game.STATE_MENU
                elif self.state == Game.STATE_PLAYING:
                    if event.key == pygame.K_p:  
                        self.is_paused = not self.is_paused
                    if not self.is_paused:
                        if self.substate == Game.SUBSTATE_AIMING:
                            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                                idx = int(event.unicode) - 1
                                if 0 <= idx < 5: self.current_weapon_idx[self.current_turn] = idx
                            elif event.key == pygame.K_t: self.substate = Game.SUBSTATE_SHOP
                            elif event.key == pygame.K_SPACE:
                                self.substate = Game.SUBSTATE_CHARGING
                                self.get_current_player().power = 0.0
                            elif event.key == pygame.K_w: self.randomize_wind()
                        elif self.substate == Game.SUBSTATE_SHOP:
                            player = self.get_current_player()
                            if event.key in [pygame.K_t, pygame.K_ESCAPE]: self.substate = Game.SUBSTATE_AIMING
                            elif event.key == pygame.K_1 and player.gold >= 100:
                                player.gold -= 100
                                player.shield = min(50, player.shield + 25)
                            elif event.key == pygame.K_2 and player.gold >= 120:
                                player.gold -= 120
                                player.health = min(player.max_health, player.health + 30)
                            elif event.key == pygame.K_3 and player.gold >= 150:
                                player.gold -= 150
                                player.next_damage_mult = 1.5
            elif event.type == pygame.KEYUP:
                if self.state == Game.STATE_PLAYING and self.substate == Game.SUBSTATE_CHARGING and event.key == pygame.K_SPACE and not self.is_paused:
                    self.fire_weapon_sequence()

    def fire_weapon_sequence(self):
        player = self.get_current_player()
        w_profile = CHARACTER_WEAPONS[player.mobile_type][self.current_weapon_idx[self.current_turn]]
        if player.gold < w_profile.cost:
            self.substate = Game.SUBSTATE_AIMING
            return
        player.gold -= w_profile.cost
        abs_angle = player.base_angle + player.angle
        rad = math.radians(abs_angle)
        sx, sy = player.x + math.cos(rad) * 24, player.y - 12 - math.sin(rad) * 24
        player.recoil_offset, player.muzzle_flash_frames = 9.0, 6
        if self.snd_shoot: self.snd_shoot.play()

        if w_profile.special_type == "double":
            self.projectiles_queue.append(Projectile(sx, sy, abs_angle, player.power, self.wind_x, w_profile, player))
            self.projectiles_queue.append(Projectile(sx - math.cos(rad)*6, sy + math.sin(rad)*6, abs_angle, player.power * 0.92, self.wind_x, w_profile, player))
        elif w_profile.special_type == "machinegun":
            for i in range(3):
                self.projectiles_queue.append(Projectile(sx - math.cos(rad)*(i*5), sy + math.sin(rad)*(i*5), abs_angle, player.power * (1.0 - i*0.05), self.wind_x, w_profile, player))
        else:
            self.projectiles_queue.append(Projectile(sx, sy, abs_angle, player.power, self.wind_x, w_profile, player))
        self.substate = Game.SUBSTATE_FIRING

    def update_physics_and_logic(self):
        for p in self.particles[:]:
            p.update()
            if p.alpha <= 0: self.particles.remove(p)
            
        if self.state != Game.STATE_PLAYING or self.is_paused: return  

        for t in self.tanks: t.is_moving = False

        if self.substate == Game.SUBSTATE_AIMING:
            self.turn_timer -= 1.0 / FPS
            if self.turn_timer <= 0: self.end_turn_cycle()
            keys = pygame.key.get_pressed()
            p = self.get_current_player()
            if keys[pygame.K_LEFT]: p.move(-1, self.terrain)
            if keys[pygame.K_RIGHT]: p.move(1, self.terrain)
            if keys[pygame.K_UP]: p.angle = min(180.0, p.angle + 1.2)
            if keys[pygame.K_DOWN]: p.angle = max(0.0, p.angle - 1.2)
        elif self.substate == Game.SUBSTATE_CHARGING:
            p = self.get_current_player()
            p.power += 1.8
            if p.power >= 100.0:
                p.power = 100.0
                self.fire_weapon_sequence()
        elif self.substate == Game.SUBSTATE_FIRING:
            if not self.projectiles_queue:
                self.substate = Game.SUBSTATE_AIMING
                return
            proj = self.projectiles_queue[0]
            for _ in range(5):
                proj.vx += (proj.wind_x * proj.wind_factor) / 5
                proj.vy += proj.gravity / 5
                proj.x += proj.vx / 5
                proj.y += proj.vy / 5
                if proj.x < 0 or proj.x >= WIDTH or proj.y > HEIGHT + 80:
                    self.projectiles_queue.pop(0)
                    if not self.projectiles_queue: self.end_turn_cycle()
                    return
                if 0 <= int(proj.x) < WIDTH and proj.y >= self.terrain.heights[int(proj.x)]:
                    self.trigger_explosion(proj.x, proj.y, proj.profile, proj.owner)
                    return
                for target in self.tanks:
                    if math.hypot(proj.x - target.x, proj.y - (target.y - 10)) < 19.0:
                        self.trigger_explosion(proj.x, proj.y, proj.profile, proj.owner)
                        return
        elif self.substate == Game.SUBSTATE_EXPLODING:
            if self.current_explosion:
                self.current_explosion.update()
                if self.current_explosion.is_finished:
                    self.current_explosion = None
                    if self.projectiles_queue: self.projectiles_queue.pop(0)
                    self.substate = Game.SUBSTATE_FIRING if self.projectiles_queue else self.end_turn_cycle()

        for t in self.tanks:
            t.update_position(self.terrain)
            if t.y >= HEIGHT - 5: t.health = 0
        if self.player1.health <= 0 or self.player2.health <= 0:
            if self.player1.health <= 0 and self.player2.health <= 0: self.winner_name = "Empate Táctico"
            else: self.winner_name = self.player2.name if self.player1.health <= 0 else self.player1.name
            self.state = Game.STATE_GAME_OVER

    def trigger_explosion(self, x, y, profile, owner):
        if self.snd_explosion: self.snd_explosion.play()
        radius = profile.radius
        v_shift = 25 if profile.special_type == "buster" else 0
        owner.gold += self.terrain.destroy(x, y, radius, vertical_shift=v_shift)

        for target in self.tanks:
            distance = math.hypot(target.x - x, (target.y - 10) - (y + v_shift))
            if distance < radius:
                factor = 1.0 - (distance / radius)
                calculated_dmg = int(profile.damage * factor * owner.next_damage_mult)
                if calculated_dmg < 6 and factor > 0.0: calculated_dmg = 6
                
                target.take_damage(calculated_dmg)
                if target != owner and calculated_dmg > 0: owner.gold += int(calculated_dmg * 1.5)

        owner.next_damage_mult = 1.0
        for t in self.tanks: t.update_position(self.terrain)
        self.current_explosion = ExplosionAnimation(x, y + v_shift, radius)
        p_color = (120, 200, 255) if profile.special_type == "thunder" else (243, 156, 18)
        for _ in range(55 if radius > 60 else 26):
            ang, spd = random.uniform(0, 2 * math.pi), random.uniform(1.8, 6.0)
            self.particles.append(Particle(x, y + v_shift, p_color, math.cos(ang)*spd, math.sin(ang)*spd - 1.5))
        self.substate = Game.SUBSTATE_EXPLODING

    def end_turn_cycle(self):
        self.projectiles_queue.clear()
        self.current_explosion = None
        self.current_turn = (self.current_turn + 1) % 2
        self.turn_timer = 30.0
        self.randomize_wind()
        self.substate = Game.SUBSOUND_AIMING if hasattr(self, 'SUBSOUND_AIMING') else Game.SUBSTATE_AIMING

    def draw_aiming_radar(self, surface):
        player = self.get_current_player()
        abs_angle = player.base_angle + player.angle
        rad = math.radians(abs_angle)
        cx, cy = int(player.x), int(player.y - 12)
        dots_color = (46, 204, 113) if self.substate != Game.SUBSTATE_CHARGING else (int(46*(1-player.power/100.0)+231*(player.power/100.0)), int(204*(1-player.power/100.0)+76*(player.power/100.0)), int(113*(1-player.power/100.0)+60*(player.power/100.0)))
        pygame.draw.line(surface, (231, 76, 60), (int(cx + math.cos(rad) * 28), int(cy - math.sin(rad) * 28)), (int(cx + math.cos(rad) * 45), int(cy - math.sin(rad) * 45)), 3)
        for off in [-15, -7.5, 7.5, 15]:
            rad_off = math.radians(abs_angle + off)
            pygame.draw.circle(surface, dots_color, (int(cx + math.cos(rad_off) * 45), int(cy - math.sin(rad_off) * 45)), 2)

    def draw_beautiful_gradient(self):
        for y in range(0, HEIGHT, 4):
            lr = (y / HEIGHT) * 2.0 if (y / HEIGHT) < 0.5 else ((y / HEIGHT) - 0.5) * 2.0
            top_c, bot_c = (COLOR_SKY_TOP, COLOR_SKY_MID) if (y / HEIGHT) < 0.5 else (COLOR_SKY_MID, COLOR_SKY_BOTTOM)
            pygame.draw.rect(self.screen, (int(top_c[0]*(1-lr)+bot_c[0]*lr), int(top_c[1]*(1-lr)+bot_c[1]*lr), int(top_c[2]*(1-lr)+bot_c[2]*lr)), (0, y, WIDTH, 4))

    def draw_power_bar(self, surface):
        p = self.get_current_player()
        bx, by, bw, bh = WIDTH // 2 - 250, HEIGHT - 45, 500, 22
        pygame.draw.rect(surface, (30, 30, 30), (bx, by, bw, bh), border_radius=2)
        pygame.draw.rect(surface, (150, 150, 150), (bx, by, bw, bh), 2, border_radius=2)
        if p.power > 0:
            pygame.draw.rect(surface, (241, 196, 15) if p.power < 75 else (231, 76, 60), (bx + 2, by + 2, int(bw * (p.power / 100.0)) - 4, bh - 4))
        for i in range(1, 10): pygame.draw.line(surface, (100, 100, 100), (bx + int(bw * (i / 10.0)), by), (bx + int(bw * (i / 10.0)), by + bh - 1), 1)
        txt_p = self.font_sm.render(f"FORCE: {p.power:.1f}%", True, COLOR_WHITE)
        surface.blit(txt_p, (bx + bw // 2 - txt_p.get_width() // 2, by - 18))

    def draw_shop_overlay(self, surface):
        overlay = pygame.Surface((520, 300), pygame.SRCALPHA)
        overlay.fill((15, 15, 25, 235))
        pygame.draw.rect(overlay, COLOR_GOLD, (0, 0, 520, 300), 2, border_radius=4)
        overlay.blit(pygame.transform.scale(self.font_title.render("TIENDA TÁCTICA", True, COLOR_GOLD), (320, 32)), (100, 20))
        items = [("1. Escudo de Energía Absorbente (+25 SHIELD)", "100G"), ("2. Nano-Kit de Reparación Estructura (+30 HP)", "120G"), ("3. Módulo de Sobrecarga Atómica (Próximo shot x1.5)", "150G")]
        for i, (desc, cost) in enumerate(items):
            overlay.blit(self.font_main.render(desc, True, COLOR_WHITE), (30, 85 + i*45))
            overlay.blit(self.font_main.render(cost, True, COLOR_GOLD), (440, 85 + i*45))
        overlay.blit(self.font_sm.render("Presione [T] o [ESC] para salir del suministro comercial.", True, (170, 170, 170)), (30, 250))
        surface.blit(overlay, (WIDTH // 2 - 260, HEIGHT // 2 - 150))

    def render_character_select_screen(self):
        self.screen.blit(self.font_title.render("SELECCIÓN DE COMPAÑÍA MÓVIL", True, COLOR_GOLD), (WIDTH // 2 - 290, 40))
        phase_str = "JUGADOR 1: Seleccione su Unidad" if self.selection_phase == 1 else "JUGADOR 2: Seleccione su Unidad"
        self.screen.blit(self.font_main.render(phase_str, True, COLOR_WHITE), (WIDTH // 2 - 140, 110))
        map_names = {1: "Colinas Suaves", 2: "Montañas Altas", 3: "Valles Profundos", 4: "Ondas Regulares", 5: "Mesetas / Terrazas"}
        t_map = self.font_main.render(f"MAPA SELECCIONADO: {map_names[self.terrain.map_type].upper()}", True, (52, 152, 219))
        self.screen.blit(t_map, (WIDTH // 2 - t_map.get_width() // 2, HEIGHT - 150))

        card_w, card_h, start_x, y_pos = 190, 260, WIDTH // 2 - 425, 180
        for i, m_type in enumerate(self.mobiles_pool):
            cx = start_x + i * 220
            is_hov = (self.selection_phase == 1 and self.p1_sel_idx == i) or (self.selection_phase == 2 and self.p2_sel_idx == i)
            pygame.draw.rect(self.screen, (25, 35, 60) if is_hov else (15, 20, 35), (cx, y_pos, card_w, card_h), border_radius=6)
            pygame.draw.rect(self.screen, COLOR_GOLD if is_hov else (70, 85, 110), (cx, y_pos, card_w, card_h), 3, border_radius=6)
            
            if self.asset_mgr.use_sprites:
                spr = self.asset_mgr.sprites[m_type]['idle']
                rect_spr = spr.get_rect(center=(cx + card_w // 2, y_pos + 120))
                preview_x, preview_y = cx + card_w // 2, y_pos + 120
                self.screen.blit(spr, rect_spr.topleft)
            else:
                preview_x, preview_y = cx + card_w // 2, y_pos + 120
                if m_type == 'Knight': pygame.draw.rect(self.screen, (41, 128, 185), (preview_x - 20, preview_y - 10, 40, 12), border_radius=3)
                elif m_type == 'Mage': pygame.draw.circle(self.screen, (155, 89, 182), (preview_x, preview_y - 22), 6)
                elif m_type == 'Dragon': pygame.draw.rect(self.screen, (39, 174, 96), (preview_x - 18, preview_y - 10, 36, 11))
                elif m_type == 'Heavy': pygame.draw.rect(self.screen, (211, 84, 0), (preview_x - 18, preview_y - 15, 36, 11))

            self.screen.blit(self.font_main.render(m_type, True, COLOR_WHITE), (cx + card_w//2 - 30, y_pos + 20))
            self.screen.blit(self.font_sm.render("HP: 135 (Alto)" if m_type == 'Heavy' else "HP: 100 (Normal)", True, (160, 170, 190)), (cx + 25, y_pos + 210))
        self.screen.blit(self.font_sm.render("Use [FLECHAS] para navegar | [ENTER / ESPACIO] para confirmar unidad", True, COLOR_GOLD), (WIDTH // 2 - 260, HEIGHT - 90))

    def render(self):
        self.draw_beautiful_gradient()
        for p in self.particles: p.draw(self.screen)

        if self.state == Game.STATE_MENU:
            self.screen.blit(self.font_title.render("GUNBOUND: SLOPE ADAPTIVE", True, COLOR_GOLD), (WIDTH//2 - 280, HEIGHT//2 - 50))
            self.screen.blit(self.font_main.render("Presione [ESPACIO] para ingresar al hangar estratégico", True, COLOR_WHITE), (WIDTH//2 - 240, HEIGHT//2 + 25))
        elif self.state == Game.STATE_CHARACTER_SELECT:
            self.render_character_select_screen()
        elif self.state == Game.STATE_PLAYING:
            self.terrain.draw(self.screen) 
            self.player1.draw(self.screen, self.current_turn == 0, self.asset_mgr)
            self.player2.draw(self.screen, self.current_turn == 1, self.asset_mgr)
            if self.substate in [Game.SUBSTATE_AIMING, Game.SUBSTATE_CHARGING]: self.draw_aiming_radar(self.screen)
            if self.substate == Game.SUBSTATE_FIRING and self.projectiles_queue: self.projectiles_queue[0].draw(self.screen)
            if self.substate == Game.SUBSTATE_EXPLODING and self.current_explosion: self.current_explosion.draw(self.screen)

            panel = pygame.Surface((WIDTH, 65), pygame.SRCALPHA)
            panel.fill((16, 22, 33, 210))
            self.screen.blit(panel, (0, 0))
            cp = self.get_current_player()
            cw = CHARACTER_WEAPONS[cp.mobile_type][self.current_weapon_idx[self.current_turn]]
            self.screen.blit(self.font_main.render(f"TURNO: {cp.name} ({cp.mobile_type})", True, cp.color), (30, 10))
            self.screen.blit(self.font_main.render(f"VIENTO: {abs(self.wind_x):.2f} " + ("Derecha >>" if self.wind_x >= 0 else "<< Izquierda"), True, (52, 152, 219)), (30, 36))
            self.screen.blit(self.font_main.render(f"TIME: {max(0.0, self.turn_timer):.1f}s", True, COLOR_WHITE), (320, 20))
            self.screen.blit(self.font_main.render(f"ORO: {cp.gold}G", True, COLOR_GOLD), (490, 20))
            self.screen.blit(self.font_main.render(f"ARMA [{self.current_weapon_idx[self.current_turn]+1}]: {cw.name}", True, COLOR_BULLET), (655, 10))
            self.screen.blit(self.font_sm.render(f"{cw.desc}", True, (180, 185, 195)), (655, 38))
            self.draw_power_bar(self.screen)
            if self.substate == Game.SUBSTATE_SHOP: self.draw_shop_overlay(self.screen)

            if self.is_paused:  
                txt_p = self.font_title.render("SIMULACIÓN EN PAUSA", True, COLOR_GOLD)
                self.screen.blit(txt_p, (WIDTH // 2 - txt_p.get_width() // 2, HEIGHT // 2 - 30))
                txt_help = self.font_main.render("Presione [P] para reanudar el entorno", True, COLOR_WHITE)
                self.screen.blit(txt_help, (WIDTH // 2 - txt_help.get_width() // 2, HEIGHT // 2 + 30))
        elif self.state == Game.STATE_GAME_OVER:
            self.screen.blit(self.font_title.render("COMBATE FINALIZADO", True, COLOR_GOLD), (WIDTH//2 - 210, HEIGHT//3))
            self.screen.blit(self.font_main.render(f"Ganador de la ronda de simulación: {self.winner_name}", True, COLOR_WHITE), (WIDTH//2 - 180, HEIGHT//3 + 70))
            self.screen.blit(self.font_sm.render("Presione [R] para reiniciar al hangar de selección o [ESC] para el menú.", True, COLOR_WHITE), (WIDTH//2 - 270, HEIGHT//3 + 140))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update_physics_and_logic()
            self.render()
            self.clock.tick(FPS)