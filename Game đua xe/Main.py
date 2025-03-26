# Thư viện
import os
import sys
os.chdir(os.path.dirname(__file__))
base_path = getattr(sys, '_MEIPASS', os.getcwd())
    
import pygame
from pygame.locals import *
import random

pygame.init()

# Âm thanh
pygame.mixer.init()

# Tải nhạc nền và hiệu ứng âm thanh
pygame.mixer.music.load('sounds/background_music.mp3')  # Nhạc nền
crash_sound = pygame.mixer.Sound('sounds/crash.wav')  # Âm thanh khi chạm
point_sound = pygame.mixer.Sound('sounds/point.wav')  # Âm thanh khi tăng điểm
highscore_sound = pygame.mixer.Sound('sounds/highscore.wav')  # Âm thanh khi đạt highscore
accelerate_sound = pygame.mixer.Sound('sounds/accelerate.wav')  # Âm thanh tăng tốc
decelerate_sound = pygame.mixer.Sound('sounds/decelerate.wav')  # Âm thanh giảm tốc
game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')  # Âm thanh khi game over

# Phát nhạc nền
pygame.mixer.music.play(-1)  # Lặp vô hạn

# Màu nền
gray = (100, 100, 100)
green = (76, 208, 56)
yellow = (255, 232, 0)
red = (200, 0, 0)
white = (255, 255, 255)

# Tạo cửa sổ game
width, height = 800, 700  # Kích thước màn hình lớn hơn
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Tai nạn kinh hoàng')

# Khởi tạo biến
gameover = False
speed = 2
score = 0
highscore = 0
highscore_sound_played = False  # Đánh dấu âm thanh highscore
durability = 100  # % độ bền ban đầu

# Lưu điểm trong file
try:
    with open("highscore.txt", "r") as file:
        highscore = int(file.read())
except FileNotFoundError:
    highscore = 0

# Đường xe chạy
road_width = 500
street_width = 20
street_height = 100

# Làn đường
lane_left = 150
lane_center = 350
lane_right = 550
lanes = [lane_left, lane_center, lane_right]
lane_move_y = 0

# Road và edge
road = (100, 0, road_width, height)
left_edge = (95, 0, street_width, height)
right_edge = (595, 0, street_width, height)


# Vị trí xe ban đầu của người chơi
player_x = lane_center
player_y = 600

# Tải ảnh xe lưu thông
image_names = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = [pygame.image.load('images/' + name) for name in image_names]

# Tải ảnh xe người chơi
player_image_names = ['car.png', 'car1.png', 'car2.png', 'car3.png', 'car4.png']
player_vehicle_images = [pygame.image.load('images/' + name) for name in player_image_names]

# Tải ảnh nổ xe
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

