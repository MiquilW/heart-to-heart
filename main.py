import pygame, asyncio
from sys import exit
from random import randint, choices

async def main():
  # Player Object
  class Player(pygame.sprite.Sprite):
      i = 0
      current_time = 0
      power_up_timer = 0
      jump_particles = []
      shield_timer = 0
      gaf = 1
      half = 1
    
      def __init__(self):
          super().__init__()
          player_walk_1 = pygame.image.load('img//spida.png').convert_alpha()
          player_walk_2 = pygame.image.load('img//spida_walk.png').convert_alpha()
          self.player_walk = [player_walk_1, player_walk_2]
          self.player_index = 0

          self.image = self.player_walk[self.player_index]
          self.rect = self.image.get_rect(midbottom=(800, 0))
          self.gravity = 0
          self.is_jumping = False

          self.dx = 0
          self.dy = 0
          self.jump_magnitude = -20
          Player.player_center = self.rect.center
          Player.playerx = self.rect.centerx
          Player.playery = self.rect.centery
          Player.player_midbottom = self.rect.midbottom

          self.jump_sound = pygame.mixer.Sound('audio//jump.wav')
          self.jump_sound.set_volume(0.1)

      # Player movement & animations
      def player_input(self):
          self.dx = 0
          self.dy = 0
          if not self.is_jumping:
              self.image = pygame.image.load('img//spida.png').convert_alpha()

          keys = pygame.key.get_pressed()
          # Move right
          if keys[pygame.K_d]:
              self.dx = 10
              if not self.is_jumping:
                  self.player_index += 0.1
                  if self.player_index >= len(self.player_walk):
                      self.player_index = 0
                  self.image = self.player_walk[int(self.player_index)]

          # Move left
          if keys[pygame.K_a]:
              self.dx = -10
              if not self.is_jumping:
                  self.player_index += 0.1
                  if self.player_index >= len(self.player_walk):
                      self.player_index = 0
                  self.image = self.player_walk[int(self.player_index)]

          if self.is_jumping:
              self.image = pygame.image.load('img//spida_jump.png').convert_alpha()

          self.rect.x += self.dx
          self.rect.y += self.dy

          if self.rect.x > 1650:
              self.rect.x = -50
          if self.rect.x < -50:
              self.rect.x = 1650

      def apply_gravity(self):
          self.gravity += 1
          self.rect.y += self.gravity
          if self.gravity > 6:
              self.gravity = 6

      def collision(self):
          collision_tolerance = 10
          for platform in platform_group:
              if self.rect.colliderect(platform.rect):
                  if abs(platform.rect.top - self.rect.bottom) < collision_tolerance and self.gravity > 0:
                      self.rect.bottom = platform.rect.top
                      self.is_jumping = False
                      keys = pygame.key.get_pressed()
                      if keys[pygame.K_SPACE] or keys[pygame.K_w]:
                          self.is_jumping = True
                          self.gravity = self.jump_magnitude
                          self.jump_sound.play()

                  if abs(platform.rect.right - self.rect.left) < collision_tolerance:
                      self.rect.x = 0
                      self.rect.left = platform.rect.right
                  if abs(platform.rect.left - self.rect.right) < collision_tolerance:
                      self.rect.x = 0
                      self.rect.right = platform.rect.left

      # Updates players properties every frame
      def update(self):
          power_ups(type_producer[Player.i])
          self.player_input()
          self.apply_gravity()
          self.collision()
          Player.player_center = self.rect.center
          Player.playerx = self.rect.centerx
          Player.playery = self.rect.centery
          Player.player_midbottom = self.rect.midbottom
          Player.gravity = self.gravity


  # Enemy Object
  class Enemy(pygame.sprite.Sprite):
      enemy_time = 1000
    
      def __init__(self, type):
          super().__init__()

          if type == 'skull':
              self.image = pygame.image.load('img//skull.png').convert_alpha()
              self.type = 'skull'
              ypos = 850
          else:
              self.image = pygame.image.load('img//flamingskull.png').convert_alpha()
              self.type = 'bird'
              ypos = -50

          self.rect = self.image.get_rect(midbottom=(randint(100, 1500), ypos))

      def update(self):
          if self.type == 'skull':
              self.rect.y -= 5 // Player.half * Player.gaf
          else:
              self.rect.y += 10 // Player.half * Player.gaf
          self.destroy()

      def destroy(self):
          if self.rect.y <= -100 or self.rect.y >= 900:
              self.kill()


  # Moving platform object
  class Platform(pygame.sprite.Sprite):
      platform_time = 500
    
      def __init__(self):
          super().__init__()
          self.image = pygame.image.load('img//platform.png').convert_alpha()
          self.rect = self.image.get_rect(midtop=(randint(100, 1500), 800))

      def destroy(self):
          if self.rect.y <= -100 or self.rect.y >= 900:
              self.kill()

      def update(self):
          self.rect.y -= 2 // Player.half
          self.destroy()


  # Coin-like heart objects
  class Collectible(pygame.sprite.Sprite):
      def __init__(self):
          super().__init__()
          self.image = pygame.image.load('img//heart.png').convert_alpha()
          self.rect = self.image.get_rect(midbottom=(randint(100, 1500), randint(300, 600)))


  # Power-up Object
  class PowerUp(pygame.sprite.Sprite):
      def __init__(self, type):
          super().__init__()
          if type == 'kill':
              self.image = pygame.image.load('img//kill.png').convert_alpha()
              self.rect = self.image.get_rect(midbottom=(randint(100, 1500), randint(300, 600)))
          if type == 'slow':
              self.image = pygame.image.load('img//time.png').convert_alpha()
              self.rect = self.image.get_rect(midbottom=(randint(100, 1500), randint(300, 600)))
          if type == 'shield':
              self.image = pygame.image.load('img//shieldy.png').convert_alpha()
              self.rect = self.image.get_rect(midbottom=(randint(100, 1500), randint(300, 600)))


  # Shield object for shield power-up
  class Shield(pygame.sprite.Sprite):
      shield_filter = False
    
      def __init__(self):
          super().__init__()
          self.image = pygame.image.load('img//theshield.png').convert_alpha()
          self.rect = self.image.get_rect(center=Player.player_center)

      def update(self):
          self.rect.centerx = Player.playerx
          self.rect.centery = Player.playery


  # Function to apply effects of power-ups
  def power_ups(power_up_type):

      # Debug code ===> print('current: ' + str(current_time) + ' power: ' + str(power_up_timer))

      if power_up_type == 'kill':
          if grab_power():
              enemy_group.empty()
              Player.gaf = 0
              Player.power_up_timer = pygame.time.get_ticks()
              Player.i += 1
              if Player.i == 50:
                  Player.i = 0

      if power_up_type == 'slow':
          if grab_power():
              Player.half = 2
              Player.power_up_timer = pygame.time.get_ticks()
              Player.i += 1
              if Player.i == 50:
                  Player.i = 0

      if power_up_type == 'shield':
          if grab_power():
              shield.add(Shield())
              Shield.shield_filter = True
              Player.i += 1
              if Player.i == 50:
                  Player.i = 0

      if Player.current_time - Player.power_up_timer > 6000:
          if len(enemy_group) > 11:
              enemy_group.empty()
          Player.half = 1
          Player.gaf = 1


  # Checks for collisions between player & enemies and player & death-zone
  def collision_sprite():
      if pygame.sprite.spritecollide(player.sprite, enemy_group, False):
          enemy_group.empty()
          platform_group.empty()
          death_sound.play()
          return False
      for you in player:
          if you.rect.y > 900:
              death_sound.play()
              return False
      else:
          return True


  # Particle system for player jumps
  def player_particles():
      if Player.gravity < 6:
          bx = Player.player_midbottom[0]
          by = Player.player_midbottom[1]
          Player.jump_particles.append([[bx, by], [randint(-5, 5), 2], randint(5, 6)])
          for particle in Player.jump_particles:
              particle[0][0] += particle[1][0]
              particle[0][1] += particle[1][1]
              particle[2] -= 0.3
              pygame.draw.circle(screen, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
              if particle[2] <= 0:
                  Player.jump_particles.remove(particle)
      if Player.gravity >= 6:
          Player.jump_particles = []


  # Checks collision for shield & updates it accordingly
  def collision_groups():
      if pygame.sprite.groupcollide(shield, enemy_group, True, False):
          Player.shield_timer = pygame.time.get_ticks()
          shield_break_sound.play()
      if Player.current_time - Player.shield_timer > 2000 and Player.shield_timer != 0:
          Shield.shield_filter = False
          Player.shield_timer = 0


  # Collect heart function
  def collect():
      if pygame.sprite.spritecollide(player.sprite, coin, True):
          pickup_coin.play()
          return True


  # Collect power-up function
  def grab_power():
      if pygame.sprite.spritecollide(player.sprite, power_up, True):
          power_up_sound.play()
          return True


  # Score display
  def display_score():
      score_surface = title_font.render(str(score), True, (255, 132, 156))
      score_rect = score_surface.get_rect(center=(800, 75))
      screen.blit(score_surface, score_rect)
      return score


  # Initializations
  pygame.init()


  width = 1600
  height = 800
  screen = pygame.display.set_mode((width, height))
  pygame.display.set_caption('Heart-to-Heart')
  font = pygame.font.SysFont('timesnewroman', 50)
  title_font = pygame.font.SysFont('timesnewroman', 100)
  clock = pygame.time.Clock()
  game_active = False
  score = 0

  a = pygame.image.load('img//beige.png')
  pygame.display.set_icon(a)

  player = pygame.sprite.GroupSingle()
  player.add(Player())

  coin = pygame.sprite.Group()
  coin.add(Collectible())

  power_up = pygame.sprite.Group()

  shield = pygame.sprite.Group()

  enemy_group = pygame.sprite.Group()

  platform_group = pygame.sprite.Group()

  enemy_rect_list = []
  platform_rect_list = []
  power_up_rect_list = []

  enemy_timer = pygame.USEREVENT + 1
  platform_timer = pygame.USEREVENT + 2

  pygame.time.set_timer(enemy_timer, Enemy.enemy_time * Player.half)
  pygame.time.set_timer(platform_timer, Platform.platform_time)

  death_sound = pygame.mixer.Sound('audio//death.wav')
  death_sound.set_volume(0.1)

  pickup_coin = pygame.mixer.Sound('audio//pickup_coin.wav')
  pickup_coin.set_volume(0.1)

  power_up_sound = pygame.mixer.Sound('audio//power_up.wav')
  power_up_sound.set_volume(0.2)

  shield_break_sound = pygame.mixer.Sound('audio//shieldbreak.wav')
  power_up_sound.set_volume(0.2)

  type_producer = choices(['kill', 'slow', 'shield'], k=50)

  once = False
  # Power-up type debug code ===> print(type_producer)

  # Main game loop
  while True:
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              pygame.quit()
              exit()
          # Enemy/Platform adder
          if game_active:
              if event.type == enemy_timer:
                  enemy_group.add(Enemy('skull'))
                  if score >= 10:
                      enemy_group.add(Enemy('flamingskull'))
              if event.type == platform_timer:
                  platform_group.add(Platform())

      if game_active:
          Player.current_time = pygame.time.get_ticks()

          screen.fill('Black')

          power_up.draw(screen)
          power_up.update()

          coin.draw(screen)
          coin.update()

          platform_group.draw(screen)
          platform_group.update()

          enemy_group.draw(screen)
          enemy_group.update()

          player.draw(screen)
          player.update()

          shield.draw(screen)
          shield.update()

          for you in player:
              if you.rect.y > 900:
                  death_sound.play()
                  game_active = False

          if collect():
              score += 1
              coin.add(Collectible())
              coin.draw(screen)
              coin.update()
              once = False

          # Power-up adder every 10 points
          if score % 10 == 0 and score != 0 and not once:
              if len(power_up) == 0:
                  power_up.add(PowerUp(type_producer[Player.i]))
                  once = True

          if Shield.shield_filter is False:
              game_active = collision_sprite()

          player_particles()

          collision_groups()

          display_score()

      # When game is just started or player has lost
      else:
          keys = pygame.key.get_pressed()
          # Reinitialize everything when player starts the game
          if keys[pygame.K_w]:
              game_active = True
              score = 0
              player.remove()
              player.add(Player())
              coin.empty()
              coin.add(Collectible())
              enemy_group.empty()
              platform_group.empty()
              power_up.empty()
              Player.half = 1
              Player.gaf = 1
              Player.power_up_timer = 0
              Player.shield_timer = 0
              Player.current_time = 0
              shield.empty()
              Shield.shield_filter = False

          screen.fill('Black')

          score_message = font.render('Your score: ' + str(score), True, (255, 132, 156))
          score_message_rect = score_message.get_rect(center=(800, 520))

          title = title_font.render('Heart-to-Heart', True, (255, 132, 156))
          title_rect = title.get_rect(center=(800, 350))

          title2 = font.render('Press "w" to start', True, (255, 132, 156))
          title2_rect = title2.get_rect(center=(800, 450))

          screen.blit(title, title_rect)
          screen.blit(title2, title2_rect)

          if score > 0:
              screen.blit(score_message, score_message_rect)

      pygame.display.update()
      clock.tick(60)
      await asyncio.sleep(0)
    
asyncio.run( main() )
