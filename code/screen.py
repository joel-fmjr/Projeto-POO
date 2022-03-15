import pygame
from read_json import settings


class Screen:
    def __init__(self, screen_type, function):
        self.display_surface = pygame.display.get_surface()
        self.img_surface = pygame.image.load(
            settings['screen_img'][screen_type])
        self.background_sound = pygame.mixer.Sound(
            'audio/screen/'+screen_type+'.wav')
        self.background_sound.set_volume(0.2)
        self.function = function
        self.call_time = None
        self.call_trigger = False

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.call_time = pygame.time.get_ticks()
            self.call_trigger = True

    def cooldown(self):
        if self.call_trigger:
            current_time = pygame.time.get_ticks()
            if current_time > self.call_time + 1000:
                self.background_sound.stop()
                self.function()

    def run(self):
        self.display_surface.blit(self.img_surface, (0, 0))
        self.background_sound.play(loops=-1, fade_ms=1)
        self.input()
        self.cooldown()