# Đối tượng xe công cộng
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        image_scale = 45 / image.get_rect().width
        new_width = int(image.get_rect().width * image_scale)
        new_height = int(image.get_rect().height * image_scale)
        self.image = pygame.transform.scale(image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

# Đối tượng xe của người chơi
class PlayerVehicle(Vehicle):
    def __init__(self, x, y, image):
        super().__init__(image, x, y)
        self.target_x = x  # Vị trí mục tiêu cho chuyển làn mượt
    #giúp xe chuyển lane mượt hơn
    def move_to_target_lane(self):
        if self.rect.centerx < self.target_x:
            self.rect.centerx += min(5, self.target_x - self.rect.centerx) # Xe sẽ di chuyển sang phải bằng cách tăng self.rect.center

        elif self.rect.centerx > self.target_x:
            self.rect.centerx -= min(5, self.rect.centerx - self.target_x)# Xe sẽ di chuyển sang trái bằng cách giảm self.rect.centerx


# Tạo lại xe người chơi với hình ảnh ngẫu nhiên
def reset_player():
    random_image = random.choice(player_vehicle_images)
    return PlayerVehicle(player_x, player_y, random_image)

# Sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# Tạo xe người chơi ban đầu
player = reset_player()
player_group.add(player)

# Cài đặt khung hình trên giây
clock = pygame.time.Clock()
fps = 120

# Vòng lặp xử lý game
running = True
while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_LEFT and player.target_x > lane_left:
                player.target_x -= 200  # Chuyển làn sang trái
            if event.key == K_RIGHT and player.target_x < lane_right:
                player.target_x += 200  # Chuyển làn sang phải
            if event.key == K_UP and durability == 100:
                speed += 1  # Tăng tốc khi giữ phím lên
                pygame.mixer.Sound.play(accelerate_sound)  # Phát âm thanh tăng tốc
            if event.key == K_DOWN and speed > 3 and durability == 100:
                speed -= 1  # Giảm tốc khi giữ phím xuống
                pygame.mixer.Sound.play(decelerate_sound)  # Phát âm thanh giảm tốc

    # Di chuyển xe người chơi đến làn mục tiêu
    player.move_to_target_lane()

    # Kiểm tra va chạm
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        if durability == 100:
            durability = 50
        elif durability == 50:
            durability = 20
        elif durability == 20:
            durability = 0
        pygame.mixer.Sound.play(crash_sound)
        if durability == 0:  # Kiểm tra % độ bền
            gameover = True
            crash_rect.center = [player.rect.center[0], player.rect.top] # hiển thị ảnh nổ xe trưóc mặt xe người chơi 
            pygame.mixer.music.stop()  # Dừng nhạc nền khi Game Over
            pygame.mixer.Sound.play(game_over_sound)  # Phát âm thanh thua

    # Vẽ địa hình
    screen.fill(green)
    pygame.draw.rect(screen, gray, road)
    pygame.draw.rect(screen, yellow, left_edge)
    pygame.draw.rect(screen, yellow, right_edge)

    # Vẽ làn đường
    lane_move_y += speed * 2
    if lane_move_y >= street_height * 2:
        lane_move_y = 0
    for y in range(-street_height * 2, height, street_height * 2):
        pygame.draw.rect(screen, white, (lane_left + 90, y + lane_move_y, street_width, street_height))
        pygame.draw.rect(screen, white, (lane_center + 90, y + lane_move_y, street_width, street_height))

    # Vẽ xe người chơi
    player_group.draw(screen)

    # Tạo phương tiện lưu thông
    if len(vehicle_group) < 3:
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False
        if add_vehicle:
            lane = random.choice(lanes) #lane ngẫu nhiên khi tạo ngẫu nhiên
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, -50)
            vehicle_group.add(vehicle)

    # Di chuyển phương tiện lưu thông
    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        if vehicle.rect.top >= height:
            vehicle.kill()
            score += 1
            pygame.mixer.Sound.play(point_sound)  # Âm thanh khi tăng điểm

            # Kiểm tra nếu vượt qua highscore và phát âm thanh một lần
            if score > highscore:
                highscore = score
                if not highscore_sound_played:
                    pygame.mixer.Sound.play(highscore_sound)  # Phát âm thanh chỉ một lần
                    highscore_sound_played = True

            # Tăng độ khó khi đạt điểm
            if score > 0 and score % 5 == 0:
                speed += 0.3

    # Vẽ phương tiện giao thông
    vehicle_group.draw(screen)

    # Hiển thị điểm số
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    score_text = font.render(f'Score: {score}', True, white)
    highscore_text = font.render(f'Highscore: {highscore}', True, white)
    durability_text = font.render(f'Durability: {durability}%', True, white)  # Hiển thị % độ bền
    screen.blit(score_text, (20, 20))
    screen.blit(highscore_text, (20, 40))
    screen.blit(durability_text, (20, 60))


    if gameover:
        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, red, (0, 50, width, 100))
        text = font.render('Game Over! Play again? (Y/N)', True, white)
        text_rect = text.get_rect(center=(width / 2, 100))
        screen.blit(text, text_rect)

    # Cập nhật màn hình
    pygame.display.update()

    while gameover:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False
            if event.type == KEYDOWN:
                if event.key == K_y:
                    gameover = False
                    score = 0
                    speed = 2
                    highscore_sound_played = False  # Reset cờ highscore
                    durability = 100
                    vehicle_group.empty()
                    player_group.empty()
                    player = reset_player()
                    player_group.add(player)
                    pygame.mixer.music.play(-1)  # Phát lại nhạc nền
                elif event.key == K_n:
                    gameover = False
                    running = False

# Lưu highscore
with open("highscore.txt", "w") as file:
    file.write(str(highscore))

pygame.quit()