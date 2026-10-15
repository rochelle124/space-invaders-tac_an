import pygame
import random
from entities.player import Player
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from database import register_player_and_score, check_login, register_user, update_player_username, get_leaderboard

class GameManager:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        # --- BOLD & BULKY FONTS ---
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 54, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.reload_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50)
        
        # --- GAME STATES & VARIABLES ---
        self.game_state = "login"
        self.active_input = "username"
        self.username = ""
        self.password = ""
        self.feedback_message = ""
        self.is_success_msg = False
        self.logged_in_user = None

        # Menu Settings / Options (2 ship choices)
        self.selected_ship = "STANDARD" 
        self.settings = {"music": True, "mobile_controls": True}
        self.leaderboard_data = []

        # --- BACKGROUND MUSIC SETUP ---
        try:
            pygame.mixer.music.load("assets/sounds/backgroundmusic.mp3")
            pygame.mixer.music.set_volume(0.8)
        except Exception:
            pass

        # Login/Register Input Boxes & Buttons
        box_w, box_h = 260, 40
        start_login_y = screen_height // 2 - 90
        
        self.login_user_box = pygame.Rect(screen_width // 2 - box_w // 2, start_login_y, box_w, box_h)
        self.login_pass_box = pygame.Rect(screen_width // 2 - box_w // 2, start_login_y + 80, box_w, box_h)
        self.login_button_rect = pygame.Rect(screen_width // 2 - box_w // 2, start_login_y + 145, box_w, box_h)
        self.register_button_rect = pygame.Rect(screen_width // 2 - box_w // 2, start_login_y + 195, box_w, box_h)

        # Menu Buttons Rectangles
        btn_w, btn_h = 280, 42
        menu_start_y = 135
        self.menu_name_box = pygame.Rect(screen_width // 2 - btn_w // 2, menu_start_y, btn_w, btn_h)
        self.menu_update_btn = pygame.Rect(screen_width // 2 - btn_w // 2, menu_start_y + 50, btn_w, btn_h)
        self.menu_ship_btn = pygame.Rect(screen_width // 2 - btn_w // 2, menu_start_y + 100, btn_w, btn_h)
        self.menu_play_btn = pygame.Rect(screen_width // 2 - btn_w // 2, menu_start_y + 150, btn_w, btn_h)
        self.menu_leaderboard_btn = pygame.Rect(screen_width // 2 - btn_w // 2, menu_start_y + 200, btn_w, btn_h)
        self.menu_settings_btn = pygame.Rect(screen_width // 2 - btn_w // 2, menu_start_y + 250, btn_w, btn_h)
        
        # Log Out Button: Lower Left
        self.menu_logout_btn = pygame.Rect(20, screen_height - 60, 140, 40)

        # Ship Selection Rectangles
        self.ship1_select_rect = pygame.Rect(screen_width // 2 - 200, screen_height // 2 - 60, 180, 180)
        self.ship2_select_rect = pygame.Rect(screen_width // 2 + 20, screen_height // 2 - 60, 180, 180)

        # Safely load preview images
        self.ship1_preview = None
        self.ship2_preview = None
        try:
            raw_s1 = pygame.image.load("assets/images/ship1.1.png").convert_alpha()
            self.ship1_preview = pygame.transform.scale(raw_s1, (90, 90))
        except Exception:
            pass

        try:
            raw_s2 = pygame.image.load("assets/images/ship2.2.png").convert_alpha()
            self.ship2_preview = pygame.transform.scale(raw_s2, (90, 90))
        except Exception:
            pass

        # Back Button
        self.back_button_rect = pygame.Rect(screen_width // 2 - 90, screen_height - 65, 180, 40)

        self.level = 1
        self.reset_game_variables(reset_level=True)

    def reset_game_variables(self, reset_level=False):
        if reset_level:
            self.level = 1
        ship_file = "assets/images/ship2.2.png" if self.selected_ship == "ADVANCED" else "assets/images/ship1.1.png"
        self.player = Player(self.screen_width, self.screen_height, ship_file)
        self.buttons = MobileButtons()
        self.bullets = []  # Changed to list to support rapid-fire bullets
        self.enemies = []
        self.score = 0
        self.spawn_number = 4 + self.level  # +1 enemy added per level
        self.score_saved = False  
        self.player_history = [] 
        self.timer = 0
        self.state_timer = 0
        self.spawn_enemies()

    def spawn_enemies(self):
        self.enemies = []
        # Check if current level is a multiple of 5 (Boss Level)
        if self.level % 5 == 0:
            boss = Enemy(0, 1, self.screen_width, is_boss=True)
            self.enemies.append(boss)
        else:
            # Cycle through enemy asset variants based on level
            variant = ((self.level - 1) % 3) + 1
            asset_path = f"assets/images/enemy{variant}.{variant}.png"
            for i in range(self.spawn_number):
                self.enemies.append(Enemy(i, self.spawn_number, self.screen_width, image_path=asset_path))
        self.timer = 0

    def handle_login_action(self):
        if not self.username.strip() or not self.password.strip():
            self.feedback_message = "Please fill in all fields!"
            self.is_success_msg = False
            return

        if check_login(self.username, self.password):
            self.logged_in_user = self.username
            self.game_state = "menu"
            self.feedback_message = ""
            if self.settings["music"]:
                try:
                    pygame.mixer.music.play(-1)
                except Exception:
                    pass
        else:
            self.feedback_message = "Invalid Credentials!"
            self.is_success_msg = False

    def handle_register_action(self):
        if not self.username.strip() or not self.password.strip():
            self.feedback_message = "Please fill in all fields!"
            self.is_success_msg = False
            return

        success, msg = register_user(self.username, self.password)
        self.feedback_message = msg
        self.is_success_msg = success

    def update(self, events):
        self.screen.fill((0, 0, 0))

        # ==================== 1. LOGIN STATE ====================
        if self.game_state == "login":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.login_user_box.collidepoint(event.pos):
                        self.active_input = "username"
                    elif self.login_pass_box.collidepoint(event.pos):
                        self.active_input = "password"
                    elif self.login_button_rect.collidepoint(event.pos):
                        self.handle_login_action()
                    elif self.register_button_rect.collidepoint(event.pos):
                        self.handle_register_action()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.active_input = "password" if self.active_input == "username" else "username"
                    elif event.key == pygame.K_BACKSPACE:
                        if self.active_input == "username":
                            self.username = self.username[:-1]
                        else:
                            self.password = self.password[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.handle_login_action()
                    else:
                        if len(event.unicode) > 0 and event.unicode.isprintable():
                            if self.active_input == "username" and len(self.username) < 18:
                                self.username += event.unicode
                            elif self.active_input == "password" and len(self.password) < 18:
                                self.password += event.unicode

            self.screen.fill((10, 15, 30))
            
            title_text = self.big_font.render("SPACE INVADERS", True, (255, 230, 0))
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 70))

            user_label = self.small_font.render("USERNAME:", True, (180, 200, 255))
            self.screen.blit(user_label, (self.login_user_box.x, self.login_user_box.y - 24))
            pygame.draw.rect(self.screen, (0, 255, 200) if self.active_input == "username" else (80, 100, 140), self.login_user_box, 2, border_radius=4)
            u_surf = self.font.render(self.username, True, (255, 255, 255))
            self.screen.blit(u_surf, (self.login_user_box.x + 10, self.login_user_box.y + (self.login_user_box.height // 2 - u_surf.get_height() // 2)))

            pass_label = self.small_font.render("PASSWORD:", True, (180, 200, 255))
            self.screen.blit(pass_label, (self.login_pass_box.x, self.login_pass_box.y - 24))
            pygame.draw.rect(self.screen, (0, 255, 200) if self.active_input == "password" else (80, 100, 140), self.login_pass_box, 2, border_radius=4)
            p_surf = self.font.render("*" * len(self.password), True, (255, 255, 255))
            self.screen.blit(p_surf, (self.login_pass_box.x + 10, self.login_pass_box.y + (self.login_pass_box.height // 2 - p_surf.get_height() // 2)))

            if self.feedback_message:
                msg_color = (100, 255, 100) if self.is_success_msg else (255, 90, 90)
                fb_surf = self.small_font.render(self.feedback_message, True, msg_color)
                self.screen.blit(fb_surf, (self.screen_width // 2 - fb_surf.get_width() // 2, self.login_pass_box.y + 44))

            pygame.draw.rect(self.screen, (0, 150, 70), self.login_button_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 255, 150), self.login_button_rect, 2, border_radius=4)
            l_text = self.font.render("LOGIN", True, (255, 255, 255))
            self.screen.blit(l_text, (self.login_button_rect.x + (self.login_button_rect.width // 2 - l_text.get_width() // 2),
                                     self.login_button_rect.y + (self.login_button_rect.height // 2 - l_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (30, 90, 180), self.register_button_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 180, 255), self.register_button_rect, 2, border_radius=4)
            r_text = self.font.render("CREATE ACCOUNT", True, (255, 255, 255))
            self.screen.blit(r_text, (self.register_button_rect.x + (self.register_button_rect.width // 2 - r_text.get_width() // 2),
                                     self.register_button_rect.y + (self.register_button_rect.height // 2 - r_text.get_height() // 2)))

        # ==================== 2. MENU / MISSION CONTROL STATE ====================
        elif self.game_state == "menu":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu_name_box.collidepoint(event.pos):
                        self.active_input = "menu_username"
                    elif self.menu_update_btn.collidepoint(event.pos):
                        if self.logged_in_user and self.logged_in_user.strip():
                            new_name = self.logged_in_user.strip()
                            success = update_player_username(self.username, new_name)
                            if success:
                                self.username = new_name
                                self.feedback_message = "Name updated!"
                            else:
                                self.feedback_message = "Update failed!"
                    elif self.menu_ship_btn.collidepoint(event.pos):
                        self.game_state = "ship_select"
                    elif self.menu_play_btn.collidepoint(event.pos):
                        self.reset_game_variables(reset_level=True)
                        self.game_state = "playing"
                    elif self.menu_leaderboard_btn.collidepoint(event.pos):
                        self.leaderboard_data = get_leaderboard(10)
                        self.game_state = "leaderboard"
                    elif self.menu_settings_btn.collidepoint(event.pos):
                        self.game_state = "settings"
                    elif self.menu_logout_btn.collidepoint(event.pos):
                        self.logged_in_user = None
                        self.password = ""
                        self.feedback_message = ""
                        try:
                            pygame.mixer.music.stop()
                        except Exception:
                            pass
                        self.game_state = "login"

                elif event.type == pygame.KEYDOWN:
                    if self.active_input == "menu_username":
                        if event.key == pygame.K_BACKSPACE:
                            if len(self.logged_in_user) > 0:
                                self.logged_in_user = self.logged_in_user[:-1]
                        elif event.key == pygame.K_RETURN:
                            pass
                        else:
                            if len(event.unicode) > 0 and event.unicode.isprintable() and len(self.logged_in_user) < 18:
                                self.logged_in_user += event.unicode

            self.screen.fill((10, 15, 30))
            
            title_text = self.big_font.render("SPACE INVADERS", True, (255, 230, 0))
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 35))

            call_label = self.small_font.render("PILOT CALLSIGN:", True, (180, 200, 255))
            self.screen.blit(call_label, (self.menu_name_box.x, self.menu_name_box.y - 20))
            pygame.draw.rect(self.screen, (0, 255, 200) if self.active_input == "menu_username" else (80, 100, 140), self.menu_name_box, 2, border_radius=4)
            name_surf = self.font.render(self.logged_in_user or "", True, (255, 255, 255))
            self.screen.blit(name_surf, (self.menu_name_box.x + 10, self.menu_name_box.y + (self.menu_name_box.height // 2 - name_surf.get_height() // 2)))

            pygame.draw.rect(self.screen, (50, 50, 150), self.menu_update_btn, border_radius=4)
            pygame.draw.rect(self.screen, (100, 100, 220), self.menu_update_btn, 2, border_radius=4)
            up_text = self.font.render("UPDATE NAME", True, (255, 255, 255))
            self.screen.blit(up_text, (self.menu_update_btn.x + (self.menu_update_btn.width // 2 - up_text.get_width() // 2),
                                      self.menu_update_btn.y + (self.menu_update_btn.height // 2 - up_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (180, 100, 30), self.menu_ship_btn, border_radius=4)
            pygame.draw.rect(self.screen, (230, 150, 80), self.menu_ship_btn, 2, border_radius=4)
            ship_text = self.font.render(f"SHIP: {self.selected_ship}", True, (255, 255, 255))
            self.screen.blit(ship_text, (self.menu_ship_btn.x + (self.menu_ship_btn.width // 2 - ship_text.get_width() // 2),
                                        self.menu_ship_btn.y + (self.menu_ship_btn.height // 2 - ship_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (0, 160, 60), self.menu_play_btn, border_radius=4)
            pygame.draw.rect(self.screen, (100, 255, 150), self.menu_play_btn, 2, border_radius=4)
            play_text = self.font.render("PLAY GAME", True, (255, 255, 255))
            self.screen.blit(play_text, (self.menu_play_btn.x + (self.menu_play_btn.width // 2 - play_text.get_width() // 2),
                                        self.menu_play_btn.y + (self.menu_play_btn.height // 2 - play_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (30, 90, 180), self.menu_leaderboard_btn, border_radius=4)
            pygame.draw.rect(self.screen, (100, 180, 255), self.menu_leaderboard_btn, 2, border_radius=4)
            lb_text = self.font.render("LEADERBOARD", True, (255, 255, 255))
            self.screen.blit(lb_text, (self.menu_leaderboard_btn.x + (self.menu_leaderboard_btn.width // 2 - lb_text.get_width() // 2),
                                      self.menu_leaderboard_btn.y + (self.menu_leaderboard_btn.height // 2 - lb_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (100, 50, 150), self.menu_settings_btn, border_radius=4)
            pygame.draw.rect(self.screen, (180, 100, 230), self.menu_settings_btn, 2, border_radius=4)
            set_text = self.font.render("SETTINGS", True, (255, 255, 255))
            self.screen.blit(set_text, (self.menu_settings_btn.x + (self.menu_settings_btn.width // 2 - set_text.get_width() // 2),
                                       self.menu_settings_btn.y + (self.menu_settings_btn.height // 2 - set_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (180, 50, 50), self.menu_logout_btn, border_radius=4)
            pygame.draw.rect(self.screen, (250, 100, 100), self.menu_logout_btn, 2, border_radius=4)
            lo_text = self.small_font.render("LOG OUT", True, (255, 255, 255))
            self.screen.blit(lo_text, (self.menu_logout_btn.x + (self.menu_logout_btn.width // 2 - lo_text.get_width() // 2),
                                      self.menu_logout_btn.y + (self.menu_logout_btn.height // 2 - lo_text.get_height() // 2)))

        # ==================== 3. SHIP SELECTION STATE ====================
        elif self.game_state == "ship_select":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.ship1_select_rect.collidepoint(event.pos):
                        self.selected_ship = "STANDARD"
                        self.game_state = "menu"
                    elif self.ship2_select_rect.collidepoint(event.pos):
                        self.selected_ship = "ADVANCED"
                        self.game_state = "menu"
                    elif self.back_button_rect.collidepoint(event.pos):
                        self.game_state = "menu"

            self.screen.fill((10, 15, 30))
            st_title = self.big_font.render("CHOOSE YOUR SHIP", True, (255, 230, 0))
            self.screen.blit(st_title, (self.screen_width // 2 - st_title.get_width() // 2, 40))

            is_s1 = self.selected_ship == "STANDARD"
            s1_border = (0, 255, 200) if is_s1 else (80, 100, 140)
            pygame.draw.rect(self.screen, (20, 30, 60), self.ship1_select_rect, border_radius=8)
            pygame.draw.rect(self.screen, s1_border, self.ship1_select_rect, 3, border_radius=8)
            if self.ship1_preview:
                self.screen.blit(self.ship1_preview, (self.ship1_select_rect.x + 45, self.ship1_select_rect.y + 25))
            s1_label = self.font.render("STANDARD", True, (255, 255, 255))
            self.screen.blit(s1_label, (self.ship1_select_rect.x + (self.ship1_select_rect.width // 2 - s1_label.get_width() // 2), self.ship1_select_rect.y + 130))

            is_s2 = self.selected_ship == "ADVANCED"
            s2_border = (0, 255, 200) if is_s2 else (80, 100, 140)
            pygame.draw.rect(self.screen, (20, 30, 60), self.ship2_select_rect, border_radius=8)
            pygame.draw.rect(self.screen, s2_border, self.ship2_select_rect, 3, border_radius=8)
            if self.ship2_preview:
                self.screen.blit(self.ship2_preview, (self.ship2_select_rect.x + 45, self.ship2_select_rect.y + 25))
            s2_label = self.font.render("ADVANCED", True, (255, 255, 255))
            self.screen.blit(s2_label, (self.ship2_select_rect.x + (self.ship2_select_rect.width // 2 - s2_label.get_width() // 2), self.ship2_select_rect.y + 130))

            pygame.draw.rect(self.screen, (150, 50, 50), self.back_button_rect, border_radius=4)
            pygame.draw.rect(self.screen, (255, 100, 100), self.back_button_rect, 2, border_radius=4)
            b_text = self.font.render("BACK", True, (255, 255, 255))
            self.screen.blit(b_text, (self.back_button_rect.x + (self.back_button_rect.width // 2 - b_text.get_width() // 2),
                                     self.back_button_rect.y + (self.back_button_rect.height // 2 - b_text.get_height() // 2)))

        # ==================== 4. LEADERBOARD STATE ====================
        elif self.game_state == "leaderboard":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button_rect.collidepoint(event.pos):
                        self.game_state = "menu"

            self.screen.fill((10, 15, 30))
            lb_title = self.big_font.render("LEADERBOARD", True, (255, 230, 0))
            self.screen.blit(lb_title, (self.screen_width // 2 - lb_title.get_width() // 2, 35))

            y_offset = 120
            for i, row in enumerate(self.leaderboard_data[:8]):
                txt = self.font.render(f"{i+1}. {row['username']} - {row['score']}", True, (255, 255, 255))
                self.screen.blit(txt, (self.screen_width // 2 - txt.get_width() // 2, y_offset))
                y_offset += 35

            pygame.draw.rect(self.screen, (150, 50, 50), self.back_button_rect, border_radius=4)
            pygame.draw.rect(self.screen, (255, 100, 100), self.back_button_rect, 2, border_radius=4)
            b_text = self.font.render("BACK", True, (255, 255, 255))
            self.screen.blit(b_text, (self.back_button_rect.x + (self.back_button_rect.width // 2 - b_text.get_width() // 2),
                                     self.back_button_rect.y + (self.back_button_rect.height // 2 - b_text.get_height() // 2)))

        # ==================== 5. SETTINGS STATE ====================
        elif self.game_state == "settings":
            music_rect = pygame.Rect(self.screen_width // 2 - 140, 180, 280, 45)
            controls_rect = pygame.Rect(self.screen_width // 2 - 140, 240, 280, 45)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if music_rect.collidepoint(event.pos):
                        self.settings["music"] = not self.settings["music"]
                        if self.settings["music"]:
                            try:
                                pygame.mixer.music.play(-1)
                            except Exception:
                                pass
                        else:
                            try:
                                pygame.mixer.music.stop()
                            except Exception:
                                pass
                    elif controls_rect.collidepoint(event.pos):
                        self.settings["mobile_controls"] = not self.settings["mobile_controls"]
                    elif self.back_button_rect.collidepoint(event.pos):
                        self.game_state = "menu"

            self.screen.fill((10, 15, 30))
            s_title = self.big_font.render("SETTINGS", True, (255, 230, 0))
            self.screen.blit(s_title, (self.screen_width // 2 - s_title.get_width() // 2, 40))

            pygame.draw.rect(self.screen, (50, 100, 150), music_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 180, 255), music_rect, 2, border_radius=4)
            m_status = "ON" if self.settings["music"] else "OFF"
            m_text = self.font.render(f"MUSIC: {m_status}", True, (255, 255, 255))
            self.screen.blit(m_text, (music_rect.x + (music_rect.width // 2 - m_text.get_width() // 2),
                                     music_rect.y + (music_rect.height // 2 - m_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (50, 100, 150), controls_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 180, 255), controls_rect, 2, border_radius=4)
            c_status = "ON" if self.settings["mobile_controls"] else "OFF"
            c_text = self.font.render(f"MOBILE CONTROLS: {c_status}", True, (255, 255, 255))
            self.screen.blit(c_text, (controls_rect.x + (controls_rect.width // 2 - c_text.get_width() // 2),
                                     controls_rect.y + (controls_rect.height // 2 - c_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (150, 50, 50), self.back_button_rect, border_radius=4)
            pygame.draw.rect(self.screen, (255, 100, 100), self.back_button_rect, 2, border_radius=4)
            b_text = self.font.render("BACK", True, (255, 255, 255))
            self.screen.blit(b_text, (self.back_button_rect.x + (self.back_button_rect.width // 2 - b_text.get_width() // 2),
                                     self.back_button_rect.y + (self.back_button_rect.height // 2 - b_text.get_height() // 2)))

        # ==================== 6. GAMEPLAY & BLINKING STATES ====================
        elif self.game_state == "playing" or self.game_state == "blinking":
            self.player_history.append((self.player.x, self.player.y))
            if len(self.player_history) > 60:
                self.player_history.pop(0)

            if self.game_state == "playing":
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.player.move_left()
                if keys[pygame.K_RIGHT]:
                    self.player.move_right()
                
                screen_button_fired = self.buttons.handle_mouse(self.player, events)
                
                # Rapid-fire support: checked via key hold (pygame.K_SPACE or K_UP)
                keyboard_fired = keys[pygame.K_SPACE] or keys[pygame.K_UP]
                
                # Limit bullet creation rate slightly so it streams continuously instead of spawning all at once in 1 frame
                if not hasattr(self, 'fire_cooldown'):
                    self.fire_cooldown = 0
                
                if self.fire_cooldown > 0:
                    self.fire_cooldown -= 1

                if (screen_button_fired or keyboard_fired) and self.fire_cooldown == 0:
                    self.bullets.append(Bullet(self.player.x + self.player.width // 2 - 16, self.player.y))
                    self.fire_cooldown = 8  # Controls rapid-fire speed

                self.player.keep_inside_screen()
                
                # Update all active bullets
                for bullet in self.bullets[:]:
                    bullet.update()
                    if not bullet.is_active:
                        self.bullets.remove(bullet)
                
                self.timer += 1
                
                if self.timer >= 180:
                    waiting_enemies = [e for e in self.enemies if e.state == "waiting"]
                    if waiting_enemies:
                        chosen_enemy = random.choice(waiting_enemies)
                        target_x, target_y = self.player_history[0]
                        chosen_enemy.start_drop(target_x, target_y)
                    self.timer = 0
                
                all_despawned = True
                for enemy in self.enemies:
                    enemy.update()
                    if enemy.state != "offscreen":
                        all_despawned = False
                
                if all_despawned:
                    self.level += 1  # Increment level when wave is cleared
                    self.spawn_number = 4 + self.level
                    self.spawn_enemies()

                self.check_collisions()

            elif self.game_state == "blinking":
                self.player.update_blink()
                self.state_timer += 1
                
                for enemy in self.enemies:
                    enemy.update()

                if self.state_timer >= 180: 
                    self.game_state = "game_over"

            # Render Game Objects
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            if self.settings.get("mobile_controls", True):
                self.buttons.draw(self.screen)
            
            # Upper-left UI Elements: Score and Level Tracker
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            level_text = self.font.render(f"Level: {self.level}", True, (255, 230, 0))
            self.screen.blit(score_text, (20, 20))
            self.screen.blit(level_text, (20, 50))

        # ==================== 7. GAME OVER STATE ====================
        elif self.game_state == "game_over":
            if not self.score_saved:
                user_to_save = self.logged_in_user if self.logged_in_user else "Guest"
                register_player_and_score(user_to_save, self.score)
                self.score_saved = True

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.reload_button_rect.collidepoint(event.pos):
                        self.game_state = "menu"

            go_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(go_text, (self.screen_width // 2 - go_text.get_width() // 2, self.screen_height // 2 - 100))
            
            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score_text, (self.screen_width // 2 - final_score_text.get_width() // 2, self.screen_height // 2 - 20))
            
            pygame.draw.rect(self.screen, (50, 150, 50), self.reload_button_rect, border_radius=4)
            btn_text = self.font.render("MAIN MENU", True, (255, 255, 255))
            self.screen.blit(btn_text, (self.reload_button_rect.x + (self.reload_button_rect.width // 2 - btn_text.get_width() // 2),
                                        self.reload_button_rect.y + (self.reload_button_rect.height // 2 - btn_text.get_height() // 2)))

    def check_collisions(self):
        player_rect = self.player.get_rect()

        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue

            enemy_rect = enemy.get_rect()
            
            if player_rect.colliderect(enemy_rect):
                self.game_state = "blinking"
                self.player.is_blinking = True
                self.state_timer = 0
                return
            
            # Check collisions with all active rapid-fire bullets
            for bullet in self.bullets[:]:
                if bullet.get_rect().colliderect(enemy_rect):
                    self.bullets.remove(bullet)
                    
                    # Handle Boss (5 hits to die) vs Regular Enemies
                    if getattr(enemy, "is_boss", False):
                        enemy.health = getattr(enemy, "health", 5) - 1
                        if enemy.health <= 0:
                            enemy.state = "offscreen"
                            self.score += 10  # Higher score for defeating the boss
                    else:
                        enemy.state = "offscreen"
                        self.score += 1
                    break