import pygame as pg
import math
from settings import *
from tilemap import *
from  random import  uniform,choice,randint, random
import  pytweening as tween
from  itertools import  chain


vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2.0
            if hits[0].rect.centerx < sprite.hit_rect.centerx :
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2.0
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2.0
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2.0
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y, angle=0):
        self.groups = game.all_sprites
        self._layer = PLAYER_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img[0]


        self.rect = self.image.get_rect()



        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0


        self.health = PLAYER_HEALTH
        self.rect.center = (x, y)

        self.leg = Leg(game,game.anin,self.rect.center)
        self.leg.move()

        self.currence_weapon = 0
        self.weapon_list =game.weapon_list
        self.weapons = []
        for gun in self.weapon_list :
            self.weapons.append(Gun(game,gun,self.pos))


        self.damaged = False
        pos = self.pos + vec(18, 13).rotate(-self.rot)

        self.gun = self.weapons[self.currence_weapon]
        self.gun.active = 1
        self.weaponchange()

        self.reload = 0
        self.need_weapon = 0

        self.weapon_change_time = pg.time.get_ticks()
        self.weapons_reload_time = 0

        self.gun.shoot_flag = 0

    def new_pos(self,x,y):
        self.pos = vec(x, y)
    def add_gun(self,name):

        self.weapon_list = self.game.weapon_list
        self.weapons.append(Gun(self.game, name, self.pos))
        self.currence_weapon = len(self.weapons)-1

    def weaponchange(self):

        self.gun.active = 0
        self.gun = self.weapons[self.currence_weapon]
        self.gun.active = 1


    def get_angle(self, mouse):

        #Find the new angle between the center of the Turret and the mouse.


        co = self.game.camera.cordinate() # get corniate of the camera from top left



        self.rot = -math.degrees(math.atan2(co[1] + mouse[1] - self.rect.centery, co[0] + mouse[0] - self.rect.centerx))


    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)

        keys = pg.key.get_pressed()
        mouse = pg.mouse
        moBut = mouse.get_pressed()
        if keys[pg.K_r]:
            self.reload = 1
            self.weapons_reload_time = pg.time.get_ticks()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            # self.rot_speed = PLAYER_ROT_SPEED
            self.vel += vec(-PLAYER_SPEED, 0)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            # self.rot_speed = -PLAYER_ROT_SPEED
            self.vel += vec(PLAYER_SPEED, 0)
        if keys[pg.K_UP] or keys[pg.K_w]:
            # self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
            self.vel += vec(0, -PLAYER_SPEED)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            # self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            self.vel += vec(0, PLAYER_SPEED)
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel = self.vel * 0.7071
        if keys[pg.K_q]:
            if pg.time.get_ticks()-self.weapon_change_time  >500:
                self.currence_weapon +=1
                if self.currence_weapon >= len(self.weapon_list):
                    self.currence_weapon = 0
                self.need_weapon = 1
                self.weapon_change_time = pg.time.get_ticks()
                # cancel when change gun
                self.weapons_reload_time = pg.time.get_ticks()
                self.reload = 0

        if mouse:

            self.get_angle(mouse.get_pos())
        if moBut[0] and self.gun.bullet_in_chamber > 0:#left click

            #cancel when shoot
            self.weapons_reload_time = pg.time.get_ticks()
            self.reload = 0
            #shoot

            self.gun.shoot_flag = 1




    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

    def hit(self):
        self.damaged = True
        self.damaged_alpha = chain(DAMAGE_ALPHA *2)
    def update(self):
        self.get_keys()

        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img[WEAPONS[self.gun.weapon]['hand']], self.rot)
        #self.gun_img = pg.transform.rotate(self.game.player_gun_img, self.rot)
        # self.image = pg.transform.rotate(self.game.player_img, self.angle)
        if self.damaged:
            try:
                self.image.fill((255,255,255, next(self.damaged_alpha)),
                                special_flags= pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False

        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt


        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        # use hit_rect.center instead of pos because of the line above
        self.leg.follow(self.hit_rect.center, self.rot)
        for gun in self.weapons:
            gun.follow(self.hit_rect.center, self.rot)

        if self.vel.length()>0:
            self.leg.move()


        if self.reload == 1:
            if pg.time.get_ticks() - self.weapons_reload_time > 1000:
                if self.gun.bullet_in_chamber < self.gun.max_bullets:
                    if self.gun.megazine >= self.gun.max_bullets:
                        self.gun.megazine -= int(self.gun.max_bullets) - self.gun.bullet_in_chamber
                        self.gun.bullet_in_chamber = int(self.gun.max_bullets)

                    else:
                        self.gun.bullet_in_chamber += int(self.gun.megazine)
                        self.gun.megazine = 0

                self.reload = 0

        if self.need_weapon == 1:
            self.weaponchange()
            self.need_weapon = 0

class BossBoltStrike(pg.sprite.Sprite):

    def __init__(self, game, pos, dir,rot):
        self.groups = game.all_sprites,game.projectile
        self._layer = MOB_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.mob2_img = game.mob2_img['boltStrike']
        self.image = game.mob2_img['boltStrike'][0]
        self.hit_box = game.mob2_img['hit_box']
        self.rect = self.image.get_rect()
        self.no = vec(pos) + vec(250,40).rotate(-rot)
        self.pos = vec(pos) + vec(250,40).rotate(-rot)
        self.rect.center = self.pos
        self.hit_rect = self.hit_box.get_rect()
        self.hit_rect.center = self.rect.center
        self.hit = 1

        self.vel = dir * 50000000
        self.rot = rot

        #self.strike_time = 100
        self.frame_now = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 80

        print("ok")
    def move(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now

            self.frame_now += 1
            if self.frame_now == 10:
                self.frame_now = -1
                self.kill()

    def update(self):
        self.move()
        self.image = pg.transform.rotate(self.game.mob2_img['boltStrike'][self.frame_now].copy(), self.rot-90)

        self.rect = self.image.get_rect()
        self.rect.center = self.no
        self.pos += self.vel * self.game.dt

        self.hit_rect.center = self.pos




class Boss(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        self._layer = MOB_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob2_img['move'][0].copy() # FIX bug double image
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.rot = 0
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = BOSS_HEALTH

        self.speed = choice(MOB_SPEED)
        self.rect.center = (x,y)
        self.target = game.player
        self.hitted = 0
        self.damaged = False

        self.frame_now = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 80
        self.sp_rate = 100

        self.mob2_img = game.mob2_img
        self.attact_flag = 0
        self.attact_frame = -1

        self.sp_flag = 0
        self.sp_frame = -1


    def move(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            if self.sp_flag == 1:
                self.attact_flag = 0
                if now - self.last_update >  self.frame_rate :
                    self.last_update = now

                    self.sp_frame += 1
                    if self.sp_frame == len(self.mob2_img['spmove']):
                        self.sp_flag = 0
                        self.sp_frame = -1


            if self.attact_flag == 1 and self.sp_flag == 0:

                    self.last_update = now
                    self.attact_frame +=1
                    if self.attact_frame == len(self.mob2_img['attack']):
                        self.attact_flag = 0
                        self.attact_frame = -1
            else:

                    self.last_update = now
                    self.frame_now += 1
                    if self.frame_now == len(self.mob2_img['move']):
                        self.frame_now = -1

    def stop(self):
        self.moving = 0

    def attact(self):
        if abs(self.pos.length() - self.target.pos.length()) <80:
            self.attact_flag = 1


    def MoveSet(self):
        dir = vec(1, 0).rotate(-self.rot)
        rot = self.rot%360
        self.bos = BossBoltStrike(self.game,self.pos,dir,rot)
    def update(self):

        target_dist = self.target.pos - self.pos

        # faster a bit
        self.hitted = 1
        if random() <0.002:
            choice(self.game.zombie_moan_sounds).play()

        if random() <0.005 and self.sp_flag == 0:
            self.sp_flag = 1
            self.MoveSet()
        self.move()# update frame
        self.attact()

        self.rot = target_dist.angle_to(vec(1, 0))

        self.image = pg.transform.rotate(self.game.mob2_img['move'][self.frame_now], self.rot)
        if self.sp_flag == 1:
            self.image = pg.transform.rotate(self.game.mob2_img['spmove'][self.sp_frame], self.rot)

        else:
            if self.attact_flag == 1 and self.sp_flag == 0:
                self.image = pg.transform.rotate(self.game.mob2_img['attack'][self.attact_frame], self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center


        if self.health <=0:
            choice(self.game.zombie_hit_sounds).play()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32,32))
            self.game.score +=10 #up the score
            self.kill()

    def draw_health(self):
        if self.health >BOSS_HEALTH/2:
            col = GREEN
        elif self.health > BOSS_HEALTH/4:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width*self.health / BOSS_HEALTH)
        self.health_bar = pg.Rect(0,0 , width, 7)
        if self.health < BOSS_HEALTH:

            pg.draw.rect(self.image, col, self.health_bar)
class Mob2(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        self._layer = MOB_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob2_img['move'][0].copy() # FIX bug double image
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.rot = 0
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = MOB_HEALTH

        self.speed = choice(MOB_SPEED)
        self.rect.center = (x,y)
        self.target = game.player
        self.hitted = 0
        self.damaged = False

        self.frame_now = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 80

        self.mob2_img = game.mob2_img
        self.attact_flag = 0
        self.attact_frame = -1


    def avoid_mob(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0< dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def d(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if mob.hitted == 1 and  0< dist.length() < 75:
                    self.hitted = 1

    def move(self):
        now = pg.time.get_ticks()
        if self.attact_flag == 1:
            if now - self.last_update > self.frame_rate:
                self.last_update = now

                self.attact_frame +=1
                if self.attact_frame == len(self.mob2_img['attack']):
                    self.attact_flag = 0
                    self.attact_frame = -1
        else:
            if now - self.last_update > self.frame_rate:

                self.last_update = now
                self.frame_now += 1
                if self.frame_now == len(self.mob2_img['move']):
                    self.frame_now = -1

    def stop(self):
        self.moving = 0

    def attact(self):
        if abs(self.pos.length() - self.target.pos.length()) <80:
            self.attact_flag = 1


    def update(self):

        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < DETECT_RADIUS**2 or self.hitted == 1:
            # faster a bit
            self.hitted = 1
            if random() <0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.move()# update frame
            self.attact()

            self.rot = target_dist.angle_to(vec(1, 0))

            self.image = pg.transform.rotate(self.game.mob2_img['move'][self.frame_now], self.rot)
            if self.attact_flag == 1:
                self.image = pg.transform.rotate(self.game.mob2_img['attack'][self.attact_frame], self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mob()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt

            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2


            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        self.follow_the_damaged()

        if self.health <=0:
            choice(self.game.zombie_hit_sounds).play()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32,32))
            self.game.score +=10 #up the score
            self.kill()
    def follow_the_damaged(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if mob.hitted == 1 and  0< dist.length() < 75:
                    self.hitted = 1

    def draw_health(self):
        if self.health >60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width*self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0,0 , width, 7)
        if self.health < MOB_HEALTH:

            pg.draw.rect(self.image, col, self.health_bar)
class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        self._layer = MOB_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy() # FIX bug double image
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.rot = 0
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEED)
        self.rect.center = (x,y)
        self.target = game.player
        self.hitted = 0
        self.damaged = False

    def avoid_mob(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0< dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def follow_the_damaged(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if mob.hitted == 1 and  0< dist.length() < 150:
                    self.hitted = 1



    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < DETECT_RADIUS**2 or self.hitted == 1:
            # faster a bit
            self.hitted = 1
            if random() <0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.rot = target_dist.angle_to(vec(1, 0))
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.game.mob_img, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mob()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2


            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        self.follow_the_damaged()
        if self.health <=0:
            choice(self.game.zombie_hit_sounds).play()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32,32))
            self.game.score +=10 #up the score
            self.kill()

    def draw_health(self):
        if self.health >60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width*self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0,0 , width, 7)
        if self.health < MOB_HEALTH:

            pg.draw.rect(self.image, col, self.health_bar)

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage,rot) :
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon_list[game.player.currence_weapon]]['bullet_size']]
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        #spread = uniform(-GUN_SPREAD,GUN_SPREAD)
        self.vel = dir * WEAPONS[game.player.weapon_list[game.player.currence_weapon]]['bullet_speed'] * uniform(0.9,1.1)
        self.spawn_time = pg.time.get_ticks()
        self.hit_rect = self.rect
        self.damage = damage
        self.rot = rot

    def update(self):

        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon_list[self.game.player.currence_weapon]]['bullet_lifetime']:
            self.kill()
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups =  game.walls
        self._layer = WALL_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game


        self.rect = pg.Rect(x,y,w,h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self,game,pos):
        self.groups = game.all_sprites
        self._layer = EFFECTS_LAYER
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        size = randint(20,50)
        self.image = pg.transform.scale(choice(game.gun_flashes),(size,size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self,game,pos, type):
        self._layer = ITEM_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self,self.groups)
        self.type = type
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1
        self.pos = pos

    def update(self):
        # bobbing moiton
        offset = BOB_RANGE * (self.tween(self.step/BOB_RANGE)-0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

class Gun(pg.sprite.Sprite):
    def __init__(self, game, name,  pos):
        self.groups = game.all_sprites, game.Guns
        self._layer = PLAYER_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_guns_img[name]
        self.weapon = name

        self.rect = self.image.get_rect()

        self.last_shot = - WEAPONS[self.weapon]['rate']



        self.pos = pos
        self.rect.center = pos
        self.rot = 0

        self.bullet_in_chamber = WEAPONS[self.weapon]['max_bullets']
        self.max_bullets = WEAPONS[self.weapon]['max_bullets']
        self.megazine = WEAPONS[self.weapon]['left']

        self.active = 0


        self.shoot_flag = 0



    def follow(self,pos,rot):

        self.rot = rot%360
        self.pos = pos + WEAPONS[self.weapon]['pos'].rotate(-rot)



    def shoot(self):



        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + BARREL_OFFSET.rotate(-self.rot)

            self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spred = uniform(-WEAPONS[self.weapon]['spread'],WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spred), WEAPONS[self.weapon]['damage'],self.rot)



                snd = choice(self.game.weapon_sounds[self.weapon])
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()
            self.bullet_in_chamber -= 1
            MuzzleFlash(self.game, pos)



    def update(self):

        self.image = pg.transform.rotate(self.game.player_guns_img[self.weapon].copy(), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        if self.shoot_flag == 1:
            self.shoot()
            self.shoot_flag = 0

class Effect(pg.sprite.Sprite):
    def __init__(self, center, rot,  anin):
        self._layer = 4
        pg.sprite.Sprite.__init__(self)
        #self.size = size
        self.rot = rot


        self.frame_now = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 35
        self.anin = anin
        self.image = pg.transform.rotate(self.anin[self.frame_now], 180+self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = center


    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_now += 1
            if self.frame_now == len(self.anin):
                self.kill()
            else:
                center = self.rect.center
                self.image = pg.transform.rotate(self.anin[self.frame_now],180+self.rot)
                self.rect = self.image.get_rect()
                self.rect.center = center

class Explosion(pg.sprite.Sprite):
    def __init__(self, center, size, explosion_anin):
        self._layer = 4
        pg.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anin[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame_now = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 35
        self.explosion_anin = explosion_anin

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_now += 1
            if self.frame_now == len(self.explosion_anin[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion_anin[self.size][self.frame_now]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Leg(pg.sprite.Sprite):
    def __init__(self, game, anin, pos):
        self._layer = 1
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)

        self.image = anin[0]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos

        self.frame_now = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 80
        self.anin = anin
        self.game = game


        self.rot = 0

        self.check = 0

        self.moving = 0
    def move(self):
        now = pg.time.get_ticks()

        if now - self.last_update > self.frame_rate:

            self.last_update = now
            self.frame_now += 1
            if self.frame_now == len(self.anin):
                self.frame_now = -1

    def stop(self):
        self.moving = 0
    def follow(self,pos,rot):

        self.rot = rot%360
        self.pos = vec(pos)



        self.update()

    def update(self):



        self.image = pg.transform.rotate(self.game.anin[self.frame_now].copy(), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos



