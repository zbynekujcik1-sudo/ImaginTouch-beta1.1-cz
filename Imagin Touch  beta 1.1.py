import cv2
import mediapipe as mp
import numpy as np
import pygame
import time
import os

# Inicializace mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Inicializace pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()

# Cesty k souborům
base_path = os.path.dirname(os.path.abspath(__file__))
background_img = pygame.image.load(os.path.join(base_path, 'assets/background/wild-west-mountains-landscape-ai-bit-pixel-scene-generated-game-background-futuristic-night-arid-western-land-rocks-sand-286584744.webp'))
background_img = pygame.transform.scale(background_img, (width, height))

target_img = pygame.image.load(os.path.join(base_path, 'assets/target/target-aim-flat-icon-darts-game-symbol-logo-vector-20095794.jpg'))
target_img = pygame.transform.scale(target_img, (100, 100))

crosshair_img = pygame.image.load(os.path.join(base_path, 'assets/crosshair/8acc27da8a7d3c5f0a9364f4a968b0dd.png'))
crosshair_img = pygame.transform.scale(crosshair_img, (40, 40))

sound_path = os.path.join(base_path, 'beep.wav')
hit_sound = pygame.mixer.Sound(sound_path)

# Skóre
score = 0
best_score_file = os.path.join(base_path, 'best_score.txt')
best_score = 0
if os.path.exists(best_score_file):
    try:
        with open(best_score_file, 'r') as f:
            best_score = int(f.read())
    except:
        best_score = 0

font = pygame.font.SysFont("Arial", 40)

def draw_text_center(text, y, selected=False):
    color = (255, 0, 0) if selected else (255, 255, 255)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(width // 2, y))
    screen.blit(label, rect)

def main_menu():
    options = ["Módy", "Ukončit hru"]
    selected = 0
    while True:
        screen.blit(background_img, (0, 0))
        draw_text_center("Hlavní menu", height // 6)
        for i, option in enumerate(options):
            draw_text_center(option, height // 3 + i * 60, selected == i)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Módy":
                        return mode_menu()
                    elif options[selected] == "Ukončit hru":
                        pygame.quit()
                        exit()

def mode_menu():
    options = ["Herní mód", "Zpět"]
    selected = 0
    while True:
        screen.blit(background_img, (0, 0))
        draw_text_center("Výběr módu", height // 6)
        for i, option in enumerate(options):
            draw_text_center(option, height // 3 + i * 60, selected == i)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Herní mód":
                        return game_length_menu()
                    elif options[selected] == "Zpět":
                        return main_menu()

def game_length_menu():
    options = ["30 sekund", "60 sekund", "300 sekund", "Zpět"]
    durations = [30, 60, 300]
    selected = 0
    while True:
        screen.blit(background_img, (0, 0))
        draw_text_center("Zvol délku hry", height // 6)
        for i, option in enumerate(options):
            draw_text_center(option, height // 3 + i * 60, selected == i)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Zpět":
                        return mode_menu()
                    else:
                        return durations[selected]

def game_loop(duration_sec):
    global score, best_score
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    start_time = time.time()
    running = True
    score = 0

    target_w, target_h = target_img.get_size()
    target_x = np.random.randint(target_w//2, width - target_w//2)
    target_y = np.random.randint(target_h//2, height - target_h//2)

    while running:
        elapsed = time.time() - start_time
        if elapsed >= duration_sec:
            break

        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)

        screen.blit(background_img, (0, 0))

        small_frame = cv2.resize(frame, (350, 230))
        small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        small_surf = pygame.surfarray.make_surface(small_frame.swapaxes(0, 1))
        screen.blit(small_surf, (10, 10))

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        hand_x, hand_y = None, None
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                lm = handLms.landmark[8]
                hand_x = int(lm.x * width)
                hand_y = int(lm.y * height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False

        screen.blit(target_img, (target_x - target_w//2, target_y - target_h//2))

        if hand_x and hand_y:
            screen.blit(crosshair_img, (hand_x - 20, hand_y - 20))
            dist = np.hypot(hand_x - target_x, hand_y - target_y)
            if dist < max(target_w, target_h) // 2 + 20:
                score += 1
                hit_sound.play()
                target_x = np.random.randint(target_w//2, width - target_w//2)
                target_y = np.random.randint(target_h//2, height - target_h//2)

        screen.blit(font.render(f"Skóre: {score}", True, (255, 255, 255)), (20, 20))
        screen.blit(font.render(f"Čas: {int(duration_sec - elapsed)}s", True, (255, 255, 255)), (width - 180, 20))
        screen.blit(font.render(f"Nejlepší skóre: {best_score}", True, (255, 255, 255)), (20, height - 60))

        pygame.display.flip()

    cap.release()
    cv2.destroyAllWindows()

    if score > best_score:
        best_score = score
        with open(best_score_file, 'w') as f:
            f.write(str(score))

def main():
    while True:
        duration = main_menu()
        game_loop(duration)

        showing = True
        while showing:
            screen.fill((0, 0, 0))
            msg = font.render(f"Konec hry! Skóre: {score}", True, (255, 255, 255))
            msg2 = font.render("Stiskni R pro restart, Q pro ukončení", True, (255, 255, 255))
            screen.blit(msg, (width//3, height//3))
            screen.blit(msg2, (width//3, height//3 + 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        showing = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        return

if __name__ == "__main__":
    main()
