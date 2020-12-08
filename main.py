import pygame as pg
import  sys
import random
from settings import *

from sprite import  *
from  os import path
from tilemap import *


# HUD function
def draw_player_health(surf, x, y, pct):
    if pct <0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x,y, BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pg.Rect(x,y,fill,BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf,col,fill_rect)
    pg.draw.rect(surf,WHITE, outline_rect,2)

class Game:
    def __init__(self):
        # initialize pygame and create window
        pg.mixer.pre_init(44100,-16,1,2048)
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        #pg.key.set_repeat(500,100)
        self.running = True
        self.level = 1

        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = game_folder+"/PNG"
        self.map_folder = game_folder+"/maps"
        snd_folder = game_folder+"/snd"
        music_folder = game_folder+"/music"
        self.title_font = game_folder+"/font/ZOMBIE.TTF"
        self.hud_font = game_folder+"/font/Impacted2.0.ttf"


        self.dim_image = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_image.fill((0,0,0,180))

        self.player_img = pg.image.load(img_folder+"/player/"+ PLAYER_IMAGE).convert_alpha()
        self.player_gun = "weapon_gun.png"
        self.player_gun_img = pg.image.load(img_folder+"/weapons/"+self.player_gun).convert_alpha()

        self.mob_img = pg.image.load(img_folder+"/mobs/"+MOB_IMG).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(img_folder+"/weapons/"+BULLET_IMG).convert_alpha()
        self.bullet_images['sm'] =  pg.transform.scale(self.bullet_images['lg'],(10,10))
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(img_folder+"/weapons/muzzle_flash/"+img).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGE:
            self.item_images[item] = pg.image.load(img_folder+"/items/"+ ITEM_IMAGE[item])
        self.splat = pg.image.load(img_folder+"/mobs/"+SPLAT ).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64,64))

        # sound loading
        pg.mixer.music.load(music_folder+"/"+BG_MUSIC)
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(snd_folder+"/"+ EFFECTS_SOUNDS[type])
        self.weapon_sounds = {}
        self.weapon_sounds['gun']= []
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon]  = []
            for snd in WEAPON_SOUNDS[weapon]:

                s=pg.mixer.Sound(snd_folder+"/"+snd)
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)

        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(snd_folder+"/"+snd)
            s.set_volume(0.1)
            self.zombie_moan_sounds.append(s)

        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(snd_folder+"/"+snd))
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(snd_folder + "/" + snd))


    def new(self):
        #reset the game

        self.map = TiledMap(self.map_folder +"/"+ LEVEL[self.level])

        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()

        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width/2, tile_object.y+tile_object.height/2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x,tile_object.y,tile_object.width,tile_object.height)
            if tile_object.name == 'zombie':
               Mob(self, obj_center.x,obj_center.y)
            if tile_object.name in ['health','shotgun']:
               Item(self, obj_center, tile_object.name)

        self.camera = Camera(self.map.width,self.map.height)
        self.draw_debug = False
        self.effects_sounds['level_start'].play()
        self.pause = 0
    def run(self):
        #game loop

        self.playing = True
        pg.mixer.music.play(-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.pause:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()


    def update(self):

        self.all_sprites.update()
        self.camera.update(self.player)


        # NEXT LEVEL
        if len(self.mobs) == 0 :
            self.playing = False
            if self.level == len(LEVEL)-1:
                self.level = 1
                self.playing = False
                self.show_start_screen()

            else:
                self.level+=1
                self.next_screen()


        # player hit item
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type == 'shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'
        # mob hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits :
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0,0)
            if self.player.health <= 0:
                self.playing = False

                self.show_go_screen()
        if hits:
            self.player.hit()
            self.player.pos += vec(MOB_KNOCKBACK,0).rotate(-hits[0].rot)
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = vec(0,0)
            mob.hit = 1

    def events(self):
        for event in pg.event.get():
            # check for closing the window
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_SPACE:
                    self.draw_debug =  not self.draw_debug
                if event.key == pg.K_p:
                    self.pause = not self.pause



    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))

        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()

            self.screen.blit(sprite.image,self.camera.apply(sprite))




        # HUD function
        draw_player_health(self.screen, 10,10,self.player.health / PLAYER_HEALTH)
        self.draw_text('Zombie: {}'.format(len(self.mobs)), self.hud_font, 30, WHITE,
                       WIDTH -10, 10, align="ne")

        if self.pause:
            self.screen.blit(self.dim_image,(0,0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH/2, HEIGHT/2, align="center")

        pg.display.flip()


    def show_start_screen(self):
        self.screen.fill(BLACK)
        level ="level " + str(self.level)
        self.draw_text("Start", self.title_font,
                       100, RED, WIDTH / 2,  HEIGHT*1/4, align="center")
        self.draw_text(level, self.title_font,
                       75, RED, WIDTH / 2, HEIGHT /2, align="center")
        self.draw_text("Press a key to begin", self.title_font,
                       75, WHITE, WIDTH / 2, HEIGHT* 3/4 , align="center")
        pg.display.flip()

        self.wait_for_key()

    def next_screen(self):
        pg.event.wait()
        self.screen.fill(BLACK)
        level = "level " + str(self.level)
        self.draw_text("Start", self.title_font,
                       100, RED, WIDTH / 2, HEIGHT * 1 / 4, align="center")
        self.draw_text(level, self.title_font,
                       75, RED, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to begin", self.title_font,
                       75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()


        self.wait_for_key()

    def show_go_screen(self):
        pg.event.wait()
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font,
                       100, RED, WIDTH/2, HEIGHT/2, align="center")
        self.draw_text("Press a key to start", self.title_font,
                       75, WHITE, WIDTH / 2, HEIGHT *3 / 4, align="center")
        pg.display.flip()

        self.wait_for_key()

    def wait_for_key(self):

        pg.event.wait() #start with a fresh event
        check = 0

        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:

                    waiting = False



g = Game()
g.show_start_screen()
while True :
    g.new()
    g.run()
    #g.show_go_screen()

g.quit()




