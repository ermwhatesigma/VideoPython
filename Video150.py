import cv2
import time
import sys
from PIL import Image
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import moviepy.editor as mp

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", " ", ".", "-", "■", "□", "▪", "▫", "U", "|", "  ", " "]


frame_size = 150

def play_audio(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

def play_video_pygame(ascii_list, frame_size):
    font = pygame.font.SysFont('Courier', 8)
    window_width, window_height = font.size('A' * frame_size)
    window_height = font.get_linesize() * max(1, len(ascii_list[0].splitlines()))
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("ASCII Video")
    clock = pygame.time.Clock()
    for frame in ascii_list:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((0, 0, 0))
        y_offset = 0
        for line in frame.splitlines():
            text_surface = font.render(line, False, (255, 255, 255))
            screen.blit(text_surface, (0, y_offset))
            y_offset += font.get_linesize()
        pygame.display.flip()
        clock.tick(30)
    pygame.display.set_caption("ASCII Video")

def extract_transform_generate(video_path, start_frame, number_of_frames, frame_size, show_loading=False):
    ascii_list = []
    capture = cv2.VideoCapture(video_path)
    capture.set(1, start_frame)
    frame_count = 1
    ret, image_frame = capture.read()
    if show_loading:
        font = pygame.font.SysFont('Courier', 10)
        screen = pygame.display.set_mode((600, 50))
        pygame.display.set_caption("Loading ASCII Frames")
        screen.fill((0, 0, 0))
        pygame.display.flip()
    while ret and frame_count < number_of_frames:
        ret, image_frame = capture.read()
        if not ret or image_frame is None:
            break
        try:
            image = Image.fromarray(image_frame)
            ascii_characters = pixels_to_ascii(greyscale(resize_image(image, frame_size)))
            pixel_count = len(ascii_characters)
            ascii_image = "\n".join([ascii_characters[i:(i + frame_size)] for i in range(0, pixel_count, frame_size)])
            ascii_list.append(ascii_image)
        except Exception:
            continue
        frame_count += 1
        if show_loading:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.fill((0, 0, 0))
            progress = int(frame_count / number_of_frames * 600)
            pygame.draw.rect(screen, (0, 255, 0), (0, 20, progress, 10))
            pygame.display.flip()
    capture.release()

    return ascii_list

def resize_image(image_frame, frame_size):
    width, height = image_frame.size
    aspect_ratio = height / (width * 2.5)
    new_height = int(aspect_ratio * frame_size)
    resized_image = image_frame.resize((frame_size, new_height))
    return resized_image

def greyscale(image_frame):
    return image_frame.convert("L")

def pixels_to_ascii(image_frame):
    pixels = image_frame.getdata()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters

def preflight_operations(path, frame_size):
    if os.path.exists(path):
        path_to_video = path.strip()
        cap = cv2.VideoCapture(path_to_video)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        video = mp.VideoFileClip(path_to_video)
        path_to_audio = 'audio.mp3'
        video.audio.write_audiofile(path_to_audio)
        ascii_list = extract_transform_generate(path_to_video, 0, total_frames, frame_size, show_loading=True)
        return total_frames, ascii_list
    else:
        return 0, []

def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    
    while True:
        print('==============================================================')
        print('Select option:')
        print('1) Play')
        print('2) Exit')
        print('==============================================================')
        user_input = input("Your option: ").strip()
        if user_input == '1':
            user_input = input("Please enter the video file name (file must be in root!): ")
            total_frames, ascii_list = preflight_operations(user_input, frame_size)
            if total_frames > 0 and len(ascii_list) > 0:
                play_audio('audio.mp3')
                play_video_pygame(ascii_list, frame_size)
            else:
                print('No frames to play.')
        elif user_input == '2':
            exit()
        else:
            print('Unknown input.')

if __name__ == '__main__':
    main()